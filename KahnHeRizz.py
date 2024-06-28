import time
import random
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException

def random_sleep(min_time, max_time):
    time.sleep(random.uniform(min_time, max_time))

def check_website_update(url, button_xpath, base_case_text, check_frequency=15):
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-extensions')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-browser-side-navigation')
    options.add_argument('--disable-gpu')
    
    # Randomize user agent
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.1 Safari/605.1.15",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:92.0) Gecko/20100101 Firefox/92.0",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36 OPR/80.0.4170.72"
    ]
    options.add_argument(f"user-agent={random.choice(user_agents)}")
    
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """
    })
    
    def wait_and_click(xpath, timeout=10):
        try:
            element = WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((By.XPATH, xpath)))
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            random_sleep(1, 10)
            
            # Add some randomness to the click location
            action = ActionChains(driver)
            action.move_to_element_with_offset(element, random.randint(1, 5), random.randint(1, 5))
            action.click()
            action.perform()
            return True
        except (TimeoutException, WebDriverException):
            print(f"Failed to click element with XPath: {xpath}")
            return False

    def simulate_human_behavior():
        # Simulate scrolling
        for _ in range(random.randint(2, 5)):
            driver.execute_script(f"window.scrollTo(0, {random.randint(10, 100)});")
            random_sleep(0.5, 1.5)
        
        # Simulate mouse movements
        action = ActionChains(driver)
        for _ in range(random.randint(3, 7)):
            action.move_by_offset(random.randint(-100, 100), random.randint(-100, 100))
            action.perform()
            random_sleep(0.2, 0.7)

    try:
        while True:
            try:
                driver.get(url)
                random_sleep(5, 8)  # Increased delay after page load
                
                # simulate_human_behavior()
                
                # Close cookie banner if present
                wait_and_click("//button[@class='onetrust-close-btn-handler onetrust-close-btn-ui banner-close-button ot-close-icon']")
                
                if wait_and_click(button_xpath):
                    try:
                        # Wait for the page to load after clicking the button
                        random_sleep(30, 45)
                        
                        simulate_human_behavior()
                        
                        # Find all elements with the `no-availability` class
                        no_tickets_elements = WebDriverWait(driver, 30).until(
                            EC.presence_of_all_elements_located((By.CLASS_NAME, "no-availability"))
                        )
                        # print all of the no_ticket_elements:
                        for no_tickets_element in no_tickets_elements:
                            print(f"No tickets available: {no_tickets_element.text}")
                        else:
                            print(f"No tickets available. Checking again in {check_frequency} minutes.")
                    
                        update_detected = False
                        for no_tickets_element in no_tickets_elements:
                            current_text = no_tickets_element.text.strip()
                            if current_text != base_case_text:
                                print(f"Update detected! New text: {current_text}")
                                update_detected = True
                                break  # Break the loop if an update is detected
                        
                        if not update_detected:
                            print(f"No update detected. Text is still: '{base_case_text}'. Checking again in {check_frequency} minutes.")
                    
                    except (TimeoutException, NoSuchElementException) as e:
                        print(f"Error finding 'no-availability' class: {str(e)}")
                        print("The website structure might have changed, tickets might be available, or the page didn't load completely.")
                else:
                    print("Failed to click the 'Buy Tickets' button. Retrying in the next iteration.")
            
            except WebDriverException as e:
                print(f"An error occurred: {str(e)}")
                print("Retrying in the next iteration.")
            
            random_sleep(check_frequency * 60, check_frequency * 60 + 30)
    
    finally:
        driver.quit()

if __name__ == "__main__":
    url = "https://www.mlb.com/redsox/tickets/concerts/noah-kahan"
    button_xpath = "//div[@data-slug='bos-button-tickets-concerts-noah-kahan-buy-tickets-7-18']//a[@class='p-button__link']"
    base_case_text = "No tickets were found matching your filter criteria"
    check_frequency = 15  # minutes
    
    check_website_update(url, button_xpath, base_case_text, check_frequency)
