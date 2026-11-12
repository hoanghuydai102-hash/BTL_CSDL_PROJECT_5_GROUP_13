-- File: 04_insert_data.sql
-- THÊM DỮ LIỆU MẪU VÀO CƠ SỞ DỮ LIỆU

USE QL_VAN_TAI;

-- 1. THÊM DỮ LIỆU BẢNG XE

INSERT INTO XE (
    BienSo, MauSac, HangSanXuat, DoiXe,
    Model, NamSanXuat, SoChoNgoi, TrangThai
)
VALUES
('29A-12345', 'Trắng', 'Toyota', 'Hiace', 'Hiace 2.8', 2022, 45, TRUE),
('30F-67890', 'Bạc', 'Hyundai', 'Universe', 'Universe 2023', 2023, 29, TRUE),
('51B-11223', 'Đen', 'Ford', 'Transit', 'Transit Luxury', 2021, 16, TRUE),
('29B-44556', 'Xanh', 'Thaco', 'TB120S', 'Thaco TB120S', 2022, 45, TRUE),
('30G-77889', 'Trắng', 'Samco', 'Felix', 'Samco Felix', 2020, 29, TRUE),
('51C-99001', 'Đỏ', 'Mercedes-Benz', 'Sprinter', 'Sprinter 519', 2023, 16, TRUE);


-- 2. THÊM DỮ LIỆU BẢNG TAI_XE

INSERT INTO TAI_XE (
    MaTaiXe, HoTen, SoCCCD, SoBangLai, LoaiBangLai,
    DiaChi, NgaySinh, NgayVaoNghe, SDT, Email, TrangThai
)
VALUES
(1, 'Nguyễn Văn An', '001088000001', 'DL001', 'E',
 'Hà Nội', '1988-03-15', '2010-06-01', '0901000001', 'an.nguyen@example.com', 'Đang làm việc'),
(2, 'Trần Văn Bình', '001088000002', 'DL002', 'D',
 'Hà Nội', '1985-07-20', '2008-05-10', '0901000002', 'binh.tran@example.com', 'Đang làm việc'),
(3, 'Lê Văn Cường', '001088000003', 'DL003', 'E',
 'Bắc Ninh', '1990-01-12', '2012-03-15', '0901000003', 'cuong.le@example.com', 'Đang làm việc'),
(4, 'Phạm Văn Dũng', '001088000004', 'DL004', 'D',
 'Hải Phòng', '1987-09-25', '2011-08-20', '0901000004', 'dung.pham@example.com', 'Đang làm việc'),
(5, 'Hoàng Văn Đức', '001088000005', 'DL005', 'E',
 'Nam Định', '1982-11-08', '2005-04-12', '0901000005', 'duc.hoang@example.com', 'Đang làm việc'),
(6, 'Đỗ Văn Giang', '001088000006', 'DL006', 'D',
 'Hà Nam', '1991-05-17', '2014-02-01', '0901000006', 'giang.do@example.com', 'Đang làm việc'),
(7, 'Vũ Văn Hùng', '001088000007', 'DL007', 'E',
 'Hà Nội', '1984-12-30', '2007-09-10', '0901000007', 'hung.vu@example.com', 'Đang làm việc'),
(8, 'Bùi Văn Khánh', '001088000008', 'DL008', 'D',
 'Thanh Hóa', '1989-06-22', '2013-07-15', '0901000008', 'khanh.bui@example.com', 'Đang làm việc'),
(9, 'Đặng Văn Long', '001088000009', 'DL009', 'E',
 'Ninh Bình', '1986-04-18', '2009-11-05', '0901000009', 'long.dang@example.com', 'Đang làm việc'),
(10, 'Ngô Văn Minh', '001088000010', 'DL010', 'D',
 'Hà Nội', '1992-08-14', '2015-01-20', '0901000010', 'minh.ngo@example.com', 'Đang làm việc'),
(11, 'Dương Văn Nam', '001088000011', 'DL011', 'E',
 'Hưng Yên', '1983-02-27', '2006-06-15', '0901000011', 'nam.duong@example.com', 'Đang làm việc'),
(12, 'Lý Văn Phúc', '001088000012', 'DL012', 'D',
 'Hải Dương', '1990-10-05', '2012-12-01', '0901000012', 'phuc.ly@example.com', 'Đang làm việc');


-- 3. THÊM DỮ LIỆU BẢNG TUYEN_DUONG

INSERT INTO TUYEN_DUONG (
    MaTuyenDuong, TenTuyenDuong, DiemDi, DiemDen,
    ChieuDai, DoPhucTap, ThoiGianDi, TrangThai
)
VALUES
(1, 'Hà Nội - Hải Phòng', 'Hà Nội', 'Hải Phòng', 120.00, 1, 2.00, TRUE),
(2, 'Hà Nội - Thanh Hóa', 'Hà Nội', 'Thanh Hóa', 160.00, 2, 3.00, TRUE),
(3, 'Hà Nội - Nghệ An', 'Hà Nội', 'Nghệ An', 300.00, 2, 5.00, TRUE),
(4, 'Hà Nội - Lào Cai', 'Hà Nội', 'Lào Cai', 290.00, 3, 6.00, TRUE),
(5, 'Hà Nội - Quảng Ninh', 'Hà Nội', 'Quảng Ninh', 180.00, 2, 3.50, TRUE),
(6, 'Hà Nội - Hà Giang', 'Hà Nội', 'Hà Giang', 300.00, 3, 7.00, TRUE);


-- 4. THÊM DỮ LIỆU BẢNG BAO_DUONG

INSERT INTO BAO_DUONG (
    MaBaoDuong, MaXe, ThoiGianBaoDuong,
    NoiDung, ChiPhi, TrangThai
)
VALUES
(1, 1, '2025-09-10 08:00:00', 'Thay dầu và kiểm tra động cơ', 2500000, 'Hoàn thành'),
(2, 2, '2025-09-12 08:00:00', 'Kiểm tra hệ thống phanh', 4200000, 'Hoàn thành'),
(3, 3, '2025-09-15 08:00:00', 'Bảo dưỡng động cơ định kỳ', 1800000, 'Hoàn thành'),
(4, 4, '2025-09-18 08:00:00', 'Kiểm tra hệ thống điện', 3200000, 'Hoàn thành'),
(5, 5, '2025-09-20 08:00:00', 'Thay lốp và kiểm tra khung gầm', 5500000, 'Hoàn thành'),
(6, 6, '2025-09-25 08:00:00', 'Bảo dưỡng toàn bộ xe', 6000000, 'Hoàn thành');


-- 5. THÊM DỮ LIỆU BẢNG CHUYEN_XE

INSERT INTO CHUYEN_XE (
    MaChuyen, MaXe, MaTaiXe, MaPhuXe, MaTuyenDuong,
    SoKhach, ThoiGianKhoiHanh, SoKmThucTe, GiaVe, TrangThai
)
VALUES

-- 5.1. CÁC CHUYẾN XE HOÀN THÀNH TRONG THÁNG 10/2025

(1, 1, 1, 2, 1, 40, '2025-10-05 06:00:00', 120.00, 150000, 'Đã hoàn thành'),
(2, 2, 3, 4, 2, 25, '2025-10-06 07:00:00', 160.00, 180000, 'Đã hoàn thành'),
(3, 3, 5, 6, 3, 12, '2025-10-07 06:30:00', 300.00, 250000, 'Đã hoàn thành'),
(4, 4, 7, 8, 4, 40, '2025-10-08 05:00:00', 290.00, 300000, 'Đã hoàn thành'),
(5, 5, 9, 10, 5, 25, '2025-10-09 07:30:00', 180.00, 200000, 'Đã hoàn thành'),
(6, 6, 11, 12, 6, 12, '2025-10-10 05:30:00', 300.00, 350000, 'Đã hoàn thành'),

-- 5.2. CÁC CHUYẾN XE HOÀN THÀNH TRONG THÁNG 11/2025

(7, 1, 1, 2, 1, 38, '2025-11-05 06:00:00', 121.00, 150000, 'Đã hoàn thành'),
(8, 2, 3, 4, 2, 27, '2025-11-06 07:00:00', 162.00, 180000, 'Đã hoàn thành'),
(9, 3, 5, 6, 3, 14, '2025-11-07 06:30:00', 302.00, 250000, 'Đã hoàn thành'),
(10, 4, 7, 8, 4, 42, '2025-11-08 05:00:00', 292.00, 300000, 'Đã hoàn thành'),
(11, 5, 9, 10, 5, 26, '2025-11-09 07:30:00', 182.00, 200000, 'Đã hoàn thành'),
(12, 6, 11, 12, 6, 13, '2025-11-10 05:30:00', 303.00, 350000, 'Đã hoàn thành'),

-- 5.3. CÁC CHUYẾN XE ĐÃ LÊN LỊCH TRONG THÁNG 11/2026

(13, 1, 1, 2, 1, 35, '2026-11-10 06:00:00', 0, 150000, 'Đã lên lịch'),
(14, 2, 3, 4, 2, 24, '2026-11-11 07:00:00', 0, 180000, 'Đã lên lịch'),
(15, 3, 5, 6, 3, 10, '2026-11-12 06:30:00', 0, 250000, 'Đã lên lịch'),
(16, 4, 7, 8, 4, 38, '2026-11-13 05:00:00', 0, 300000, 'Đã lên lịch'),
(17, 5, 9, 10, 5, 22, '2026-11-14 07:30:00', 0, 200000, 'Đã lên lịch'),
(18, 6, 11, 12, 6, 10, '2026-11-15 05:30:00', 0, 350000, 'Đã lên lịch');


-- 6. KIỂM TRA TOÀN BỘ DỮ LIỆU

SELECT * FROM XE;

SELECT * FROM TAI_XE;

SELECT * FROM TUYEN_DUONG;

SELECT * FROM CHUYEN_XE;

SELECT * FROM BAO_DUONG;

-- 7. THỐNG KÊ SỐ LƯỢNG BẢN GHI

SELECT 'XE' AS TenBang, COUNT(*) AS SoLuong FROM XE
UNION ALL
SELECT 'TAI_XE', COUNT(*) FROM TAI_XE
UNION ALL
SELECT 'TUYEN_DUONG', COUNT(*) FROM TUYEN_DUONG
UNION ALL
SELECT 'CHUYEN_XE', COUNT(*) FROM CHUYEN_XE
UNION ALL
SELECT 'BAO_DUONG', COUNT(*) FROM BAO_DUONG;

-- BỔ SUNG CHUYẾN XE MỚI HOÀN THÀNH TRONG THÁNG 11-2025

INSERT INTO CHUYEN_XE (
    MaChuyen,
    MaXe,
    MaTaiXe,
    MaPhuXe,
    MaTuyenDuong,
    SoKhach,
    ThoiGianKhoiHanh,
    SoKmThucTe,
    GiaVe,
    TrangThai
)
VALUES

-- ------------------------------------------------------------
-- ĐỢT 1: GIỮA THÁNG (12/11 - 15/11/2025)
-- ------------------------------------------------------------

-- Chuyến 19: Tài xế 2 lái, tài xế 1 làm phụ xe.
-- Tuyến 3 - Độ phức tạp 2.
(19, 1, 2, 1, 3, 40, '2025-11-12 06:00:00',
 305.00, 250000, 'Đã hoàn thành'),

-- Chuyến 20: Tài xế 4 lái, tài xế 3 làm phụ xe.
-- Tuyến 4 - Độ phức tạp 3.
(20, 2, 4, 3, 4, 25, '2025-11-14 05:30:00',
 295.00, 300000, 'Đã hoàn thành'),

-- Chuyến 21: Tài xế 6 lái, tài xế 5 làm phụ xe.
-- Tuyến 1 - Độ phức tạp 1.
(21, 3, 6, 5, 1, 12, '2025-11-15 08:00:00',
 120.00, 150000, 'Đã hoàn thành'),


-- ------------------------------------------------------------
-- ĐỢT 2: GIỮA CUỐI THÁNG (17/11 - 19/11/2025)
-- ------------------------------------------------------------

-- Chuyến 22: Tài xế 8 lái, tài xế 7 làm phụ xe.
-- Tuyến 6 - Độ phức tạp 3.
(22, 4, 8, 7, 6, 41, '2025-11-17 06:00:00',
 300.00, 350000, 'Đã hoàn thành'),

-- Chuyến 23: Tài xế 1 tiếp tục lái, tài xế 3 làm phụ xe.
-- Tuyến 6 - Độ phức tạp 3.
(23, 1, 1, 3, 6, 43, '2025-11-19 05:00:00',
 308.00, 350000, 'Đã hoàn thành'),


-- ------------------------------------------------------------
-- ĐỢT 3: CUỐI THÁNG (21/11 - 28/11/2025)
-- ------------------------------------------------------------

-- Chuyến 24: Tài xế 2 lái, tài xế 4 làm phụ xe.
-- Tuyến 5 - Độ phức tạp 2.
(24, 2, 2, 4, 5, 26, '2025-11-21 07:00:00',
 185.00, 200000, 'Đã hoàn thành'),

-- Chuyến 25: Tài xế 9 lái, tài xế 3 làm phụ xe.
-- Tuyến 4 - Độ phức tạp 3.
(25, 5, 9, 3, 4, 22, '2025-11-23 05:30:00',
 290.00, 300000, 'Đã hoàn thành'),

-- Chuyến 26: Tài xế 10 lái, tài xế 1 làm phụ xe.
-- Tuyến 2 - Độ phức tạp 2.
(26, 6, 10, 1, 2, 14, '2025-11-25 06:30:00',
 160.00, 180000, 'Đã hoàn thành'),

-- Chuyến 27: Tài xế 4 lái, tài xế 2 làm phụ xe.
-- Tuyến 1 - Độ phức tạp 1.
(27, 1, 4, 2, 1, 39, '2025-11-28 07:00:00',
 122.00, 150000, 'Đã hoàn thành');


-- ============================================================
-- KIỂM TRA DỮ LIỆU VỪA BỔ SUNG
-- ============================================================

SELECT
    CX.MaChuyen,
    XE.BienSo,
    TX1.HoTen AS TaiXe,
    TX2.HoTen AS PhuXe,
    TD.TenTuyenDuong,
    TD.DoPhucTap,
    CX.SoKhach,
    CX.ThoiGianKhoiHanh,
    CX.SoKmThucTe,
    CX.GiaVe,
    CX.TrangThai,
    CX.SoKhach * CX.GiaVe AS DoanhThu
FROM CHUYEN_XE CX
JOIN XE ON CX.MaXe = XE.MaXe
JOIN TAI_XE TX1 ON CX.MaTaiXe = TX1.MaTaiXe
JOIN TAI_XE TX2 ON CX.MaPhuXe = TX2.MaTaiXe
JOIN TUYEN_DUONG TD
    ON CX.MaTuyenDuong = TD.MaTuyenDuong
WHERE CX.MaChuyen BETWEEN 19 AND 27
ORDER BY CX.ThoiGianKhoiHanh;