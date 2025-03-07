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
BASE_URL = "http://127.0.0.1:8000/"
wait_for_server(BASE_URL)

# Set up WebDriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=chrome_options)
driver.implicitly_wait(10)

def run_test(test_function):
    try:
        test_function()
        print(f"✅ {test_function.__name__} PASSED")
    except AssertionError as e:
        print(f"❌ {test_function.__name__} FAILED: {str(e)}")
    except Exception as e:
        print(f"⚠️ {test_function.__name__} ERROR: {str(e)}")

def test_register_valid():
    driver.get(BASE_URL + "register.php")
    driver.find_element(By.ID, "username").send_keys("user123")
    driver.find_element(By.ID, "name").send_keys("User Test")
    driver.find_element(By.ID, "InputEmail").send_keys("user@test.com")
    driver.find_element(By.ID, "InputPassword").send_keys("Password123!")
    driver.find_element(By.ID, "InputRePassword").send_keys("Password123!")
    driver.find_element(By.NAME, "submit").click()
    assert "index.php" in driver.current_url, "Error: Registrasi gagal."

def test_register_existing_user():
    driver.get(BASE_URL + "register.php")
    driver.find_element(By.ID, "username").send_keys("existingUser")
    driver.find_element(By.NAME, "submit").click()
    assert "Username sudah terdaftar" in driver.page_source, "Error: Username seharusnya sudah ada."

def test_register_existing_email():
    driver.get(BASE_URL + "register.php")
    driver.find_element(By.ID, "InputEmail").send_keys("user@test.com")
    driver.find_element(By.NAME, "submit").click()
    assert "Email sudah terdaftar" in driver.page_source, "Error: Email seharusnya sudah ada."

def test_register_password_mismatch():
    driver.get(BASE_URL + "register.php")
    driver.find_element(By.ID, "InputPassword").send_keys("Password123!")
    driver.find_element(By.ID, "InputRePassword").send_keys("WrongPass123!")
    driver.find_element(By.NAME, "submit").click()
    assert "Password tidak sama" in driver.page_source, "Error: Password mismatch tidak terdeteksi."

def test_register_empty_fields():
    driver.get(BASE_URL + "register.php")
    driver.find_element(By.NAME, "submit").click()
    assert "Data tidak boleh kosong" in driver.page_source, "Error: Form kosong tidak ditangani."

def test_login_valid():
    driver.get(BASE_URL + "login.php")
    driver.find_element(By.ID, "username").send_keys("validUser")
    driver.find_element(By.ID, "InputPassword").send_keys("ValidPass123!")
    driver.find_element(By.NAME, "submit").click()
    assert "index.php" in driver.current_url, "Error: Login gagal."

def test_login_invalid_user():
    driver.get(BASE_URL + "login.php")
    driver.find_element(By.ID, "username").send_keys("unknownUser")
    driver.find_element(By.ID, "InputPassword").send_keys("ValidPass123!")
    driver.find_element(By.NAME, "submit").click()
    assert "Register User Gagal" in driver.page_source, "Error: Username tidak valid tidak ditangani."

def test_login_wrong_password():
    driver.get(BASE_URL + "login.php")
    driver.find_element(By.ID, "username").send_keys("validUser")
    driver.find_element(By.ID, "InputPassword").send_keys("WrongPass123!")
    driver.find_element(By.NAME, "submit").click()
    assert "Register User Gagal" in driver.page_source, "Error: Password salah tidak ditangani."

def test_login_sql_injection():
    driver.get(BASE_URL + "login.php")
    driver.find_element(By.ID, "username").send_keys("' OR 1=1 --")
    driver.find_element(By.ID, "InputPassword").send_keys("anything")
    driver.find_element(By.NAME, "submit").click()
    assert "Register User Gagal" in driver.page_source, "Error: SQL Injection berhasil!"

# Daftar test case
TEST_CASES = [
    #test_register_valid,
    #test_register_existing_user,
    #test_register_existing_email,
    #test_register_password_mismatch,
    #test_register_empty_fields,
    test_login_valid,
    test_login_invalid_user,
    test_login_wrong_password,
    test_login_sql_injection,
]

# Jalankan semua test case
for test in TEST_CASES:
    run_test(test)

driver.quit()
