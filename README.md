# BTL CSDL – Project 5: Quản lý hãng vận tải hành khách đường dài

## 1. Giới thiệu

Ứng dụng web quản lý hãng vận tải hành khách đường dài được xây dựng bằng **Python Flask** và **MySQL 8.0**.

Hệ thống hỗ trợ quản lý phương tiện, tài xế, tuyến đường, chuyến xe, bảo dưỡng, bảng lương và thống kê doanh thu. Ứng dụng cung cấp giao diện trực quan, giúp người dùng thực hiện các nghiệp vụ quản lý mà không cần sử dụng trực tiếp câu lệnh SQL.

## 2. Công nghệ sử dụng

- Backend: Python, Flask.
- Frontend: HTML, CSS, Jinja2.
- Cơ sở dữ liệu: MySQL 8.0.
- Kết nối CSDL: mysql-connector-python.
- Thiết kế mô hình EER: Draw.io.
- Quản lý mã nguồn: Git, GitHub.

## 3. Cấu trúc thư mục

| Thư mục / File         | Nội dung                                                                  |
|------------------------|---------------------------------------------------------------------------|
| `database/`            | Các file SQL tạo CSDL, bảng, ràng buộc, dữ liệu mẫu, truy vấn và kiểm thử |
| `app/`                 | Ứng dụng Flask (`app.py`, `templates/`, `static/`)                        |
| `app/requirements.txt` | Danh sách thư viện Python cần thiết                                       |
| `screenshots/`         | Ảnh chụp giao diện website và sơ đồ EER                                   |
| `docs/`                | Báo cáo bài tập lớn (Word/PDF)                                            |
| `backup/`              | Bản sao lưu CSDL trước khi triển khai website                             |
| `README.md`            | Giới thiệu và hướng dẫn cài đặt dự án                                     |
| `.gitignore`           | Các file và thư mục không đưa lên GitHub                                  |

## 4. Yêu cầu môi trường

- Python 3.10 trở lên.
- MySQL Server 8.0.
- MySQL Workbench hoặc công cụ quản lý MySQL tương đương.
- Git (nếu tải mã nguồn bằng lệnh git clone).

## 5. Hướng dẫn cài đặt và chạy ứng dụng

### Bước 1. Tải mã nguồn

Tải repository từ GitHub bằng chức năng **Code → Download ZIP**, sau đó giải nén và mở thư mục dự án bằng Visual Studio Code.

### Bước 2. Khởi tạo cơ sở dữ liệu

Mở MySQL Workbench, kết nối đến MySQL Server và lần lượt thực thi các file trong thư mục `database/` theo thứ tự:

1. `01_create_database.sql`: Tạo cơ sở dữ liệu.
2. `02_create_tables.sql`: Tạo các bảng và khóa ngoại.
3. `03_constraints.sql`: Thiết lập các ràng buộc nghiệp vụ.
4. `04_insert_data.sql`: Nhập dữ liệu mẫu.
5. `05_queries.sql`: Tạo view và thực hiện các truy vấn báo cáo.

Có thể chạy thêm `06_test.sql` và `07_full_tests.sql` để kiểm tra dữ liệu và các ràng buộc.

**Cảnh báo:** File `00_drop_table.sql` chỉ sử dụng khi cần xóa và khởi tạo lại dữ liệu. Không chạy file này trên cơ sở dữ liệu đang sử dụng nếu chưa sao lưu.

### Bước 3. Tạo môi trường ảo Python

Mở Terminal tại thư mục gốc của dự án:

```bash
cd app
python -m venv .venv
```

Kích hoạt môi trường ảo trên Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Trên Windows Command Prompt:

```cmd
.venv\Scripts\activate.bat
```

Trên macOS hoặc Linux:

```bash
source .venv/bin/activate
```

### Bước 4. Cài đặt thư viện

```bash
python -m pip install -r requirements.txt
```

### Bước 5. Khởi động website

```bash
python app.py
```

Khi chạy, chương trình yêu cầu nhập mật khẩu MySQL.

Thông tin kết nối mặc định:

| Thông số | Giá trị    |
|----------|------------|
|   Host   | 127.0.0.1  |
|   Port   | 3306       |
|   User   | root       |
| Database | ql_van_tai |

Nhập mật khẩu MySQL của máy đang sử dụng, sau đó mở trình duyệt tại địa chỉ:

**http://127.0.0.1:5000**

Nếu MySQL sử dụng tài khoản, host hoặc port khác, cập nhật thông tin kết nối trong hàm `get_connection()` tại file `app/app.py`.

## 6. Chức năng chính

### 6.1. Dashboard tổng quan

Hiển thị các thông tin thống kê tổng quan của hệ thống.

### 6.2. Quản lý xe

- Hiển thị danh sách phương tiện.
- Thêm, sửa và xóa thông tin xe.
- Quản lý biển số, số chỗ ngồi, thông tin sản xuất và trạng thái hoạt động.

### 6.3. Quản lý tài xế

- Hiển thị danh sách tài xế.
- Thêm, sửa và xóa thông tin tài xế.
- Quản lý giấy phép lái xe, thông tin liên hệ và thâm niên.

### 6.4. Quản lý tuyến đường

- Thêm, sửa và xóa tuyến đường.
- Quản lý điểm đi, điểm đến, chiều dài và độ phức tạp tuyến đường.

### 6.5. Quản lý chuyến xe

- Quản lý thông tin chuyến xe và phân công phương tiện, lái xe, phụ xe.
- Kiểm tra số lượng hành khách và các ràng buộc phân công.
- Kiểm tra trùng lịch.
- Hỗ trợ ẩn và khôi phục chuyến xe.

### 6.6. Quản lý bảo dưỡng

- Theo dõi lịch sử bảo dưỡng phương tiện.
- Quản lý nội dung, thời gian và chi phí bảo dưỡng.
- Hiển thị thời hạn bảo dưỡng tiếp theo và danh sách xe quá hạn.

### 6.7. Bảng lương và doanh thu

- Tính lương tài xế theo tháng dựa trên số chuyến, vai trò và độ phức tạp tuyến đường.
- Thống kê doanh thu theo phương tiện trong khoảng thời gian được chọn.

## 7. Thiết kế cơ sở dữ liệu

Cơ sở dữ liệu bao gồm 5 bảng chính:

|    Bảng     | Nội dung                      |
|-------------|-------------------------------|
|     XE      | Thông tin phương tiện         |
|   TAI_XE    | Thông tin tài xế              |
| TUYEN_DUONG | Thông tin tuyến đường         |
|  CHUYEN_XE  | Thông tin chuyến xe           |
|  BAO_DUONG  | Lịch sử bảo dưỡng phương tiện |

Các bảng được liên kết thông qua khóa chính và khóa ngoại nhằm đảm bảo tính toàn vẹn dữ liệu.

### Ràng buộc nghiệp vụ

- Số khách không vượt quá số chỗ ngồi của xe trừ 2.
- Lái xe chính và phụ xe phải là hai tài xế khác nhau.
- Độ phức tạp tuyến đường thuộc tập {1, 2, 3}.
- Mỗi chuyến xe có đúng một xe, một tuyến đường, một lái xe chính và một phụ xe.
- Lái xe chính và phụ xe được phân công cố định trong suốt chuyến đi.

## 8. Hình ảnh và tài liệu

- Thư mục `screenshots/`: Ảnh chụp giao diện website và sơ đồ EER.
- Thư mục `docs/`: Báo cáo bài tập lớn và tài liệu thiết kế hệ thống.

## 9. Thành viên thực hiện

- Môn học: Cơ sở dữ liệu.
- Đề tài: Project 5 – Quản lý hãng vận tải hành khách đường dài.
- Giảng viên hướng dẫn: Nguyễn Việt Dũng.
- Lớp: INT1313-20261-06.
- Nhóm: Cở Sở Dữ Liệu - 06.

| STT |      Họ và tên      | Mã sinh viên |
|-----|---------------------|--------------|
|  1  | Hoàng Huy Đại       |  B24DCCN090  |
|  2  | Nguyễn Tất Dũng     |  B24DCCN157  |
|  3  | Cao Xuân Chính      |  B24DCCN076  |
|  4  | Nguyễn Quang Minh   |  B24DCCN396  |
|  5  | Trần Quốc Việt      |  B24DCCN617  |


Dự án được thực hiện phục vụ mục đích học tập trong khuôn khổ bài tập lớn môn Cơ sở dữ liệu.