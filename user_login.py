import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


@pytest.fixture
def driver():
    #Setup and teardown fixture for Chrome WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


def register_user(driver, email):
    #Helper function to register a new user on LambdaTest before login
    #Similar code used in user_registration
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=account/register")
    driver.find_element(By.ID, "input-firstname").send_keys("Test")
    driver.find_element(By.ID, "input-lastname").send_keys("User")
    driver.find_element(By.ID, "input-email").send_keys(email)
    driver.find_element(By.ID, "input-telephone").send_keys("1234567890")
    driver.find_element(By.ID, "input-password").send_keys("SecurePassword123!")
    driver.find_element(By.ID, "input-confirm").send_keys("SecurePassword123!")
    driver.find_element(By.XPATH, "//label[@for='input-agree']").click()
    driver.find_element(By.XPATH, "//input[@value='Continue']").click()

    # Wait until registration is successful
    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/success")
    )


def test_successful_user_login(driver):
    #Test Scenario 1: Successful User Login with Valid Credentials
    unique_email = f"testuser_{int(time.time())}@example.com"
    register_user(driver, unique_email)

    #Clear cookies to log out the freshly registered session so we can test login
    driver.delete_all_cookies()

    #get user login url
    login_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    driver.get(login_url)

    #Enter registered email and correct password
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-email"))
    )
    email_field.send_keys(unique_email)
    driver.find_element(By.ID, "input-password").send_keys("SecurePassword123!")

    #Click Login to submit form
    driver.find_element(By.XPATH, "//input[@value='Login']").click()

    #Verify redirect to MyAccount dashboard
    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/account")
    )
    assert "route=account/account" in driver.current_url
    print("[PASS] Scenario 1: User Login Successful.")


def test_unsuccessful_login_empty_fields(driver):
    #Test Scenario 2: Unsuccessful login due to Missing Mandatory Fields
    #get user login url
    login_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    driver.get(login_url)

    #Ensure login page is fully loaded before clicking
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@value='Login']"))
    )

    #Leave fields empty and click Login
    driver.find_element(By.XPATH, "//input[@value='Login']").click()

    #Verify warning alert appears and system remains on login page
    error_banner = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".alert-danger"))
    )
    assert "Warning" in error_banner.text
    assert "route=account/login" in driver.current_url
    print("[PASS] Scenario 2: Unsuccessful login handled correctly.")


def test_login_with_password_reset(driver):
    #Test Scenario 3: Password Reset request and subsequent successful login
    unique_email = f"testuser_reset_{int(time.time())}@example.com"
    register_user(driver, unique_email)

    #Clear cookies to start clean on the login page
    driver.delete_all_cookies()

    #get user login url
    login_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    driver.get(login_url)

    #Click Forgotten Password option and verify redirect
    forgot_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'route=account/forgotten')]"))
    )
    forgot_link.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/forgotten")
    )

    #Enter registered email and submit request
    email_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-email"))
    )
    email_field.send_keys(unique_email)
    driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()

    #Verify confirmation message redirecting to login page
    success_banner = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSSSelector, ".alert-success"))
    )
    assert "confirmation link has been sent" in success_banner.text

    #Complete login verification using updated credentials
    driver.get(login_url)
    email_field_login = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "input-email"))
    )
    email_field_login.send_keys(unique_email)
    driver.find_element(By.ID, "input-password").send_keys("SecurePassword123!")
    driver.find_element(By.XPATH, "//input[@value='Login']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/account")
    )
    assert "route=account/account" in driver.current_url
    print("[PASS] Scenario 3: Password reset request flow and subsequent login verified.")