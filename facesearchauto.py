from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils import logger
import time
import pickle
import os
import sys
import threading
from datetime import datetime
from threading import Lock
import random
from dotenv import load_dotenv
load_dotenv()



lock = Lock()
set_current_urls = set()

date_folder = datetime.now().strftime('%Y-%m-%d')
os.makedirs(f'results/{date_folder}', exist_ok= True)

cookies_file_path = "facebook_cookies.pkl"


def save_cookies(driver: webdriver.Chrome, file_path: str) -> None:
    """
    Chức năng này sẽ lưu cookies vào file.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
        file_path (str): Đường dẫn file để lưu cookies
    Returns:
        None
    """
    cookies = driver.get_cookies()
    with open(file_path, 'wb') as file:
        pickle.dump(cookies, file)

def load_cookies(driver: webdriver.Chrome, file_path: str) -> None:
    """
    Chức năng này sẽ load cookies từ file.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
        file_path (str): Đường dẫn file chứa cookies
    Returns:
        None
    """
    try:
        with open(file_path, 'rb') as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
    except FileNotFoundError:
        logger.logger('logs/error.log', f"No cookies found at {file_path}")

def scroll_to_load_all_results(driver: webdriver.Chrome) -> None:
    """
    Cuộn trang để tải tất cả kết quả.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        None
    """
    last_height = driver.execute_script("return document.body.scrollHeight")
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def click_see_more_buttons(driver: webdriver.Chrome) -> None:
    """
    Click vào các nút 'See More' để tải thêm kết quả.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        None
    """
    while True:
        try:
            see_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'See More') or contains(text(), 'More')]"))
            )
            see_more_button.click()
            time.sleep(2)
        except Exception as e:
            logger.logger('logs/error.log', f"No more 'See More' buttons found or error occurred: {e}")
            break

def filter_pages(driver: webdriver.Chrome) -> bool:
    """
    Lọc kết quả tìm kiếm để chỉ hiển thị bài viết gần đây nhất.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        bool: True nếu lọc thành công, ngược lại False.    
    """

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
        process_search_results(driver)
        return True
    except Exception as e:
        logger.logger('logs/error.log', f"Error filtering pages or applying filter: {e}")
        return False

def process_search_results(driver: webdriver.Chrome) -> None:
    """
    Xử lý kết quả tìm kiếm.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        None
    """
    try:
        last_articles = driver.find_elements(By.XPATH, '//span/div/span[1]/span/a')
        logger.logger('logs/info.log', f"Total articles found: {len(last_articles)}")

        file_path = f'results/{date_folder}/list-url.txt'
        with open(file_path, 'a', encoding='utf-8') as file:
            for article in last_articles:
                try:
                    article.click()
                    time.sleep(5)
                    page_url = article.get_attribute("href")
                    if page_url:
                        file.write(page_url + '\n')
                        print(f"Saved URL: {page_url}")
                    driver.back()
                    time.sleep(2)
                except Exception as inner_e:
                    logger.logger('logs/error.log', f"Error processing article: {inner_e}")
                    continue
    except Exception as e:
        logger.logger('logs/error.log', f"Error processing search results: {e}")


def perform_search(search_query: str,passwword: str) -> None:
    """Perform a search on Facebook and process the results."""

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    
    # chrome_options.add_argument("--headless")
    service = Service(log_path = os.devnull)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.facebook.com")
        time.sleep(1)

        load_cookies(driver, cookies_file_path)
        driver.refresh()
        time.sleep(1)
        time.sleep(random.randint(5, 10))
        driver.find_element(By.XPATH, '//input[@type="password" and @name="pass"]').send_keys(passwword)
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@value="Continue" and @type="submit"]').click()
        time.sleep(random.randint(5, 10))

    except Exception as e:
        logger.logger('logs/error.log', f"Error during login: {e}")
        driver.quit()
        return

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='search']"))
    )
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    if filter_pages(driver):
        logger.logger('logs/info.log', f"Crawling {search_query} ...")

    driver.quit()

def search(password: str) -> None:
    """
    Đọc các từ khóa từ file và thực hiện tìm kiếm.
    Returns:
        None
    """
    
    search_queries = []
    try:
        with open('search_queries.txt', 'r', encoding='utf-8') as f:
            search_queries = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        logger.logger('logs/error.log', "search_queries.txt not found")
        sys.exit(1)

    threads = []
    for query in search_queries:
        thread = threading.Thread(target=perform_search, args=(query,password))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

def check_login(email, password):
    """
    Kiểm tra xem đã đăng nhập vào Facebook chưa.
    Returns:
        None
    """
    if not os.path.exists('facebook_cookies.pkl'):
        get_cookies(email=email, password=password)

def get_cookies(email: str, password: str):
    """
    Lấy cookies từ Facebook.
    Returns:
        None
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
            email_input = driver.find_element(By.ID, "email")
            password_input = driver.find_element(By.ID, "pass")

            email_input.send_keys(email)
            password_input.send_keys(password)
            password_input.send_keys(Keys.RETURN)
            time.sleep(5)

            save_cookies(driver, cookies_file_path)

    except Exception as e:
        logger.logger('logs/error.log', f"Error during login: {e}")
        driver.quit()
        return


if __name__ == "__main__":
    # time start
    start_time = time.time()
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    check_login(email, password)
    search(password=password)
    # time end
    end_time = time.time()
    logger.logger('logs/info.log', f"Execution time: {end_time - start_time} seconds")
