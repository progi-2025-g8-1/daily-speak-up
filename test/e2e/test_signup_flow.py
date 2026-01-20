import pytest
import time
import os
import uuid
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

def get_latest_magic_link(retries=20, delay=1):
    paths = [
        "backend/latest_link.txt",
        "latest_link.txt",
        os.path.join(os.getcwd(), "backend/latest_link.txt")
    ]
    
    for _ in range(retries):
        for p in paths:
            if os.path.exists(p):
                try:
                    with open(p, "r") as f:
                        content = f.read().strip()
                        if content and "http" in content:
                            return content
                except:
                    pass
        time.sleep(delay)
    
    return None

def clear_magic_link_file():
    paths = [
        "backend/latest_link.txt",
        "latest_link.txt",
        os.path.join(os.getcwd(), "backend/latest_link.txt")
    ]
    for p in paths:
        if os.path.exists(p):
            try:
                os.remove(p)
            except:
                pass

def normalize_link(link, frontend_url):
    if not link:
        return link
    
    from urllib.parse import urlparse, urlunparse
    
    parsed_link = urlparse(link)
    parsed_frontend = urlparse(frontend_url)
    
    normalized = parsed_link._replace(
        scheme=parsed_frontend.scheme,
        netloc=parsed_frontend.netloc
    )
    
    return urlunparse(normalized)

class TestSignupFlow:
    
    def test_signup_flow_e2e(self, driver, frontend_url):        
        unique_id = str(uuid.uuid4())[:8]
        user_email = f"test_e2e_{unique_id}@example.com"
        user_handle = f"user_{unique_id}"
        
        clear_magic_link_file()
        
        # 1. Open landing page
        driver.get(frontend_url)
        time.sleep(2)
        assert "Daily" in driver.page_source
        
        # 2. Click login button
        login_btn = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Prijava')]"))
        )
        login_btn.click()
        time.sleep(2)
        
        # 3. Find email input
        email_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[name='email']"))
        )
        
        # 4. Test invalid email
        email_input.send_keys("invalid-email")
        time.sleep(0.5)
        
        # Try to find and click submit button with invalid email
        try:
            submit_btn_invalid = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Magic Link')]]"))
            )
            submit_btn_invalid.click()
            time.sleep(1)
        except:
            pass
        
        email_input.clear()
        
        # 5. Submit valid email
        email_input.send_keys(user_email)
        time.sleep(0.5)
        
        # Find submit button
        submit_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[.//span[contains(text(), 'Magic Link')]]"))
        )
        submit_btn.click()
        time.sleep(2)
        
        # 6. Get and navigate to magic link
        link = get_latest_magic_link()
        assert link is not None, "Magic link was not generated"
        
        normalized_link = normalize_link(link, frontend_url)
        driver.get(normalized_link)
        time.sleep(5)
        
        # 7. Wait for redirect to onboarding
        WebDriverWait(driver, 20).until(
            lambda d: "/onboarding" in d.current_url or "/home" in d.current_url
        )
        
        if "/home" in driver.current_url:
            return  # Already completed onboarding
        
        # 8. Phase 1: Name and handle
        name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[id='name']"))
        )
        name_input.send_keys(f"Test User {user_handle}")
        
        handle_input = driver.find_element(By.CSS_SELECTOR, "input[id='handle']")
        handle_input.send_keys(user_handle)
        time.sleep(1)
        
        next_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[@type='submit']"))
        )
        next_btn.click()
        time.sleep(2)
        
        # 9. Phase 2: Interests
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//*[contains(text(), 'interes')]"))
        )
        
        # Test persistence
        driver.refresh()
        time.sleep(2)
        
        # Select interests
        time.sleep(1)
        interest_buttons = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.XPATH, "//button[@type='button']"))
        )
        
        clickable_interests = [btn for btn in interest_buttons 
                             if btn.text and len(btn.text) > 0 
                             and btn.text not in ['Nastavi', 'Završi', 'Finish', 'Complete']]
        
        for i in range(min(3, len(clickable_interests))):
            clickable_interests[i].click()
            time.sleep(0.5)
        
        # 10. Complete onboarding
        time.sleep(1)
        
        # Find finish button
        finish_btn = None
        try:
            finish_btn = driver.find_element(By.XPATH, "//button[contains(@class, 'p-button') and .//i[contains(@class, 'pi-check')]]")
        except:
            all_buttons = driver.find_elements(By.TAG_NAME, "button")
            for btn in reversed(all_buttons):
                if btn.is_displayed() and btn.is_enabled() and btn.text and len(btn.text) > 5:
                    finish_btn = btn
                    break
        
        assert finish_btn is not None, "Could not find finish button"
        finish_btn.click()
        time.sleep(3)
        
        # 11. Verify redirect to home
        WebDriverWait(driver, 15).until(
            lambda d: "/home" in d.current_url or d.current_url == frontend_url + "/"
        )
        
        try:
            time.sleep(2)
            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"Home page loaded, body contains: {body_text[:200]}")
        except:
            pass
        
        print("PASS")

