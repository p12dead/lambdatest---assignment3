import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import random


@pytest.fixture
def driver():
    #Setup and teardown fixture for Chrome WebDriver
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


def test_successful_user_registration(driver):
    #Test Scenario 1: Successful User Registration with Valid Data
    #get user registration url
    register_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/register"
    driver.get(register_url)

    #Generate a unique email using a random number to avoid duplicate email errors
    unique_email = f"test_user_{random.randint(10000, 99999)}@example.com"

    #Fill in valid registration details
    driver.find_element(By.ID, "input-firstname").send_keys("Prithika")
    driver.find_element(By.ID, "input-lastname").send_keys("Sekar")
    driver.find_element(By.ID, "input-email").send_keys(unique_email)
    driver.find_element(By.ID, "input-telephone").send_keys("0412345678")
    driver.find_element(By.ID, "input-password").send_keys("SecurePass123!")
    driver.find_element(By.ID, "input-confirm").send_keys("SecurePass123!")

    #Select Newsletter Subscribe option
    newsletter_radio = driver.find_element(By.XPATH, "//input[@name='newsletter' and @value='1']")
    if not newsletter_radio.is_selected():
        newsletter_radio.click()

    #Click on Privacy Policy checkbox
    privacy_checkbox = driver.find_element(By.XPATH, "//input[@name='agree']")
    if not privacy_checkbox.is_selected():
        privacy_checkbox.click()

    #Click on Continue to submit registration form
    continue_btn = driver.find_element(By.XPATH, "//input[@value='Continue']")
    continue_btn.click()

    #Acknowledge successful registration (Redirects to successful account creation page)
    WebDriverWait(driver, 10).until(
        EC.url_contains("route=account/success")
    )

    success_heading = driver.find_element(By.TAG_NAME, "h1").text
    assert "Your Account Has Been Created!" in success_heading
    print("[PASS] Scenario 1: User registered successfully.")


def test_registration_missing_mandatory_fields(driver):
    #Test Scenario 2: Unsuccessful Registration due to Missing Mandatory Fields
    #get user registration url
    register_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/register"
    driver.get(register_url)

    #Leave all mandatory fields blank and privacy policy unticked
    #Click on Continue to submit registration form
    continue_btn = driver.find_element(By.XPATH, "//input[@value='Continue']")
    continue_btn.click()

    #Verify that warning errors appear
    error_locator = (By.CSS_SELECTOR, ".text-danger, .alert-danger")
    error_elements = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located(error_locator)
    )

    assert len(error_elements) > 0, "Validation errors should be displayed for mandatory fields."

    #Confirm user registration was unsuccessful and system remains on registration page
    assert "route=account/register" in driver.current_url
    print("[PASS] Scenario 2: Missing mandatory fields correctly blocked registration.")


def test_registration_invalid_email(driver):
    #Test Scenario 3: Unsuccessful Registration due to Invalid Email Address
    #get user registration url
    register_url = "https://ecommerce-playground.lambdatest.io/index.php?route=account/register"
    driver.get(register_url)

    #Enter valid names, invalid email format, valid telephone/passwords, and check privacy policy
    driver.find_element(By.ID, "input-firstname").send_keys("Prithika")
    driver.find_element(By.ID, "input-lastname").send_keys("Sekar")
    driver.find_element(By.ID, "input-email").send_keys("invalid-email-format")  # Missing '@' and domain
    driver.find_element(By.ID, "input-telephone").send_keys("0412345678")
    driver.find_element(By.ID, "input-password").send_keys("SecurePass123!")
    driver.find_element(By.ID, "input-confirm").send_keys("SecurePass123!")

    privacy_checkbox = driver.find_element(By.XPATH, "//input[@name='agree']")
    if not privacy_checkbox.is_selected():
        privacy_checkbox.click()

    #Click on Continue to submit registration form
    continue_btn = driver.find_element(By.XPATH, "//input[@value='Continue']")
    continue_btn.click()

    #Confirm user registration was unsuccessful and system remains on registration page
    time.sleep(2)
    assert "route=account/register" in driver.current_url
    print("[PASS] Scenario 3: Invalid email format correctly blocked registration.")