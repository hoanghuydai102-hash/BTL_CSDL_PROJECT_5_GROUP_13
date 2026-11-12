-- File: 05_queries.sql
-- CÁC TRUY VẤN DỮ LIỆU
USE QL_VAN_TAI;

-- 1. TÍNH LƯƠNG TÀI XẾ VÀ PHỤ XE THEO THÁNG

-- Thay đổi tháng và năm tại đây
SET @Thang = MONTH(CURDATE());
SET @Nam = YEAR(CURDATE());

SET @NgayDau = STR_TO_DATE(
    CONCAT(@Nam, '-', LPAD(@Thang, 2, '0'), '-01'),
    '%Y-%m-%d'
);

SET @NgayCuoi = DATE_ADD(@NgayDau, INTERVAL 1 MONTH);

SELECT
    TX.MaTaiXe,
    TX.HoTen,
    COUNT(PC.MaChuyen) AS SoChuyen,

    SUM(
        CASE
            WHEN PC.VaiTro = 'Tài xế' THEN PC.TienCong
            ELSE 0
        END
    ) AS TienCongTaiXe,

    SUM(
        CASE
            WHEN PC.VaiTro = 'Phụ xe' THEN PC.TienCong
            ELSE 0
        END
    ) AS TienCongPhuXe,

    COALESCE(SUM(PC.TienCong), 0) AS TongLuong

FROM TAI_XE TX

LEFT JOIN (
    -- CÔNG VIỆC TÀI XẾ

    SELECT
        CX.MaTaiXe AS MaTaiXe,
        CX.MaChuyen,
        'Tài xế' AS VaiTro,

        CASE TD.DoPhucTap
            WHEN 1 THEN 400000
            WHEN 2 THEN 600000
            WHEN 3 THEN 800000
        END AS TienCong

    FROM CHUYEN_XE CX

    JOIN TUYEN_DUONG TD
        ON CX.MaTuyenDuong = TD.MaTuyenDuong

    WHERE CX.TrangThai = 'Đã hoàn thành'
      AND CX.ThoiGianKhoiHanh >= @NgayDau
      AND CX.ThoiGianKhoiHanh < LEAST(@NgayCuoi, NOW())

    UNION ALL

    -- CÔNG VIỆC PHỤ XE

    SELECT
        CX.MaPhuXe AS MaTaiXe,
        CX.MaChuyen,
        'Phụ xe' AS VaiTro,

        CASE TD.DoPhucTap
            WHEN 1 THEN 200000
            WHEN 2 THEN 300000
            WHEN 3 THEN 400000
        END AS TienCong

    FROM CHUYEN_XE CX

    JOIN TUYEN_DUONG TD
        ON CX.MaTuyenDuong = TD.MaTuyenDuong

    WHERE CX.TrangThai = 'Đã hoàn thành'
      AND CX.ThoiGianKhoiHanh >= @NgayDau
      AND CX.ThoiGianKhoiHanh < LEAST(@NgayCuoi, NOW())

) PC
    ON TX.MaTaiXe = PC.MaTaiXe

GROUP BY TX.MaTaiXe, TX.HoTen
ORDER BY TongLuong DESC;


-- 2. TÍNH DOANH THU TỪNG XE TRONG KHOẢNG THỜI GIAN
-- Thay đổi ngày bắt đầu và ngày kết thúc
SET @TuNgay = '2025-11-01';
SET @DenNgay = '2025-11-30';

SELECT
    XE.MaXe,
    XE.BienSo,

    COUNT(CX.MaChuyen) AS SoChuyen,

    COALESCE(SUM(CX.SoKhach), 0) AS TongSoKhach,

    COALESCE(SUM(CX.SoKhach * CX.GiaVe), 0) AS TongDoanhThu

FROM XE

LEFT JOIN CHUYEN_XE CX
    ON XE.MaXe = CX.MaXe
    AND CX.TrangThai = 'Đã hoàn thành'
    AND CX.ThoiGianKhoiHanh >= @TuNgay
    AND CX.ThoiGianKhoiHanh < DATE_ADD(@DenNgay, INTERVAL 1 DAY)

GROUP BY XE.MaXe, XE.BienSo
ORDER BY TongDoanhThu DESC;


-- 3. TÍNH LỊCH BẢO DƯỠNG TIẾP THEO CỦA CÁC XE
CREATE OR REPLACE VIEW vw_lich_bao_duong AS

SELECT
    DS.MaXe,
    DS.BienSo,
    DS.LanBaoDuongCuoi,
    DS.TongKmTrongSo,
    DS.SoNgayGiam,
    DS.NgayBaoDuongTiepTheo,

    CASE
        WHEN DS.NgayBaoDuongTiepTheo IS NULL
            THEN 'Chưa có lịch sử bảo dưỡng'

        WHEN DS.NgayBaoDuongTiepTheo < CURDATE()
            THEN 'Quá hạn'

        ELSE 'Chưa đến hạn'
    END AS TrangThaiBaoDuong

FROM (
    SELECT
        XE.MaXe,
        XE.BienSo,

        BD.LanBaoDuongCuoi,

        COALESCE(KM.TongKmTrongSo, 0) AS TongKmTrongSo,

        FLOOR(
            COALESCE(KM.TongKmTrongSo, 0) / 100
        ) AS SoNgayGiam,

        CASE
            WHEN BD.LanBaoDuongCuoi IS NULL THEN NULL

            ELSE DATE_ADD(
                DATE(BD.LanBaoDuongCuoi),
                INTERVAL GREATEST(
                    360 - FLOOR(COALESCE(KM.TongKmTrongSo, 0) / 100),
                    0
                ) DAY
            )
        END AS NgayBaoDuongTiepTheo

    FROM XE

    LEFT JOIN (
        -- LẤY LẦN BẢO DƯỠNG HOÀN THÀNH GẦN NHẤT

        SELECT
            MaXe,
            MAX(ThoiGianBaoDuong) AS LanBaoDuongCuoi

        FROM BAO_DUONG

        WHERE TrangThai = 'Hoàn thành'

        GROUP BY MaXe

    ) BD
        ON XE.MaXe = BD.MaXe

    LEFT JOIN (
        -- TÍNH TỔNG SỐ KM CÓ TRỌNG SỐ SAU LẦN BẢO DƯỠNG GẦN NHẤT

        SELECT
            BD1.MaXe,
            BD1.LanBaoDuongCuoi,

            SUM(
                CX.SoKmThucTe *
                CASE TD.DoPhucTap
                    WHEN 1 THEN 1.0
                    WHEN 2 THEN 1.2
                    WHEN 3 THEN 1.5
                    ELSE 1.0
                END
            ) AS TongKmTrongSo

        FROM (
            SELECT
                MaXe,
                MAX(ThoiGianBaoDuong) AS LanBaoDuongCuoi

            FROM BAO_DUONG

            WHERE TrangThai = 'Hoàn thành'

            GROUP BY MaXe

        ) BD1

        LEFT JOIN CHUYEN_XE CX
            ON BD1.MaXe = CX.MaXe
            AND CX.TrangThai = 'Đã hoàn thành'
            AND CX.ThoiGianKhoiHanh > BD1.LanBaoDuongCuoi

        LEFT JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong

        GROUP BY BD1.MaXe, BD1.LanBaoDuongCuoi

    ) KM
        ON XE.MaXe = KM.MaXe

) DS;


-- HIỂN THỊ LỊCH BẢO DƯỠNG TẤT CẢ XE

SELECT *
FROM vw_lich_bao_duong
ORDER BY NgayBaoDuongTiepTheo;


-- 4. LIỆT KÊ CÁC XE ĐÃ QUÁ HẠN BẢO DƯỠNG

SELECT *
FROM vw_lich_bao_duong
WHERE TrangThaiBaoDuong = 'Quá hạn'
ORDER BY NgayBaoDuongTiepTheo;

-- 5. KIỂM TRA TỔNG SỐ CHUYẾN HOÀN THÀNH CỦA TỪNG XE

SELECT
    XE.MaXe,
    XE.BienSo,
    COUNT(CX.MaChuyen) AS SoChuyenHoanThanh
FROM XE
LEFT JOIN CHUYEN_XE CX
    ON XE.MaXe = CX.MaXe
    AND CX.TrangThai = 'Đã hoàn thành'
GROUP BY XE.MaXe, XE.BienSo
ORDER BY XE.MaXe;

-- 6. KIỂM TRA SỐ KHÁCH CÓ VƯỢT SỨC CHỨA KHÔNG

SELECT
    CX.MaChuyen,
    XE.BienSo,
    XE.SoChoNgoi,
    CX.SoKhach,
    XE.SoChoNgoi - 2 AS SoKhachToiDa,
    CASE
        WHEN CX.SoKhach <= XE.SoChoNgoi - 2 THEN 'Hợp lệ'
        ELSE 'Không hợp lệ'
    END AS KetQua
FROM CHUYEN_XE CX
JOIN XE
    ON CX.MaXe = XE.MaXe;

-- 7. THỐNG KÊ SỐ LƯỢNG BẢN GHI CỦA CÁC BẢNG

SELECT 'XE' AS TenBang, COUNT(*) AS SoLuong FROM XE
UNION ALL
SELECT 'TAI_XE', COUNT(*) FROM TAI_XE
UNION ALL
SELECT 'TUYEN_DUONG', COUNT(*) FROM TUYEN_DUONG
UNION ALL
SELECT 'CHUYEN_XE', COUNT(*) FROM CHUYEN_XE
UNION ALL
SELECT 'BAO_DUONG', COUNT(*) FROM BAO_DUONG;

-- KẾT THÚC FILE