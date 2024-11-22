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
from selenium.webdriver.common.action_chains import ActionChains
from dotenv import load_dotenv
load_dotenv()



lock = Lock()
set_current_urls = set()

date_folder = datetime.now().strftime('%Y-%m-%d')
os.makedirs(f'results/{date_folder}', exist_ok= True)

cookies_file_path = "facebook_cookies.pkl"


def save_cookies(driver: webdriver.Chrome, file_path) -> None:
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

def load_cookies(driver: webdriver.Chrome, file_path) -> None:
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
    Cuộn trang để tải tất cả kết quả, kiểm tra liên tiếp 10 lần nếu chiều cao không đổi mới dừng.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        None
    """
    import time

    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_count = 0  # Đếm số lần liên tiếp chiều cao không đổi
    
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            unchanged_count += 1
        else:
            unchanged_count = 0  # Reset nếu chiều cao thay đổi
        
        if unchanged_count >= 10:  # Dừng khi không đổi liên tiếp 10 lần
            break
        
        last_height = new_height

def scroll_and_process_results(driver: webdriver.Chrome) -> None:
    """
    Cuộn trang để tải kết quả và xử lý bài viết trong quá trình cuộn.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        None
    """

    import os
    import time

    processed_articles = set()  # Bộ lưu trữ URL đã xử lý
    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_count = 0  # Đếm số lần liên tiếp chiều cao không đổi
    date_folder = "2024-11-22"  # Tự chỉnh theo ngày thực tế
    file_path = f'results/{date_folder}/list-url.txt'
    articles_file_path = f'results/{date_folder}/list-articles.txt'

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(articles_file_path):
        with open(articles_file_path, 'r', encoding='utf-8') as afile:
            processed_articles.update(line.strip() for line in afile.readlines())

    with open(file_path, 'a', encoding='utf-8') as file, \
            open(articles_file_path, 'a', encoding='utf-8') as articles_file:
        while True:
            articles = driver.find_elements(By.XPATH, '//span/div/span[1]/span/a')
            logger.logger('logs/info.log', f"Found {len(articles)} articles on current view.")

            articles = [article for article in articles if article.get_attribute("href") not in processed_articles]

            for article in articles:
                try:
                    article_url = article.get_attribute("href")
                    if not article_url:
                        continue
                    
                    articles_file.write(article_url + '\n')
                    articles_file.flush()
                    processed_articles.add(article_url)

                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", article)
                    # WebDriverWait(driver, 10).until(EC.element_to_be_clickable(article))
                    # ActionChains(driver).move_to_element(article).click().perform()
                    # clicck article
                    article.click()
                    time.sleep(1)  

                    current_url = driver.current_url
                    if current_url and current_url not in processed_articles:
                        file.write(current_url + '\n')
                        file.flush()
                        processed_articles.add(current_url)
                        logger.logger('logs/info.log', f"Processed and saved URL: {current_url}")

                    driver.back()
                    # time.sleep(2)

                except Exception as e:
                    logger.logger('logs/error.log', f"Error processing article: {e}")
                    # driver.back()
                    # time.sleep(2)
                    continue

            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                unchanged_count += 1
            else:
                unchanged_count = 0  #

            if unchanged_count >= 10:
                logger.logger('logs/info.log', "No new content detected. Stopping scroll.")
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
    # time.sleep(500)
    try:
        pages_filter = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Posts')]"))
        )
        pages_filter.click()
        
        recent_posts = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//input[@aria-label="Recent Posts" and @type="checkbox" and @role="switch" and @aria-checked="false"]'))
        )
        recent_posts.click()
        
        # scroll_to_load_all_results(driver)
        # click_see_more_buttons(driver)
        # process_search_results(driver)
        scroll_and_process_results(driver)
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
                    logger.logger('logs/info.log', f"Saved URL: {page_url}")
                driver.back()
                time.sleep(2)
            except Exception as inner_e:
                logger.logger('logs/error.log', f"Error processing article: {inner_e}")
                continue



def perform_search(search_query,passwword) -> None:
    """Perform a search on Facebook and process the results."""

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    # chrome_options.add_argument("--force-device-scale-factor=0.25")    
    # chrome_options.add_argument("--headless")

    service = Service(log_path = os.devnull)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get("https://www.facebook.com")
        time.sleep(1)

        load_cookies(driver, cookies_file_path)
        driver.refresh()
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@type="password" and @name="pass"]').send_keys(passwword)
        time.sleep(1)
        driver.find_element(By.XPATH, '//input[@value="Continue" and @type="submit"]').click()

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

def search(password) -> None:
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

def get_cookies(email, password):
    """
    Lấy cookies từ Facebook.
    Returns:
        None
    """
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--headless")
    
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
