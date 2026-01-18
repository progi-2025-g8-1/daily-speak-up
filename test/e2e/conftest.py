import pytest
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

@pytest.fixture(scope="session")
def frontend_url():
    return os.getenv("FRONTEND_URL", "http://localhost:5173")

@pytest.fixture(scope="function")
def driver():
    options = Options()
    # options.add_argument("--headless")  # Comment out for debugging
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--start-maximized")
    options.add_argument("--disable-web-security")
    options.add_argument("--disable-site-isolation-trials")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-gpu")
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.implicitly_wait(5)
        yield driver
    finally:
        if driver:
            driver.quit()
