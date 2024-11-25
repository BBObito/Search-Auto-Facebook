import os
import sys
sys.path.append('../')

def logger(path_log, text):
    os.makedirs(f'{"/".join(path_log.split("/")[:-1])}', exist_ok=True)
    with open(f'{path_log}', 'a+', encoding='utf-8') as f:
        f.write(str(text) + '\n')
        f.close()

# save script
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

