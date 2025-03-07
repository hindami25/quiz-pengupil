from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

# Konfigurasi WebDriver (gunakan headless untuk testing otomatis)
options = webdriver.FirefoxOptions()
#options.add_argument('--headless')  # Jalankan tanpa GUI
browser = webdriver.Firefox(options=options)

# Base URL aplikasi
BASE_URL = "http://localhost/quiz-pengupil/"

# Helper function untuk print hasil test case
def print_result(test_id, description, result):
    status = "✅ PASSED" if result else "❌ FAILED"
    print(f"{test_id}: {description} -> {status}")

# Fungsi untuk logout
def logout():
    """Logout dari sistem setelah pengujian login atau registrasi berhasil"""
    try:
        browser.get(BASE_URL + "/index.php")  # Buka halaman utama setelah login
        time.sleep(2)
        logout_button = browser.find_element(By.LINK_TEXT, "Logout")
        logout_button.click()
        time.sleep(2)
        print("[INFO] Logout berhasil.")
    except:
        print("[WARNING] Logout gagal atau tidak diperlukan.")

# Fungsi untuk registrasi
def register(name, email, username, password, repassword, expected_error=None):
    browser.get(BASE_URL + "/register.php")
    time.sleep(2)
    browser.find_element(By.NAME, "name").send_keys(name)
    browser.find_element(By.NAME, "email").send_keys(email)
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "repassword").send_keys(repassword)
    browser.find_element(By.NAME, "submit").click()
    time.sleep(2)

    if expected_error:
        result = expected_error in browser.page_source
    else:
        wait = WebDriverWait(browser, 3)  # Tunggu hingga 3 detik
        result = wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Anda berhasil login ke sistem.')]"))).text
        logout()  # Logout setelah registrasi berhasil
    return result

# **TEST CASES REGISTRASI**
print_result("TC-1.1", "Registrasi dengan data valid", register("Test User", "testuser@example.com", "testuser123", "TestPassword123!", "TestPassword123!"))
print_result("TC-1.2", "Registrasi dengan username yang sudah ada", register("Test User", "testuser2@example.com", "testuser123", "TestPassword123!", "TestPassword123!", "Username sudah terdaftar !!"))
print_result("TC-1.3", "Registrasi dengan email yang sudah ada", register("Test User", "testuser@example.com", "testuser456", "TestPassword123!", "TestPassword123!", "Username sudah terdaftar !!"))
print_result("TC-1.4", "Registrasi dengan password dan re-password tidak cocok", register("Test User", "testuser3@example.com", "testuser789", "TestPassword123!", "WrongPassword!", "Password tidak sama !!"))
print_result("TC-1.5", "Registrasi dengan username kosong", register("Test User", "testuser4@example.com", "", "TestPassword123!", "TestPassword123!", "Data tidak boleh kosong !!"))
print_result("TC-1.6", "Registrasi dengan password kosong", register("Test User", "testuser5@example.com", "testuser555", "", "", "Data tidak boleh kosong !!"))

# Tutup browser setelah pengujian
browser.quit()
