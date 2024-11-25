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
from datetime import datetime
from threading import Lock
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


def scroll_to_load_all_results(driver: webdriver.Chrome, stop_k) -> None:
    """
    Cuộn trang để tải tất cả kết quả, kiểm tra liên tiếp 10 lần nếu chiều cao không đổi mới dừng.
    Args:
        driver (webdriver.Chrome): Đối tượng driver.
    Returns:
        None
    """
    count_stop = 0

    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_count = 0  
    
    while True:
        get_element_coordinates(driver)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(1)
        new_height = driver.execute_script("return document.body.scrollHeight")
        
        if new_height == last_height:
            unchanged_count += 1
        else:
            unchanged_count = 0  
        
        if unchanged_count >= 10:
            break
        
        last_height = new_height
        count_stop += 1
        if count_stop >= stop_k:
            break

def check_duplicate_urls():
    file_path = f'results/{date_folder}/list-url.txt'
    delete_url_false = "https://www.facebook.com/search/posts?"

    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại.")
        return

    with open(file_path, 'r', encoding='utf-8') as file:
        urls = file.readlines()

    processed_urls = []
    removed_count = 0

    for url in urls:
        url = url.strip()
        if "__cft__[0]" in url:
            url = url.split("__cft__[0]")[0]
        if delete_url_false in url:
            removed_count += 1
            continue
        if url and url not in processed_urls:
            processed_urls.append(url)

    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(processed_urls))

    logger.logger('logs/info.log', f"Số lượng URL đã xóa: {removed_count}")
    logger.logger('logs/info.log', f"Tổng số URL còn lại: {len(processed_urls)}")

def get_element_coordinates(driver: webdriver.Chrome):
    """
    Lấy tọa độ (x, y) của phần tử trên trang web và lưu URL của chúng vào file,
    không sử dụng lại những tọa độ đã sử dụng rồi.

    :param driver: Đối tượng WebDriver của Selenium.
    :param date_folder: Thư mục theo ngày để lưu kết quả.
    :return: None
    """
    try:
        elements = driver.find_elements(By.XPATH, '//*[starts-with(@id, ":r")]/span/span/a[@role="link" and @tabindex="0"]')

        if not elements:
            logger.logger('logs/error.log', "No elements found on current view.")
            return

        actions = ActionChains(driver)

        used_coordinates = set()
        urls = []

        for i, element in enumerate(elements, start=1):
            try:
                location = element.location
                x = int(location['x'])
                y = int(location['y'])
                coord = (x, y)
                
                if coord in used_coordinates:
                    logger.logger('logs/info.log', f"Skipping element {i}: coordinates (x, y) ({x}, {y}) already used.")
                    continue
                
                used_coordinates.add(coord)
                actions.move_to_element_with_offset(element, 0, 0).perform()
                logger.logger('logs/info.log', f"Element {i}: coordinates (x, y) are ({x}, {y})")

                url = element.get_attribute('href')
                if url:
                    urls.append(url)
                    logger.logger('logs/info.log', f"Saved URL: {url}")
            except Exception as e:
                logger.logger('logs/error.log', f"Failed to process element {i}: {e}")

        file_path = f'results/{date_folder}/list-url.txt'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        with open(file_path, 'a', encoding='utf-8') as file:
            for url in urls:
                file.write(url + '\n')

    except Exception as e:
        logger.logger('logs/error.log', f"Error getting element coordinates: {e}")
                
def filter_pages(driver: webdriver.Chrome, stop_k: int) -> bool:
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
        time.sleep(5)
        
        
        scroll_to_load_all_results(driver,stop_k=stop_k)
        check_duplicate_urls()
        return True
    except Exception as e:
        logger.logger('logs/error.log', f"Error filtering pages or applying filter: {e}")
        return False

def perform_search(search_query,passwword,stop_k) -> None:
    """Perform a search on Facebook and process the results."""

    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--mute-audio")
    chrome_options.add_argument("--window-size=1900,1080")
    
    # chrome_options.add_argument("--force-device-scale-factor=0.25")    
    chrome_options.add_argument("--headless")

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
        # driver.quit()
        # return

    search_box = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='search']"))
    )
    search_box.send_keys(search_query)
    search_box.send_keys(Keys.RETURN)
    time.sleep(5)

    if filter_pages(driver,stop_k=stop_k):
        logger.logger('logs/info.log', f"Crawling {search_query} ...")

    driver.quit()
    
def check_login(email, password):
    """
    Kiểm tra xem đã đăng nhập vào Facebook chưa.
    Returns:
        None
    """
    
    file_path = "facebook_cookies.pkl"
    if os.path.exists(file_path):
        creation_time = os.path.getctime(file_path)
        readable_time = time.ctime(creation_time)
        # lấy time hiện tại trù đi time của readable_time nếu mà lớn hơn 2h thì xóa file
        if time.time() - creation_time > 7200:
            os.remove(file_path)
            print("File đã bị xóa.")
            
    else:
        print("File không tồn tại.")
        
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
    email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    check_login(email, password)
    search("hieuthuhai",password,stop_k=5)

