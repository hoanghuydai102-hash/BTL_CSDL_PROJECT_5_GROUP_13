-- File: 06_test.sql
-- Mục đích: kiểm thử tổng thể DATABASE

USE QL_VAN_TAI;

-- TEST 1: KIỂM TRA SỐ LƯỢNG BẢN GHI

SELECT 'XE' AS TenBang, COUNT(*) AS SoLuong FROM XE
UNION ALL
SELECT 'TAI_XE', COUNT(*) FROM TAI_XE
UNION ALL
SELECT 'TUYEN_DUONG', COUNT(*) FROM TUYEN_DUONG
UNION ALL
SELECT 'CHUYEN_XE', COUNT(*) FROM CHUYEN_XE
UNION ALL
SELECT 'BAO_DUONG', COUNT(*) FROM BAO_DUONG;

-- TEST 2: KIỂM TRA SỐ KHÁCH KHÔNG VƯỢT QUA SỨC CHỨA


SELECT
    CX.MaChuyen,XE.BienSo,CX.SoKhach,XE.SoChoNgoi,XE.SoChoNgoi - 2 AS SoKhachToiDa
FROM CHUYEN_XE CX
JOIN XE ON CX.MaXe = XE.MaXe
WHERE CX.SoKhach > XE.SoChoNgoi - 2;

-- TEST 3: KIỂM TRA TÀI XẾ VÀ PHỤ XE KHÔNG TRÙNG NHAU

SELECT MaChuyen, MaTaiXe, MaPhuXe
FROM CHUYEN_XE
WHERE MaTaiXe=MaPhuXe;

-- TEST 4: KIẺM TRA CHUYẾN HOÀN TOÀN PHẢI CÓ KM>=0
SELECT MaChuyen, SoKmThucTe, TrangThai
FROM CHUYEN_XE
WHERE TrangThai = 'Đã hoàn thành' AND SoKmThucTe <= 0;

-- TEST 5: KIỂM TRA CHUYẾN XE CÓ DỮ LIỆU HỢP LỆ

SELECT CX.MaChuyen, XE.BienSo, TX1.HoTen AS TaiXe, TX2.HoTen AS PhuXe, TD.TenTuyenDuong, CX.SoKhach, CX.GiaVe, CX.TrangThai
FROM CHUYEN_XE CX
JOIN XE ON CX.MaXe = XE.MaXe
JOIN TAI_XE TX1 ON CX.MaTaiXe = TX1.MaTaiXe
JOIN TAI_XE TX2 ON CX.MaPhuXe = TX2.MaTaiXe
JOIN TUYEN_DUONG TD ON CX.MaTuyenDuong = TD.MaTuyenDuong
ORDER BY CX.MaChuyen;

-- TEST 7: KIỂM TRA VIEW LỊCH BẢO DƯỠNG

SELECT *
FROM vw_lich_bao_duong
ORDER BY NgayBaoDuongTiepTheo;

-- TEST 8: KIỂM TRA DOANH THU THÁNG 11/2025

SELECT
    XE.BienSo,
    COUNT(CX.MaChuyen) AS SoChuyen,
    SUM(CX.SoKhach) AS TongSoKhach,
    SUM(CX.SoKhach * CX.GiaVe) AS DoanhThu
FROM XE
JOIN CHUYEN_XE CX
    ON XE.MaXe = CX.MaXe
WHERE CX.TrangThai = 'Đã hoàn thành'
  AND CX.ThoiGianKhoiHanh >= '2025-11-01'
  AND CX.ThoiGianKhoiHanh < '2025-12-01'
GROUP BY XE.MaXe, XE.BienSo
ORDER BY DoanhThu DESC;
