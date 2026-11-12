# PROJECT 5 — ĐỀ BÀI GỐC VÀ ĐỐI CHIẾU SOURCE

Nguồn: đề bài do người dùng cung cấp ngày 2026-11-08. Đây là tài liệu yêu cầu chuẩn để đối chiếu khi chỉnh sửa SQL, EER và ứng dụng.

## Yêu cầu dữ liệu
- XE: biển số, màu xe, hãng sản xuất, đời xe, model, số ghế, số năm sử dụng, ngày bảo dưỡng cuối cùng.
- TAI_XE: tên, CMT/CCCD, số bằng lái, loại bằng, địa chỉ, ngày sinh, thâm niên; có thể làm lái xe hoặc phụ xe ở nhiều chuyến khác nhau.
- CHUYEN_XE: xe, tuyến, một lái xe và một phụ xe cố định, số khách, giá vé; số khách <= số ghế - 2.
- TUYEN_DUONG: điểm đầu/cuối, độ dài, độ phức tạp 1/2/3.

## Yêu cầu truy vấn
1. Lương tháng tính đến hiện tại theo các chuyến đã thực hiện trong tháng: vai trò lái xe nhận gấp đôi phụ xe; hệ số theo độ khó tự chọn.
2. Doanh thu từng xe theo khoảng ngày bắt đầu/kết thúc, từ số khách và giá vé các chuyến đã thực hiện.
3. Ngày bảo dưỡng tiếp theo và danh sách xe quá hạn: chu kỳ tối đa 360 ngày, giảm 1 ngày/100 km làm việc; km làm việc = km thực tế * hệ số độ khó (tự chọn).
4. Số lượng bản ghi từng bảng phải hiển thị trong ứng dụng.

## Yêu cầu nộp và điểm
- Yêu cầu 1 (40%): PDF mô tả thực thể, thuộc tính, quan hệ, sơ đồ EER.
- Yêu cầu 2 (30%): SQL MySQL tạo bảng, dữ liệu mẫu, truy vấn yêu cầu.
- Yêu cầu 3 (30%): link GitHub ứng dụng có giao diện người không biết lập trình sử dụng được; 10% cho tính năng yêu cầu 2, tối đa 20% tính năng phụ, mỗi tính năng phụ 2%.

## Đối chiếu với bản SQL hiện tại (rà soát tĩnh, chưa chạy MySQL)
- XE: thiếu cột lưu trực tiếp số năm sử dụng và ngày bảo dưỡng cuối; có thể suy ra năm sử dụng từ NamSanXuat, lần bảo dưỡng cuối từ BAO_DUONG hoàn thành. Cần diễn giải rõ trong EER và truy vấn, hoặc bổ sung theo quyết định thiết kế.
- TAI_XE: thâm niên có thể tính từ NgayVaoNghe; nên hiển thị trong app.
- CHUYEN_XE: hai FK vai trò riêng, trigger giới hạn khách <= SoChoNgoi - 2. Với 45 ghế, 44 khách là VƯỢT giới hạn 43; TEST 01 dùng 44 là đúng, không sửa thành 46 vì cho rằng 44 hợp lệ.
- TUYEN_DUONG: DoPhucTap CHECK IN (1,2,3), phù hợp.
- 05_queries.sql lương: đang đặt @Thang=11, @Nam=2025, KHÔNG tự lấy tháng hiện tại; phải sửa hoặc thêm query dùng CURDATE() và chỉ tính chuyến đã hoàn thành đến hiện tại.
- 05_queries.sql doanh thu: có lọc trạng thái đã hoàn thành, ngày bắt đầu/kết thúc, tính SoKhach * GiaVe; phù hợp về hướng tính.
- 05_queries.sql bảo dưỡng: lấy MAX(ThoiGianBaoDuong) có trạng thái Hoàn thành, tính km trọng số sau mốc đó, giảm FLOOR(km/100), ngày đến hạn = mốc bảo dưỡng + GREATEST(360 - số ngày giảm, 0). Cần thống nhất cách xử lý xe chưa có lịch sử bảo dưỡng (hiện trả NULL, không nằm trong danh sách quá hạn), mốc thời gian của chuyến hoàn thành và cách hiểu số km tích lũy.
- 05_queries.sql đếm bản ghi có sẵn; ứng dụng vẫn phải hiển thị.
- 07_full_tests.sql có vấn đề: LAST_INSERT_ID() của INSERT nhiều hàng là ID đầu tiên; phải lấy ID từng nhân viên, không tính lùi. Test 12 giảm ghế xuống 10 với 10 khách không phải vượt mức 10-2=8, nên thực ra ĐÚNG là test âm; không sửa thành 9 vì cho rằng 10 là hợp lệ. Test 13 dùng MaChuyen là đúng theo schema hiện tại.
- Bộ test hiện chỉ so sánh có lỗi/không lỗi, cần xác nhận lỗi SQLSTATE 45000 và thông điệp nghiệp vụ, tránh PASS giả.
- Không có bằng chứng ứng dụng và EER/PDF đã hoàn thành; đây là hai đầu ra riêng cần làm.

## Ưu tiên
P0: sửa test harness sai ID, xác nhận tất cả test và loại lỗi; bảo đảm 3 truy vấn cốt lõi trả dữ liệu đúng.
P1: chuyển lương sang tháng hiện tại, xử lý xe chưa bảo dưỡng, thống nhất trường suy ra và tài liệu EER.
P2: app hiển thị 3 báo cáo + đếm bản ghi, các chức năng phụ để tối đa điểm.
