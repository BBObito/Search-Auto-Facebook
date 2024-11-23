# Tự động tìm kiếm trang Facebook

## Mô tả dự án

Dự án này là một script tự động hóa bằng Python sử dụng Selenium để đăng nhập vào Facebook, thực hiện các truy vấn tìm kiếm, lọc kết quả chỉ bao gồm các Post, sau đó xử lý kết quả bằng cách lưu URL. Script hỗ trợ đa luồng, cho phép thực hiện đồng thời nhiều truy vấn tìm kiếm.

## Tính năng

- **Đăng nhập tự động**: Đăng nhập Facebook bằng cookies hoặc thông tin đăng nhập của người dùng.
- **Thực hiện tìm kiếm**: Thực hiện tìm kiếm dựa trên danh sách truy vấn.
- **Lọc Post**: Lọc kết quả tìm kiếm chỉ bao gồm các Post Facebook.
- **Đa luồng**: Hỗ trợ thực thi đồng thời nhiều truy vấn tìm kiếm.

## Yêu cầu

- Python 3.x
- Trình duyệt Google Chrome
- Selenium 4 không cần chrome driver nhưng lưu ý thiết bị phải có Trình duyệt Google Chrome

## Cài đặt

1. **Clone kho lưu trữ**:

```bash
git clone https://github.com/ifobito/Search-Auto-Facebook.git
cd Search-Auto-Facebook
```

2. **Thiết lập môi trường ảo (khuyến nghị):**

```bash
python -m venv .venv
source .venv/bin/activate  # Trên Windows sử dụng `.venv\Scripts\activate`
```

3. **Cài đặt các gói cần thiết:**

```bash
pip install -r requirements.txt
```

## Sử dụng

1. **Chuẩn bị danh sách truy vấn tìm kiếm:**
- Tạo một file văn bản có tên `search_queries.txt` trong thư mục dự án.
- Thêm mỗi truy vấn tìm kiếm vào một dòng trong file.

2. **Chạy script:**

```bash
python facesearchauto.py <email_facebook_của_bạn> <mật_khẩu_facebook_của_bạn>
```

***Ví dụ***

```bash
python facesearchauto.py user@example.com mysecurepassword
```

Script sẽ thực hiện:

- Đăng nhập vào Facebook.
- Thực hiện mỗi truy vấn tìm kiếm từ `search_queries.txt`.
- Lọc kết quả chỉ bao gồm các trang.
- Lưu URL các post tìm được.
- Lưu kết quả vào thư mục `results/YYYY-MM-DD/`, trong đó `YYYY-MM-DD` là ngày hiện tại.

3. **Kết quả**
- Ảnh chụp màn hình và URL của các trang được xác định sẽ được lưu trong thư mục `results`.
- Script sẽ thêm URL mới tìm được vào *newphishingpages.txt* (nếu chưa có) .

## Ghi chú

- **Cookies**: Script cố gắng sử dụng cookies đã lưu (facebook_cookies.pkl) để bỏ qua bước đăng nhập. Nếu cookies không hợp lệ hoặc không tồn tại, script sẽ thực hiện đăng nhập thông qua email và mật khẩu cung cấp.
- **Đa luồng**: Script xử lý đồng thời nhiều truy vấn tìm kiếm. Điều chỉnh số lượng luồng trong script nếu cần, dựa trên khả năng hệ thống của bạn.

## Xử lý sự cố

- **Hiệu suất chậm**: Facebook có thể giới hạn tốc độ duyệt nếu script chạy quá nhanh. Hãy tăng thời gian chờ trong script nếu gặp sự cố.
- **Vấn đề đăng nhập**: Nếu script không đăng nhập được, hãy xóa file `facebook_cookies.pkl` và chạy lại script để thực hiện đăng nhập thủ công.

> [!CHÚ Ý]
> Không đảm bảo mã sạch hoặc đã kiểm tra bảo mật. Đây là repo chỉ dành cho mục đích giáo dục. Không sử dụng vào mục đích bất hợp pháp. Tôi không chịu trách nhiệm với bất kỳ hành động sử dụng trái phép nào. Chỉ sử dụng cho mục đích học tập!

## Contact (tùy chọn)

Nếu bạn có thắc mắc gì liên hệ mail:
- ky.tran1752003@gmail.com