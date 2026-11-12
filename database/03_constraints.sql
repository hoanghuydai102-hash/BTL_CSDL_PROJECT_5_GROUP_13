-- File: 03_constraints.sql
-- THIẾT LẬP RÀNG BUỘC NGHIỆP VỤ

USE QL_VAN_TAI;

-- 0. XÓA CÁC TRIGGER CŨ NẾU CÓ

DROP TRIGGER IF EXISTS trg_check_so_khach_insert;
DROP TRIGGER IF EXISTS trg_check_so_khach_update;

DROP TRIGGER IF EXISTS trg_check_so_km_insert;
DROP TRIGGER IF EXISTS trg_check_so_km_update;
DROP TRIGGER IF EXISTS trg_check_sokm_insert;
DROP TRIGGER IF EXISTS trg_check_sokm_update;

DROP TRIGGER IF EXISTS trg_check_xe_insert;
DROP TRIGGER IF EXISTS trg_check_xe_update;

DROP TRIGGER IF EXISTS trg_check_taixe_insert;
DROP TRIGGER IF EXISTS trg_check_taixe_update;

DROP TRIGGER IF EXISTS trg_check_nhanvien_insert;
DROP TRIGGER IF EXISTS trg_check_nhanvien_update;

DROP TRIGGER IF EXISTS trg_kiemtra_chuyen_insert;
DROP TRIGGER IF EXISTS trg_kiemtra_chuyen_update;
DROP TRIGGER IF EXISTS trg_kiemtra_xe_update;

DROP TRIGGER IF EXISTS trg_kiemtra_taixe_update;

DROP TRIGGER IF EXISTS trg_kiemtra_baoduong_insert;
DROP TRIGGER IF EXISTS trg_kiemtra_baoduong_update;

-- 1. KIỂM TRA CÁC RÀNG BUỘC KHI THÊM CHUYẾN XE

DELIMITER //

CREATE TRIGGER trg_kiemtra_chuyen_insert
BEFORE INSERT ON CHUYEN_XE
FOR EACH ROW
BEGIN
    DECLARE v_so_cho INT;
    DECLARE v_trang_thai_xe BOOLEAN;
    DECLARE v_trang_thai_lai VARCHAR(30);
    DECLARE v_trang_thai_phu VARCHAR(30);
    DECLARE v_thoi_gian_di DECIMAL(5,2);
    DECLARE v_so_lan_bao_duong INT DEFAULT 0;
    DECLARE v_so_lan_trung_lich INT DEFAULT 0;

    -- 1.1. KIỂM TRA SỐ KHÁCH

    SELECT SoChoNgoi, TrangThai
    INTO v_so_cho, v_trang_thai_xe
    FROM XE
    WHERE MaXe = NEW.MaXe;

    IF NEW.SoKhach > v_so_cho - 2 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số khách vượt quá sức chứa cho phép của xe.';
    END IF;

    -- 1.2. KIỂM TRA SỐ KM THỰC TẾ

    IF NEW.SoKmThucTe < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số km thực tế không được âm.';
    END IF;

    IF NEW.TrangThai = 'Đã hoàn thành'
       AND NEW.SoKmThucTe <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Chuyến xe đã hoàn thành phải có số km thực tế lớn hơn 0.';
    END IF;

    -- 1.3. KIỂM TRA TRẠNG THÁI XE

    IF NEW.TrangThai IN ('Đã lên lịch', 'Đang chạy') THEN

        IF v_trang_thai_xe = FALSE THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Xe đang ngừng hoạt động, không thể phân công.';
        END IF;

        -- 1.4. KIỂM TRA XE ĐANG BẢO DƯỠNG

        SELECT COUNT(*)
        INTO v_so_lan_bao_duong
        FROM BAO_DUONG
        WHERE MaXe = NEW.MaXe
          AND TrangThai = 'Đang bảo dưỡng';

        IF v_so_lan_bao_duong > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Xe đang trong quá trình bảo dưỡng, không thể phân công.';
        END IF;

        -- 1.5. KIỂM TRA TRẠNG THÁI TÀI XẾ VÀ PHỤ XE

        SELECT TrangThai
        INTO v_trang_thai_lai
        FROM TAI_XE
        WHERE MaTaiXe = NEW.MaTaiXe;

        SELECT TrangThai
        INTO v_trang_thai_phu
        FROM TAI_XE
        WHERE MaTaiXe = NEW.MaPhuXe;

        IF v_trang_thai_lai <> 'Đang làm việc'
           OR v_trang_thai_phu <> 'Đang làm việc' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tài xế hoặc phụ xe không ở trạng thái làm việc.';
        END IF;

        -- 1.6. KIỂM TRA TÀI XẾ VÀ PHỤ XE KHÔNG TRÙNG NHAU

        IF NEW.MaTaiXe = NEW.MaPhuXe THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tài xế và phụ xe phải là hai người khác nhau.';
        END IF;

        -- 1.7. LẤY THỜI GIAN DI CHUYỂN CỦA TUYẾN

        SELECT ThoiGianDi
        INTO v_thoi_gian_di
        FROM TUYEN_DUONG
        WHERE MaTuyenDuong = NEW.MaTuyenDuong;

        IF (SELECT TrangThai FROM TUYEN_DUONG WHERE MaTuyenDuong = NEW.MaTuyenDuong) = FALSE THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tuyến đường đã ngừng hoạt động.';
        END IF;

        -- 1.8. KIỂM TRA TRÙNG LỊCH XE

        SELECT COUNT(*)
        INTO v_so_lan_trung_lich
        FROM CHUYEN_XE CX
        JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong
        WHERE CX.MaXe = NEW.MaXe
          AND CX.TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND CX.ThoiGianKhoiHanh <
              TIMESTAMPADD(
                  MINUTE,
                  ROUND(v_thoi_gian_di * 60),
                  NEW.ThoiGianKhoiHanh
              )
          AND TIMESTAMPADD(
                  MINUTE,
                  ROUND(TD.ThoiGianDi * 60),
                  CX.ThoiGianKhoiHanh
              ) > NEW.ThoiGianKhoiHanh;

        IF v_so_lan_trung_lich > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Xe đã có chuyến khác bị trùng lịch.';
        END IF;

        -- 1.9. KIỂM TRA TRÙNG LỊCH TÀI XẾ VÀ PHỤ XE

        SELECT COUNT(*)
        INTO v_so_lan_trung_lich
        FROM CHUYEN_XE CX
        JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong
        WHERE (
                CX.MaTaiXe IN (NEW.MaTaiXe, NEW.MaPhuXe)
                OR CX.MaPhuXe IN (NEW.MaTaiXe, NEW.MaPhuXe)
              )
          AND CX.TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND CX.ThoiGianKhoiHanh <
              TIMESTAMPADD(
                  MINUTE,
                  ROUND(v_thoi_gian_di * 60),
                  NEW.ThoiGianKhoiHanh
              )
          AND TIMESTAMPADD(
                  MINUTE,
                  ROUND(TD.ThoiGianDi * 60),
                  CX.ThoiGianKhoiHanh
              ) > NEW.ThoiGianKhoiHanh;

        IF v_so_lan_trung_lich > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tài xế hoặc phụ xe đã tham gia một chuyến khác bị trùng lịch.';
        END IF;

    END IF;

END //

DELIMITER ;

-- 2. KIỂM TRA CÁC RÀNG BUỘC KHI CẬP NHẬT CHUYẾN XE

DELIMITER //

CREATE TRIGGER trg_kiemtra_chuyen_update
BEFORE UPDATE ON CHUYEN_XE
FOR EACH ROW
BEGIN
    DECLARE v_so_cho INT;
    DECLARE v_trang_thai_xe BOOLEAN;
    DECLARE v_trang_thai_lai VARCHAR(30);
    DECLARE v_trang_thai_phu VARCHAR(30);
    DECLARE v_thoi_gian_di DECIMAL(5,2);
    DECLARE v_so_lan_bao_duong INT DEFAULT 0;
    DECLARE v_so_lan_trung_lich INT DEFAULT 0;

    -- 2.1. KIỂM TRA SỐ KHÁCH

    SELECT SoChoNgoi, TrangThai
    INTO v_so_cho, v_trang_thai_xe
    FROM XE
    WHERE MaXe = NEW.MaXe;

    IF NEW.SoKhach > v_so_cho - 2 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số khách vượt quá sức chứa cho phép của xe.';
    END IF;

    -- 2.2. KIỂM TRA SỐ KM THỰC TẾ

    IF NEW.SoKmThucTe < 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Số km thực tế không được âm.';
    END IF;

    IF NEW.TrangThai = 'Đã hoàn thành'
       AND NEW.SoKmThucTe <= 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Chuyến xe đã hoàn thành phải có số km thực tế lớn hơn 0.';
    END IF;

    -- 2.3. KIỂM TRA CÁC ĐIỀU KIỆN PHÂN CÔNG

    IF NEW.TrangThai IN ('Đã lên lịch', 'Đang chạy') THEN

        IF v_trang_thai_xe = FALSE THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Xe đang ngừng hoạt động, không thể phân công.';
        END IF;

        -- 2.4. KIỂM TRA XE ĐANG BẢO DƯỠNG

        SELECT COUNT(*)
        INTO v_so_lan_bao_duong
        FROM BAO_DUONG
        WHERE MaXe = NEW.MaXe
          AND TrangThai = 'Đang bảo dưỡng';

        IF v_so_lan_bao_duong > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Xe đang trong quá trình bảo dưỡng, không thể phân công.';
        END IF;

        -- 2.5. KIỂM TRA TRẠNG THÁI TÀI XẾ VÀ PHỤ XE

        SELECT TrangThai
        INTO v_trang_thai_lai
        FROM TAI_XE
        WHERE MaTaiXe = NEW.MaTaiXe;

        SELECT TrangThai
        INTO v_trang_thai_phu
        FROM TAI_XE
        WHERE MaTaiXe = NEW.MaPhuXe;

        IF v_trang_thai_lai <> 'Đang làm việc'
           OR v_trang_thai_phu <> 'Đang làm việc' THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tài xế hoặc phụ xe không ở trạng thái làm việc.';
        END IF;

        -- 2.6. KIỂM TRA TÀI XẾ VÀ PHỤ XE KHÔNG TRÙNG NHAU

        IF NEW.MaTaiXe = NEW.MaPhuXe THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tài xế và phụ xe phải là hai người khác nhau.';
        END IF;

        -- 2.7. LẤY THỜI GIAN DI CHUYỂN CỦA TUYẾN

        SELECT ThoiGianDi
        INTO v_thoi_gian_di
        FROM TUYEN_DUONG
        WHERE MaTuyenDuong = NEW.MaTuyenDuong;

        IF (SELECT TrangThai FROM TUYEN_DUONG WHERE MaTuyenDuong = NEW.MaTuyenDuong) = FALSE THEN
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tuyến đường đã ngừng hoạt động.';
        END IF;

        -- 2.8. KIỂM TRA TRÙNG LỊCH XE

        SELECT COUNT(*)
        INTO v_so_lan_trung_lich
        FROM CHUYEN_XE CX
        JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong
        WHERE CX.MaXe = NEW.MaXe
          AND CX.MaChuyen <> OLD.MaChuyen
          AND CX.TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND CX.ThoiGianKhoiHanh <
              TIMESTAMPADD(
                  MINUTE,
                  ROUND(v_thoi_gian_di * 60),
                  NEW.ThoiGianKhoiHanh
              )
          AND TIMESTAMPADD(
                  MINUTE,
                  ROUND(TD.ThoiGianDi * 60),
                  CX.ThoiGianKhoiHanh
              ) > NEW.ThoiGianKhoiHanh;

        IF v_so_lan_trung_lich > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Xe đã có chuyến khác bị trùng lịch.';
        END IF;

        -- 2.9. KIỂM TRA TRÙNG LỊCH TÀI XẾ VÀ PHỤ XE

        SELECT COUNT(*)
        INTO v_so_lan_trung_lich
        FROM CHUYEN_XE CX
        JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong
        WHERE (
                CX.MaTaiXe IN (NEW.MaTaiXe, NEW.MaPhuXe)
                OR CX.MaPhuXe IN (NEW.MaTaiXe, NEW.MaPhuXe)
              )
          AND CX.MaChuyen <> OLD.MaChuyen
          AND CX.TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND CX.ThoiGianKhoiHanh <
              TIMESTAMPADD(
                  MINUTE,
                  ROUND(v_thoi_gian_di * 60),
                  NEW.ThoiGianKhoiHanh
              )
          AND TIMESTAMPADD(
                  MINUTE,
                  ROUND(TD.ThoiGianDi * 60),
                  CX.ThoiGianKhoiHanh
              ) > NEW.ThoiGianKhoiHanh;

        IF v_so_lan_trung_lich > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Tài xế hoặc phụ xe đã tham gia một chuyến khác bị trùng lịch.';
        END IF;

    END IF;

END //

DELIMITER ;

-- 3. KIỂM TRA CÁC RÀNG BUỘC KHI CẬP NHẬT XE

DELIMITER //

CREATE TRIGGER trg_kiemtra_xe_update
BEFORE UPDATE ON XE
FOR EACH ROW
BEGIN
    DECLARE v_so_chuyen INT DEFAULT 0;

    -- 3.1. KIỂM TRA SỨC CHỨA KHI GIẢM SỐ CHỖ NGỒI

    IF NEW.SoChoNgoi < OLD.SoChoNgoi THEN

        SELECT COUNT(*)
        INTO v_so_chuyen
        FROM CHUYEN_XE
        WHERE MaXe = OLD.MaXe
          AND TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND SoKhach > NEW.SoChoNgoi - 2;

        IF v_so_chuyen > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Không thể giảm số chỗ vì xe đang có chuyến vượt quá sức chứa mới.';
        END IF;

    END IF;

    -- 3.2. KIỂM TRA KHI NGỪNG HOẠT ĐỘNG XE

    IF NEW.TrangThai = FALSE AND OLD.TrangThai = TRUE THEN

        SELECT COUNT(*)
        INTO v_so_chuyen
        FROM CHUYEN_XE
        WHERE MaXe = OLD.MaXe
          AND TrangThai IN ('Đã lên lịch', 'Đang chạy');

        IF v_so_chuyen > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Không thể ngừng hoạt động xe vì xe vẫn đang được phân công chuyến.';
        END IF;

    END IF;

END //

DELIMITER ;

-- 4. KIỂM TRA CÁC RÀNG BUỘC KHI CẬP NHẬT TÀI XẾ

DELIMITER //

CREATE TRIGGER trg_kiemtra_taixe_update
BEFORE UPDATE ON TAI_XE
FOR EACH ROW
BEGIN
    DECLARE v_so_chuyen INT DEFAULT 0;

    -- Không cho phép ngừng làm việc nếu còn chuyến chưa hoàn thành

    IF NEW.TrangThai <> 'Đang làm việc'
       AND OLD.TrangThai = 'Đang làm việc' THEN

        SELECT COUNT(*)
        INTO v_so_chuyen
        FROM CHUYEN_XE
        WHERE (MaTaiXe = OLD.MaTaiXe OR MaPhuXe = OLD.MaTaiXe)
          AND TrangThai IN ('Đã lên lịch', 'Đang chạy');

        IF v_so_chuyen > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Không thể thay đổi trạng thái nhân viên vì vẫn còn chuyến chưa hoàn thành.';
        END IF;

    END IF;

END //

DELIMITER ;

-- 5. KIỂM TRA KHI THÊM LỊCH BẢO DƯỠNG

DELIMITER //

CREATE TRIGGER trg_kiemtra_baoduong_insert
BEFORE INSERT ON BAO_DUONG
FOR EACH ROW
BEGIN
    DECLARE v_so_chuyen INT DEFAULT 0;

    IF NEW.TrangThai = 'Đang bảo dưỡng' THEN

        SELECT COUNT(*)
        INTO v_so_chuyen
        FROM CHUYEN_XE CX
        JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong
        WHERE CX.MaXe = NEW.MaXe
          AND CX.TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND CX.ThoiGianKhoiHanh <= NEW.ThoiGianBaoDuong
          AND TIMESTAMPADD(
                  MINUTE,
                  ROUND(TD.ThoiGianDi * 60),
                  CX.ThoiGianKhoiHanh
              ) > NEW.ThoiGianBaoDuong;

        IF v_so_chuyen > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Không thể bảo dưỡng vì xe vẫn còn chuyến chưa kết thúc.';
        END IF;

    END IF;

END //

DELIMITER ;

-- 6. KIỂM TRA KHI CẬP NHẬT LỊCH BẢO DƯỠNG

DELIMITER //

CREATE TRIGGER trg_kiemtra_baoduong_update
BEFORE UPDATE ON BAO_DUONG
FOR EACH ROW
BEGIN
    DECLARE v_so_chuyen INT DEFAULT 0;

    IF NEW.TrangThai = 'Đang bảo dưỡng' THEN

        SELECT COUNT(*)
        INTO v_so_chuyen
        FROM CHUYEN_XE CX
        JOIN TUYEN_DUONG TD
            ON CX.MaTuyenDuong = TD.MaTuyenDuong
        WHERE CX.MaXe = NEW.MaXe
          AND CX.TrangThai IN ('Đã lên lịch', 'Đang chạy')
          AND CX.ThoiGianKhoiHanh <= NEW.ThoiGianBaoDuong
          AND TIMESTAMPADD(
                  MINUTE,
                  ROUND(TD.ThoiGianDi * 60),
                  CX.ThoiGianKhoiHanh
              ) > NEW.ThoiGianBaoDuong;

        IF v_so_chuyen > 0 THEN
            SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Không thể cập nhật bảo dưỡng vì xe vẫn còn chuyến chưa kết thúc.';
        END IF;

    END IF;

END //

DELIMITER ;

-- 7. KIỂM TRA CÁC TRIGGER ĐÃ TẠO

SHOW TRIGGERS;

-- 8. KIỂM TRA DANH SÁCH TRIGGER TRONG DATABASE

SELECT
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_TIMING
FROM INFORMATION_SCHEMA.TRIGGERS
WHERE TRIGGER_SCHEMA = 'QL_VAN_TAI'
ORDER BY EVENT_OBJECT_TABLE, TRIGGER_NAME;
-- Khong ngung tuyen khi con chuyen chua ket thuc
DROP TRIGGER IF EXISTS trg_kiemtra_tuyen_update;
DELIMITER //
CREATE TRIGGER trg_kiemtra_tuyen_update BEFORE UPDATE ON TUYEN_DUONG FOR EACH ROW
BEGIN
 IF OLD.TrangThai = TRUE AND NEW.TrangThai = FALSE AND EXISTS (
  SELECT 1 FROM CHUYEN_XE WHERE MaTuyenDuong = OLD.MaTuyenDuong AND TrangThai IN ('Đã lên lịch','Đang chạy')
 ) THEN
  SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Tuyến đường còn chuyến chưa kết thúc.';
 END IF;
END //
DELIMITER ;
