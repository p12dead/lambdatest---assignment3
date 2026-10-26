import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


@pytest.fixture
def driver():
    """Setup and teardown fixture for Chrome WebDriver instance."""
    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")  # Uncomment if running headlessly in terminal
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


def test_successful_user_login(driver):
    """Test Scenario 1: Successful User Login with Valid Credentials"""
    login_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    driver.get(login_url)

    # Step 2 & 3: Enter registered email and correct password
    driver.find_element(By.ID, "input-email").send_keys("testuser_2026@example.com")
    driver.find_element(By.ID, "input-password").send_keys("SecurePassword123!")

    # Step 4: Click Login to submit form
    driver.find_element(By.XPATH, "//input[@value='Login']").click()

    # Step 5: Verify redirect to MyAccount dashboard
    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/account")
    )
    assert "route=account/account" in driver.current_url
    print("[PASS] Scenario 1: User Login Successful.")


def test_unsuccessful_login_empty_fields(driver):
    """Test Scenario 2: Unsuccessful login due to empty mandatory input fields"""
    login_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    driver.get(login_url)

    # Step 2 & 3: Leave fields empty and click Login
    driver.find_element(By.XPATH, "//input[@value='Login']").click()

    # Step 4 & 5: Verify warning alert appears and system remains on login page
    error_banner = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSSSelector, ".alert-danger"))
    )
    assert "Warning" in error_banner.text
    assert "route=account/login" in driver.current_url
    print("[PASS] Scenario 2: Unsuccessful login handled correctly.")


def test_login_with_password_reset(driver):
    """Test Scenario 3: Password Reset request and subsequent login"""
    login_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/login"
    driver.get(login_url)

    # Step 2 & 3: Click Forgotten Password option and verify redirect
    forgot_link = driver.find_element(By.XPATH, "//a[contains(@href, 'route=account/forgotten')]")
    forgot_link.click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/forgotten")
    )

    # Step 4 & 5: Enter registered email and submit request
    driver.find_element(By.ID, "input-email").send_keys("testuser_2026@example.com")
    driver.find_element(By.XPATH, "//button[contains(text(), 'Continue')]").click()

    # Step 6: Verify confirmation message redirecting to login page
    success_banner = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSSSelector, ".alert-success"))
    )
    assert "confirmation link has been sent" in success_banner.text

    # Step 7 - 10: Complete login verification using updated credentials
    driver.get(login_url)
    driver.find_element(By.ID, "input-email").send_keys("testuser_2026@example.com")
    driver.find_element(By.ID, "input-password").send_keys("SecurePassword123!")
    driver.find_element(By.XPATH, "//input[@value='Login']").click()

    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/account")
    )
    assert "route=account/account" in driver.current_url
    print("[PASS] Scenario 3: Password reset request flow and subsequent login verified.")