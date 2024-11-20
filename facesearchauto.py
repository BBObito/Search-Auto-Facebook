from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pickle
import re
import os
import sys
import threading
from datetime import datetime
from threading import Lock
from PIL import Image
import keyboard
import matplotlib.pyplot as plt
import random

# Initialize a global lock object
lock = Lock()
set_current_urls = set()

#Initiate current datetime and setup folder for saving
date_folder = datetime.now().strftime('%Y-%m-%d')
os.makedirs(f'results/{date_folder}', exist_ok= True)
# with open(f'results/{date_folder}/newphishingpage.txt', 'w') as file:
#     file.write('')
# file.close()

#define chrome driver settings and facebook cookie
# chrome_driver_path = "D:/chromedriver-win64/chromedriver.exe"  # Replace with your actual chrome driver path
cookies_file_path = "facebook_cookies.pkl"


def save_cookies(driver: webdriver.Chrome, file_path: str) -> None:
    """Save cookies to a file."""
    cookies = driver.get_cookies()
    with open(file_path, 'wb') as file:
        pickle.dump(cookies, file)

def load_cookies(driver: webdriver.Chrome, file_path: str) -> None:
    """Load cookies from a file."""
    try:
        with open(file_path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        print(f"No cookies found at {file_path}")

def scroll_to_load_all_results(driver: webdriver.Chrome) -> None:
    """Scroll down the page to load all results."""
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def click_see_more_buttons(driver: webdriver.Chrome) -> None:
    """Click on 'See More' buttons to reveal additional content."""
    while True:
        try:
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'See More') or contains(text(), 'More')]"))
            )
            see_more_button.click()
            time.sleep(2)
        except Exception as e:
            print("No more 'See More' buttons found or error occurred:", e)
            break

def filter_pages(driver: webdriver.Chrome) -> bool:
    """Apply the 'Pages' filter to the search results."""

    try:
        pages_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Posts')]"))
        )
        pages_filter.click()
        
        recent_posts = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@aria-label="Recent Posts" and @type="checkbox" and @role="switch" and @aria-checked="false"]'))
        )
        recent_posts.click()

        scroll_to_load_all_results(driver)
        click_see_more_buttons(driver)
        
        return True
    except Exception as e:
        print("Error filtering pages or applying filter:", e)
        return False

def save_url_to_file(path: str, url: str, mode: str) -> None:
    """ 
        Save a URL to a file in a thread-safe way.
    """
    try:
        with open(path, mode, encoding='utf-8') as f:
            f.write(url + '\n')
    except Exception as e:
        print(e)

def read_url_from_file(file_path: str) -> list[str]:
    """Read URLs from a file and return them as a list."""
    urlist = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            urlist = [line.strip() for line in file]
    except Exception as e:
        print(e)
    return urlist

def process_search_results(driver: webdriver.Chrome) -> None:
    """Process the search results and take screenshots of pages."""
    # save driver to html file
    # with open(f'results/{date_folder}/search_results.html', 'w', encoding='utf-8') as f:
    #     f.write(driver.page_source)
    
    # time.sleep(5000)
        
    articles = driver.find_elements(By.XPATH, '//span/div/span[1]/span/a')
    
    file_path = f'results/{date_folder}/newphishingpage.txt'
    with open(file_path, 'a', encoding='utf-8') as file:
        for i in range(len(articles)):
            article = articles[i]
            try:
                page_url = article.get_attribute("href")
                # Ghi URL vào file
                file.write(page_url + '\n')
            except Exception as e:
                print(f"Error processing article: {e}")
    articles_1 = driver.find_elements(By.XPATH, '//span/div/span[2]/span/a')
    
    file_path = f'results/{date_folder}/newphishingpage.txt'
    with open(file_path, 'a', encoding='utf-8') as file:
        for i in range(len(articles_1)):
            article = articles_1[i]
            try:
                page_url = article.get_attribute("href")
                # Ghi URL vào file
                file.write(page_url + '\n')
            except Exception as e:
                print(f"Error processing article: {e}")

    # for i, article in enumerate(articles):
    #     try:
    #         xpaths = [
    #             ".//div/span[1]/span/span/a[@href and @role='link']",
    #             ".//div/span[2]/span/span/a[@href and @role='link']",
    #             ".//div/span[3]/span/span/a[@href and @role='link']",
    #         ]

    #         for xpath in xpaths:
    #             try:
    #                 link = article.find_element(By.XPATH, xpath)
    #                 page_url = link.get_attribute("href")
    #                 with open(f'results/{date_folder}/newphishingpage.txt', 'a', encoding='utf-8') as file:
    #                     file.write(page_url + '\n')
    #             except Exception as e:
    #                 # Xử lý nếu không tìm thấy phần tử phù hợp
    #                 print(f"Error finding link with XPath {xpath}: {e}")

    #     except Exception as e:
    #         print(f"Error processing article: {e}")

def perform_search(search_query: str) -> None:
    """Perform a search on Facebook and process the results."""

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    service = Service(log_path = os.devnull)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.facebook.com")
        time.sleep(1)

        load_cookies(driver, cookies_file_path)
        driver.refresh()
        time.sleep(1)
        time.sleep(random.randint(5, 10))
        driver.find_element(By.XPATH, '//input[@type="password" and @name="pass"]').send_keys('thacogroup123')
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@value="Continue" and @type="submit"]').click()
        time.sleep(random.randint(5, 10))

    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()
        return

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='search']"))
    )
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    if filter_pages(driver):
        process_search_results(driver)

    driver.quit()

def search() -> None:
    """Main function to execute the search queries in separate threads."""
    
    search_queries = []
    try:
        with open('search_queries.txt', 'r', encoding='utf-8') as f:
            search_queries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("search_queries.txt not found")
        sys.exit(1)

    threads = []
    for query in search_queries:
        thread = threading.Thread(target=perform_search, args=(query,))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def check_login():
    """
        check whether cookies for login is on current path.
    """
    if not os.path.exists('facebook_cookies.pkl'):
        get_cookies()

def get_cookies():
    """
        get facebook cookies for automatically login.
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    service = Service(log_path = os.devnull)
    driver = webdriver.Chrome(service=service, options=chrome_options)
    try:
        driver.get("https://www.facebook.com")
        time.sleep(1)

        load_cookies(driver, cookies_file_path)
        driver.refresh()
        time.sleep(1)

        try:
            login_button_present = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@name='login']"))
            )
        except:
            login_button_present = False
        
        if login_button_present:
            print("Cookies doesn't exist, require email and password to login.")
            email = input('Email: ')
            password = input('Password: ')
            print(email)
            print(password)
            email_input = driver.find_element(By.ID, "email")
            password_input = driver.find_element(By.ID, "pass")

            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)

            save_cookies(driver, cookies_file_path)

    except Exception as e:
        print(f"Error during login: {e}")
        driver.quit()
        return


if __name__ == "__main__":
    check_login()
    search()
