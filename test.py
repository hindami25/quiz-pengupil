import os
import logging
import requests
import time
import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Install ChromeDriver yang sesuai dengan versi Google Chrome
chromedriver_autoinstaller.install()

# Konfigurasi Logging
LOG_DIR = "test-results"
os.makedirs(LOG_DIR, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "test_log.txt"),
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

# Fungsi untuk cek apakah server sudah aktif
def wait_for_server(url, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(url)
            if response.status_code == 200:
                print("✅ Server is up and running!")
                return True
        except requests.exceptions.ConnectionError:
            print("⏳ Waiting for server to start...")
        time.sleep(5)
    raise RuntimeError("❌ Server failed to start!")

# Cek server sebelum Selenium berjalan
BASE_URL = "http://127.0.0.1/quiz-pengupil/"
wait_for_server(BASE_URL)

# Set up WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")  # Menjalankan Chrome tanpa GUI
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

# List untuk menyimpan hasil test
test_results = []

def log_result(test_name, status, message=""):
    result = f"{test_name}: {status} - {message}"
    print(result)
    logging.info(result)

def run_test(test_function):
    """
    Helper function untuk menjalankan setiap test case tanpa menghentikan eksekusi.
    Jika ada error, akan dicatat dan test berikutnya tetap dijalankan.
    """
    try:
        test_function()
        test_results.append((test_function.__name__, "✅ PASSED", ""))
    except AssertionError as e:
        test_results.append((test_function.__name__, "❌ FAILED", str(e)))
    except Exception as e:
        test_results.append((test_function.__name__, "⚠️ ERROR", str(e)))

def test_login_valid():
    driver.get(BASE_URL + "login.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("testuser123")
    driver.find_element(By.ID, "InputPassword").send_keys("TestPassword123!")
    driver.find_element(By.NAME, "submit").click()

    time.sleep(2)
    assert "index.php" in driver.current_url, "Error: Login gagal, tidak dialihkan ke index.php."

def test_login_invalid():
    driver.get(BASE_URL + "login.php")
    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("wronguser")
    driver.find_element(By.ID, "InputPassword").send_keys("WrongPass")
    driver.find_element(By.NAME, "submit").click()

    time.sleep(2)
    assert "Register User Gagal" in driver.page_source, "Error: Pesan gagal login tidak muncul."

def test_login_empty():
    driver.get(BASE_URL + "login.php")
    driver.find_element(By.NAME, "submit").click()

    time.sleep(2)
    assert "Data tidak boleh kosong" in driver.page_source, "Error: Input kosong tidak ditangani dengan benar."

def test_sql_injection_login():
    driver.get(BASE_URL + "login.php")

    WebDriverWait(driver, 5).until(EC.presence_of_element_located((By.ID, "username"))).send_keys("' OR '1'='1")
    driver.find_element(By.ID, "InputPassword").send_keys("' OR '1'='1")
    driver.find_element(By.NAME, "submit").click()

    time.sleep(2)
    assert "index.php" not in driver.current_url, "Error: SQL Injection berhasil, sistem tidak aman!"

# Jalankan semua test case menggunakan run_test()
test_cases = [
    test_login_valid,
    test_login_invalid,
    test_login_empty,
    test_sql_injection_login
]

for test in test_cases:
    run_test(test)

# Cetak hasil semua test dengan format rapi
print("\n=== TEST RESULTS ===")
print(f"{'Test Case':<30} {'Status':<10} {'Message'}")
print("="*80)
for name, status, message in test_results:
    print(f"{name:<30} {status:<10} {message}")

# Tutup browser
driver.quit()
