import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
import time


@pytest.fixture
def driver():
    #Setup and teardown fixture for Chrome WebDriver instance\
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.maximize_window()
    yield driver
    driver.quit()


def add_product_to_cart(driver):
    #Helper function to add a product to the cart before testing checkout
    product_url = "https://ecommerce-playground.lambdatest.io/index.php?route=product/product&product_id=30"
    driver.get(product_url)
    add_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@id='button-cart']"))
    )
    add_btn.click()
    time.sleep(2)


def test_successful_checkout(driver):
    #Test Scenario 1: Successful Checkout Flow with Valid Details"""
    #Add product and navigate to cart
    add_product_to_cart(driver)
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=checkout/cart")

    #Click on checkout to proceed to Checkout page
    checkout_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@class, 'btn-primary') and contains(text(), 'Checkout')]"))
    )
    checkout_btn.click()

    #Fill in Billing Address details & Telephone
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "input-payment-firstname")))

    driver.find_element(By.ID, "input-payment-firstname").clear()
    driver.find_element(By.ID, "input-payment-firstname").send_keys("user_login")
    driver.find_element(By.ID, "input-payment-lastname").clear()
    driver.find_element(By.ID, "input-payment-lastname").send_keys("Tester")
    driver.find_element(By.ID, "input-payment-telephone").clear()
    driver.find_element(By.ID, "input-payment-telephone").send_keys("0412345678")

    driver.find_element(By.ID, "input-payment-address-1").clear()
    driver.find_element(By.ID, "input-payment-address-1").send_keys("123 Test Street")
    driver.find_element(By.ID, "input-payment-city").clear()
    driver.find_element(By.ID, "input-payment-city").send_keys("Sydney")
    driver.find_element(By.ID, "input-payment-postcode").clear()
    driver.find_element(By.ID, "input-payment-postcode").send_keys("2000")

    #Select Country and Region
    country_select = Select(driver.find_element(By.ID, "input-payment-country"))
    country_select.select_by_visible_text("Australia")
    time.sleep(1)
    zone_select = Select(driver.find_element(By.ID, "input-payment-zone"))
    zone_select.select_by_visible_text("New South Wales")

    #Click Terms & Conditions checkbox
    terms_checkbox = driver.find_element(By.XPATH, "//input[@name='agree']")
    if not terms_checkbox.is_selected():
        terms_checkbox.click()

    #Click continue / confirm order
    confirm_btn = driver.find_element(By.ID, "button-save")
    confirm_btn.click()

    #Verify successful checkout message displayed
    WebDriverWait(driver, 10).until(
        EC.url_contains("route=checkout/success")
    )
    success_heading = driver.find_element(By.TAG_NAME, "h1").text
    assert "Your Order Has Been Placed!" in success_heading or "Success" in success_heading
    print("[PASS] Scenario 1: Successful Checkout verified.")


def test_unsuccessful_checkout_missing_fields(driver):
    #Test Scenario 2: Unsuccessful Checkout due to Missing Mandatory Fields"""
    #Add product and navigate to checkout page
    add_product_to_cart(driver)
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=checkout/checkout")

    #Leave mandatory input fields blank
    #Check terms and conditions without filling mandatory details
    terms_checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//input[@name='agree']"))
    )
    if not terms_checkbox.is_selected():
        terms_checkbox.click()

    #Click continue / save
    continue_btn = driver.find_element(By.ID, "button-save")
    continue_btn.click()

    #Verify warning error appears and system remains on checkout page
    error_element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSSSelector, ".text-danger, .alert-danger"))
    )
    assert error_element.is_displayed()
    assert "checkout" in driver.current_url
    print("[PASS] Scenario 2: Missing mandatory fields correctly blocked checkout.")


def test_unsuccessful_checkout_empty_cart(driver):
    #Test Scenario 3: Unsuccessful Checkout due to Empty Shopping Cart
    #Navigate to cart and ensure it is empty
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=checkout/cart")

    remove_buttons = driver.find_elements(By.XPATH, "//button[contains(@class,'btn-danger')]")
    for btn in remove_buttons:
        btn.click()
        time.sleep(1)

    #Attempt to click checkout or navigate to checkout
    driver.get("https://ecommerce-playground.lambdatest.io/index.php?route=checkout/checkout")

    #erify redirection back to cart / homepage with empty notice
    time.sleep(2)
    assert "route=checkout/cart" in driver.current_url or "route=common/home" in driver.current_url
    print("[PASS] Scenario 3: Empty shopping cart correctly blocked checkout.")