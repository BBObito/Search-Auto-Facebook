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
    count_stop = 0

    last_height = driver.execute_script("return document.body.scrollHeight")
    unchanged_count = 0  # Đếm số lần liên tiếp chiều cao không đổi
    
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
        if count_stop >= 50:
            break

def check_duplicate_urls():
    # Lấy ngày hiện tại để tạo đường dẫn đúng (nếu cần)
    date_folder = datetime.now().strftime('%Y-%m-%d')
    file_path = f'results/{date_folder}/list-url.txt'
    delete_url_false = "https://www.facebook.com/search/posts?"

    # Kiểm tra file có tồn tại không
    if not os.path.exists(file_path):
        print(f"File {file_path} không tồn tại.")
        return

    # Đọc file và xử lý URL
    with open(file_path, 'r', encoding='utf-8') as file:
        urls = file.readlines()

    # Xử lý: xóa "__cft__[0]" trở về sau và loại bỏ các URL chứa delete_url_false
    processed_urls = []
    removed_count = 0

    for url in urls:
        url = url.strip()
        # Xóa "__cft__[0]" trở về sau nếu có
        if "__cft__[0]" in url:
            url = url.split("__cft__[0]")[0]
        # Bỏ qua URL nếu chứa delete_url_false
        if delete_url_false in url:
            removed_count += 1
            continue
        # Thêm URL vào danh sách nếu chưa có
        if url and url not in processed_urls:
            processed_urls.append(url)

    # Ghi lại file với các URL đã xử lý
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write("\n".join(processed_urls))

    # print(f"Số lượng URL đã xóa: {removed_count}")
    # print(f"Tổng số URL còn lại: {len(processed_urls)}")
    logger.logger('logs/info.log', f"Số lượng URL đã xóa: {removed_count}")
    logger.logger('logs/info.log', f"Tổng số URL còn lại: {len(processed_urls)}")




# def get_element_coordinates(driver: webdriver.Chrome):
#     """
#     Lấy tọa độ (x, y) của phần tử trên trang web và lưu URL của chúng vào file.

#     :param driver: Đối tượng WebDriver của Selenium.
#     :param date_folder: Thư mục theo ngày để lưu kết quả.
#     :return: None
#     """
#     try:
#         # Tạm dừng để trang tải đầy đủ
        
#         print("Waiting for page to load completely...")
        
#         # Tìm tất cả các phần tử theo XPath
#         elements = driver.find_elements(By.XPATH, '//*[starts-with(@id, ":r")]/span/span/a[@role="link" and @tabindex="0"]')
        
#         if not elements:
#             logger.logger('logs/error.log', "No elements found on current view.")
#             return
        
#         actions = ActionChains(driver)
        
#         for i, element in enumerate(elements, start=1):
#             try:
#                 # Lấy vị trí của phần tử
#                 location = element.location
#                 x = location['x']
#                 y = location['y']
#                 actions.move_to_element_with_offset(element, 0, 0).perform()
#                 logger.logger('logs/info.log', f"Element {i}: coordinates (x, y) are ({x}, {y})")
#             except Exception as e:
#                 logger.logger('logs/error.log', f"Failed to get coordinates of element: {e}")
        
#         # Tạo thư mục kết quả nếu chưa tồn tại
#         file_path = f'results/{date_folder}/list-url.txt'
#         os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
#         # Lưu các href của elements vào file
#         with open(file_path, 'a', encoding='utf-8') as file:
#             for element in elements:
#                 url = element.get_attribute('href')
#                 if url:
#                     file.write(url + '\n')
#                     logger.logger('logs/info.log', f"Saved URL: {url}")
#     except Exception as e:
#         logger.logger('logs/error.log', f"Error getting element coordinates: {e}")

def get_element_coordinates(driver: webdriver.Chrome):
    """
    Lấy tọa độ (x, y) của phần tử trên trang web và lưu URL của chúng vào file,
    không sử dụng lại những tọa độ đã sử dụng rồi.

    :param driver: Đối tượng WebDriver của Selenium.
    :param date_folder: Thư mục theo ngày để lưu kết quả.
    :return: None
    """
    try:
        # Tạm dừng để trang tải đầy đủ
        print("Waiting for page to load completely...")
        # time.sleep(5)  # Nếu cần thiết, bạn có thể thêm thời gian chờ

        # Tìm tất cả các phần tử theo XPath
        elements = driver.find_elements(By.XPATH, '//*[starts-with(@id, ":r")]/span/span/a[@role="link" and @tabindex="0"]')

        if not elements:
            logger.logger('logs/error.log', "No elements found on current view.")
            return

        actions = ActionChains(driver)

        used_coordinates = set()
        urls = []

        for i, element in enumerate(elements, start=1):
            try:
                # Lấy vị trí của phần tử
                location = element.location
                x = int(location['x'])
                y = int(location['y'])
                coord = (x, y)
                
                # Kiểm tra xem tọa độ đã được sử dụng chưa
                if coord in used_coordinates:
                    logger.logger('logs/info.log', f"Skipping element {i}: coordinates (x, y) ({x}, {y}) already used.")
                    continue
                
                used_coordinates.add(coord)
                actions.move_to_element_with_offset(element, 0, 0).perform()
                logger.logger('logs/info.log', f"Element {i}: coordinates (x, y) are ({x}, {y})")

                # Lấy URL và lưu lại
                url = element.get_attribute('href')
                if url:
                    urls.append(url)
                    logger.logger('logs/info.log', f"Saved URL: {url}")
            except Exception as e:
                logger.logger('logs/error.log', f"Failed to process element {i}: {e}")

        # Tạo thư mục kết quả nếu chưa tồn tại
        file_path = f'results/{date_folder}/list-url.txt'
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # Lưu các href của elements vào file
        with open(file_path, 'a', encoding='utf-8') as file:
            for url in urls:
                file.write(url + '\n')

    except Exception as e:
        logger.logger('logs/error.log', f"Error getting element coordinates: {e}")

# def 
# def processing_articles(driver: webdriver.Chrome) -> None:
#     """
#     Xử lý bài viết trong quá trình cuộn.
#     Args:
#         driver (webdriver.Chrome): Đối tượng driver.
#     Returns:
#         None
#     """
        
# def scroll_and_process_results(driver: webdriver.Chrome) -> None:
#     """
#     Cuộn trang để tải kết quả và xử lý bài viết trong quá trình cuộn.
#     Args:
#         driver (webdriver.Chrome): Đối tượng driver.
#     Returns:
#         None
#     """

#     processed_articles = set()  # Bộ lưu trữ URL đã xử lý
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     unchanged_count = 0  # Đếm số lần liên tiếp chiều cao không đổi
#     file_path = f'results/{date_folder}/list-url.txt'
#     articles_file_path = f'results/{date_folder}/list-articles.txt'

#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     if os.path.exists(articles_file_path):
#         with open(articles_file_path, 'r', encoding='utf-8') as afile:
#             processed_articles.update(line.strip() for line in afile.readlines())

#     with open(file_path, 'a', encoding='utf-8') as file, \
#             open(articles_file_path, 'a', encoding='utf-8') as articles_file:
#         while True:
#             articles = driver.find_elements(By.XPATH, '//*[starts-with(@id, ":r")]/span/span/a[@role="link" and @tabindex="0"]')
#             logger.logger('logs/info.log', f"Found {len(articles)} articles on current view.")

#             # Lọc bài viết chưa xử lý
#             articles = [article for article in articles if article.get_attribute("href") not in processed_articles]

#             count = 0
#             for article in articles:
#                 if count >= 2:  # Giới hạn xử lý 3 bài viết
#                     break

#                 try:
#                     article_url = article.get_attribute("href")
#                     if not article_url:
#                         continue
                    
#                     # Ghi URL bài viết đã xử lý
#                     articles_file.write(article_url + '\n')
#                     articles_file.flush()
#                     processed_articles.add(article_url)

#                     # Tìm phần tử bài viết và thực hiện Ctrl+Click
#                     WebDriverWait(driver, 10).until(EC.element_to_be_clickable(article))
#                     ActionChains(driver).key_down(Keys.CONTROL).click(article).key_up(Keys.CONTROL).perform()

#                     # Tab mới đã mở nhưng focus vẫn ở tab gốc
#                     # Lấy danh sách các tab
#                     all_tabs = driver.window_handles

#                     # Nếu có thêm tab mới, xử lý nó
#                     if len(all_tabs) > 1:
#                         # Chuyển sang tab mới
#                         driver.switch_to.window(all_tabs[-1])
                        
#                         # Đóng tab mới
#                         driver.close()
                        
#                         # Quay lại tab gốc (focus vẫn ở tab gốc)
#                         driver.switch_to.window(all_tabs[0])

#                     current_url = driver.current_url
#                     if current_url and current_url not in processed_articles:
#                         file.write(current_url + '\n')
#                         file.flush()
#                         if "https://www.facebook.com/search/posts?__cft__[0]" not in current_url:
#                             processed_articles.add(current_url)
#                             logger.logger('logs/info.log', f"Processed and saved URL: {current_url}")
#                         # time.sleep(1)
#                         # driver.back()

#                     # count += 1  # Tăng bộ đếm bài viết đã xử lý
#                 except Exception as e:
#                     logger.logger('logs/error.log', f"Error processing article: {e}")
#                     continue

#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)
#             new_height = driver.execute_script("return document.body.scrollHeight")

#             if new_height == last_height:
#                 unchanged_count += 1
#             else:
#                 unchanged_count = 0

#             if unchanged_count >= 10:
#                 logger.logger('logs/info.log', "No new content detected. Stopping scroll.")
#                 break

#             last_height = new_height

# def scroll_and_process_results(driver: webdriver.Chrome) -> None:
#     """
#     Cuộn trang để tải kết quả và xử lý bài viết trong quá trình cuộn.
#     Args:
#         driver (webdriver.Chrome): Đối tượng driver.
#     Returns:
#         None
#     """

#     # time.sleep(2000)

#     processed_articles = set()  # Bộ lưu trữ URL đã xử lý
#     last_height = driver.execute_script("return document.body.scrollHeight")
#     unchanged_count = 0  # Đếm số lần liên tiếp chiều cao không đổi
#     date_folder = "2024-11-22"  # Tự chỉnh theo ngày thực tế
#     file_path = f'results/{date_folder}/list-url.txt'
#     articles_file_path = f'results/{date_folder}/list-articles.txt'

#     os.makedirs(os.path.dirname(file_path), exist_ok=True)

#     if os.path.exists(articles_file_path):
#         with open(articles_file_path, 'r', encoding='utf-8') as afile:
#             processed_articles.update(line.strip() for line in afile.readlines())

#     with open(file_path, 'a', encoding='utf-8') as file, \
#             open(articles_file_path, 'a', encoding='utf-8') as articles_file:
#         while True:
#             articles = driver.find_elements(By.XPATH, '//*[starts-with(@id, ":r")]/span/span/a[@role="link" and @tabindex="0"]')
#             logger.logger('logs/info.log', f"Found {len(articles)} articles on current view.")

#             articles = [article for article in articles if article.get_attribute("href") not in processed_articles]
#             count = 0 
#             print(len(articles))
#             for article in articles:
#                 # print(article.get_attribute("href"))
#                 try:
#                     article_url = article.get_attribute("href")
#                     if not article_url:
#                         continue
                    
#                     articles_file.write(article_url + '\n')
#                     articles_file.flush()
#                     processed_articles.add(article_url)

#                     # driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", article)
#                     WebDriverWait(driver, 10).until(EC.element_to_be_clickable(article))
#                     ActionChains(driver).move_to_element(article).click().perform()
#                     # clicck article
#                     # article.click()
#                     # time.sleep(1)  

#                     current_url = driver.current_url
#                     if current_url and current_url not in processed_articles:
#                         file.write(current_url + '\n')
#                         file.flush()
#                         processed_articles.add(current_url)
#                         logger.logger('logs/info.log', f"Processed and saved URL: {current_url}")
#                         time.sleep(1)
#                         driver.back()
#                         # try:
                            
#                         #     close_button = driver.find_element(By.XPATH, '//div[@aria-hidden="false" and @aria-label="Close"]')
#                         #     if close_button:
#                         #         # close_button.click()
#                         #         WebDriverWait(driver, 10).until(EC.element_to_be_clickable(close_button))
#                         #         ActionChains(driver).move_to_element(close_button).click().perform()
                                
#                         #         logger.logger('logs/info.log', "Clicked close button to navigate back.")
#                         # except Exception:
#                         #     # Nếu không có nút đóng, sử dụng driver.back()
#                         #     driver.back()
#                         #     logger.logger('logs/info.log', "Used driver.back() to navigate back.")
#                         # driver.back()
                        
#                 except Exception as e:
#                     logger.logger('logs/error.log', f"Error processing article: {e}")
#                     # driver.back()
#                     # time.sleep(2000)
#                     continue

#             driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#             time.sleep(2)
#             new_height = driver.execute_script("return document.body.scrollHeight")

#             if new_height == last_height:
#                 unchanged_count += 1
#             else:
#                 unchanged_count = 0  #

#             if unchanged_count >= 10:
#                 logger.logger('logs/info.log', "No new content detected. Stopping scroll.")
#                 break

#             last_height = new_height
            
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

def find_All_xpath(driver: webdriver.Chrome, name_file: str) -> None:
    """
    """
    xpath_target = driver.find_elements(By.XPATH, '//*[starts-with(@id, ":r")]/span/span/a[@role="link" and @tabindex="0"]')
    # lấy ra toàn bộ url sau đó lưu vào file
    file_path = f'results/{date_folder}/{name_file}.txt'
    with open(file_path, 'a', encoding='utf-8') as file:
        for element in xpath_target:
            url = element.get_attribute('href')
            if url:
                file.write(url + '\n')
                logger.logger('logs/info.log', f"Saved URL: {url}")
            else:
                logger.logger('logs/error.log', f"Failed to retrieve URL from element: {element}")
                
# def process_search_results(driver: webdriver.Chrome, top_k: int) -> None:
#     file_path = f'results/{date_folder}/before-xpath.txt'
#     # Lưu tab gốc để không đóng nhầm
#     original_tab = driver.current_window_handle

#     while True:
#         # Đọc các URL từ file và lưu vào danh sách
#         try:
#             with open(file_path, "r") as file:
#                 urls = file.readlines()
#                 urls = [url.strip() for url in urls if url.strip()]  # Loại bỏ dòng trống
#         except FileNotFoundError:
#             print("File before-xpath.txt không tồn tại.")
#             return

#         # Nếu danh sách URL trống, thoát
#         if not urls:
#             print("Không còn URL nào để xử lý.")
#             break

#         # Lấy top_k URL để xử lý
#         current_batch = urls[:top_k]
#         remaining_urls = urls[top_k:]

#         # Mở các URL trong các tab mới
#         new_tabs = []
#         for url in current_batch:
#             driver.execute_script("window.open('');")  # Mở tab mới
#             new_tab = driver.window_handles[-1]  # Lấy handle của tab mới
#             new_tabs.append(new_tab)  # Lưu handle để đóng sau
#             driver.switch_to.window(new_tab)  # Chuyển đến tab mới
#             driver.get(url)  # Điều hướng tới URL

#         # Quay lại tab gốc sau khi mở xong
#         driver.switch_to.window(original_tab)

#         # Đóng các tab mới mở
#         for tab in new_tabs:
#             driver.switch_to.window(tab)
#             driver.close()  # Đóng tab

#         # Quay lại tab gốc (đảm bảo không mất focus)
#         driver.switch_to.window(original_tab)

#         # Cập nhật file với các URL còn lại
#         with open(file_path, "w") as file:
#             file.write("\n".join(remaining_urls))

#         # Tạm dừng nếu cần thiết
#         time.sleep(1)
          
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
        time.sleep(5)
        
        
        scroll_to_load_all_results(driver)
        
        # click_see_more_buttons(driver)
        # process_search_results(driver)
        # scroll_and_process_results(driver)
        # scroll_to_load_all_results(driver)
        # find_All_xpath(driver,"before-xpath")
        # process_search_results(driver, 3)
        # find_All_xpath(driver,"after-xpath")
        check_duplicate_urls()
        return True
    except Exception as e:
        logger.logger('logs/error.log', f"Error filtering pages or applying filter: {e}")
        return False

# # def process_search_results(driver: webdriver.Chrome) -> None:
# #     """
# #     Xử lý kết quả tìm kiếm.
# #     Args:
# #         driver (webdriver.Chrome): Đối tượng driver.
# #     Returns:
# #         None
# #     """
    
# #     last_articles = driver.find_elements(By.XPATH, '//span/div/span[1]/span/a')
# #     logger.logger('logs/info.log', f"Total articles found: {len(last_articles)}")

# #     file_path = f'results/{date_folder}/list-url.txt'
# #     with open(file_path, 'a', encoding='utf-8') as file:
# #         for article in last_articles:
# #             try:
# #                 article.click()
# #                 time.sleep(5)
# #                 page_url = article.get_attribute("href")
# #                 if page_url:
# #                     file.write(page_url + '\n')
# #                     logger.logger('logs/info.log', f"Saved URL: {page_url}")
# #                 driver.back()
# #                 time.sleep(2)
# #             except Exception as inner_e:
# #                 logger.logger('logs/error.log', f"Error processing article: {inner_e}")
# #                 continue



def perform_search(search_query,passwword) -> None:
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
