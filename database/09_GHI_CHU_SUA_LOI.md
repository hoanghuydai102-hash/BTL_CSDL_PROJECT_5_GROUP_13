# Ban sua toi thieu - 2026-11-08

- 07_full_tests.sql: sua ID cua 4 tai xe (LAST_INSERT_ID tren INSERT nhieu dong tra ID dau tien), lay MaChuyen bang SELECT, phan biet loi MySQL 1644 (SIGNAL) va 3819 (CHECK) voi loi SQL khac.
- 05_queries.sql: luong tu dong theo thang/nam hien tai, chi tinh chuyen co thoi diem khoi hanh truoc NOW().
- Giu nguyen 02_create_tables.sql va 03_constraints.sql, chua co bang chung can sua trigger.
- Test 01: 44 khach > 45 - 2 = 43, dung de bai. Test 12: 10 ghe < 10 khach + 2, dung de bai.
- 05a la tien dieu kien cho 05b,05c,06,10-15. Neu 05a FAIL, khong ket luan cac test phu thuoc.
- Test 14 va 15 con phu thuoc cach dinh nghia thoi gian bao duong va thoi gian ket thuc; can kiem tra ket qua MySQL.
- Chua chay MySQL trong moi truong nay; PASS/FAIL phai duoc xac nhan bang MySQL Workbench.
- Tiep theo: kiem tra 3 truy van luong, doanh thu, bao duong voi du lieu mau; sau do EER/PDF va app.
