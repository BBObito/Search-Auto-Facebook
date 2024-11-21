from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
import time
from selenium.webdriver.common.keys import Keys


# Khởi tạo WebDriver
driver = webdriver.Chrome()

# Mở trang web
driver.get("https://medlatec.vn/tin-tuc/dau-bung-tung-con-canh-bao-nhung-benh-ly-nao-s195-n18026?gidzl=e10u2A062YwZ2308e1eAAgCFDWozIrWilLDZ1BLBMYssKsHVu1SAVxLLELcz4GSjwmCrM64m80iHem4BBW")

# Tìm liên kết
link = driver.find_element(By.XPATH, "/html/body/div[1]/main/div[1]/div/ol/li[2]/a")

# Mở liên kết trong tab mới (giữ Ctrl và click)
ActionChains(driver).key_down(Keys.CONTROL).click(link).key_up(Keys.CONTROL).perform()

# Đợi một chút để tab mới mở ra
time.sleep(2)

# Lấy danh sách các tab
tabs = driver.window_handles

# Chuyển qua tab mới
driver.switch_to.window(tabs[1])  # Tab thứ 2 (index là 1)

# Thực hiện hành động trên tab mới (nếu cần)
print(driver.current_url)

# Đóng tab hiện tại
driver.close()

# Quay lại tab ban đầu
driver.switch_to.window(tabs[0])

# Kết thúc phiên làm việc
driver.quit()
