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
        logout_button = browser.find_element(By.NAME, "logout")
        logout_button.click()
        time.sleep(2)
        print("[INFO] Logout berhasil.")
    except:
        print("[WARNING] Logout gagal atau tidak diperlukan.")

# Fungsi untuk login
def login(username, password, expected_error=None):
    browser.get(BASE_URL + "/login.php")
    time.sleep(2)
    browser.find_element(By.NAME, "username").send_keys(username)
    browser.find_element(By.NAME, "password").send_keys(password)
    browser.find_element(By.NAME, "submit").click()
    time.sleep(2)

    if expected_error:
        result = expected_error in browser.page_source
    else:
        wait = WebDriverWait(browser, 3)  # Tunggu hingga 3 detik
        result = wait.until(EC.presence_of_element_located((By.XPATH, "//p[contains(text(), 'Anda berhasil login ke sistem.')]"))).text
        logout()  # Logout setelah login berhasil
    return result

# **TEST CASES LOGIN**
print_result("TC-2.1", "Login dengan data valid", login("testuser123", "TestPassword123!"))
print_result("TC-2.2", "Login dengan username yang tidak terdaftar", login("unknownuser", "SomePassword123!", "Register User Gagal !!"))
print_result("TC-2.3", "Login dengan password yang salah", login("testuser123", "WrongPassword!", "Register User Gagal !!"))
print_result("TC-2.4", "Login dengan username kosong", login("", "TestPassword123!", "Data tidak boleh kosong !!"))
print_result("TC-2.5", "Login dengan password kosong", login("testuser123", "", "Data tidak boleh kosong !!"))
print_result("TC-2.6", "Login dengan username dan password kosong", login("", "", "Data tidak boleh kosong !!"))

# **TEST CASE SQL Injection**
print_result("TC-2.7", "Login dengan SQL Injection", login("' OR 1=1 --", "random", "Register User Gagal !!"))

# Tutup browser setelah pengujian
browser.quit()
