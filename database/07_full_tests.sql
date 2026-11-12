-- 07_full_tests.sql | MySQL 8.0 | RUN AFTER 01,02,03,04,05
-- Tat ca du lieu test duoc ROLLBACK. Bang tam MEMORY luu ket qua.
-- CHU Y: test phu thuoc test 05a; neu 05a FAIL, ket qua test phu thuoc khong dang tin.
-- Chi chay tren CSDL test/backup, khong chay tren production.
USE QL_VAN_TAI;

-- Xoa ket qua kiem thu cu
DROP TEMPORARY TABLE IF EXISTS ket_qua_test;

-- Tao lai bang ket qua moi
CREATE TEMPORARY TABLE ket_qua_test (
    STT INT AUTO_INCREMENT PRIMARY KEY,
    TenTest VARCHAR(120),
    MongDoi VARCHAR(12),
    ThucTe VARCHAR(12),
    KetQua VARCHAR(8),
    Loi VARCHAR(255)
) ENGINE=MEMORY;

DROP PROCEDURE IF EXISTS test_expect;

DELIMITER //

CREATE PROCEDURE test_expect(
    IN p_ten VARCHAR(120),
    IN p_sql TEXT,
    IN p_expect_error BOOLEAN
)
BEGIN
    DECLARE v_error BOOLEAN DEFAULT FALSE;
    DECLARE v_msg VARCHAR(255) DEFAULT '';
    DECLARE v_errno INT DEFAULT 0;

    BEGIN
        DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
        BEGIN
            SET v_error = TRUE;

            GET STACKED DIAGNOSTICS CONDITION 1
                v_errno = MYSQL_ERRNO,
                v_msg = MESSAGE_TEXT;
        END;

        SET @test_sql = p_sql;

        PREPARE stmt FROM @test_sql;

        IF NOT v_error THEN
            EXECUTE stmt;
            DEALLOCATE PREPARE stmt;
        END IF;
    END;

    INSERT INTO ket_qua_test (
        TenTest,
        MongDoi,
        ThucTe,
        KetQua,
        Loi
    )
    VALUES (
        p_ten,

        IF(
            p_expect_error,
            'LOI',
            'THANH CONG'
        ),

        IF(
            v_error,
            'LOI',
            'THANH CONG'
        ),

        IF(
            v_error = p_expect_error
            AND (
                NOT p_expect_error
                OR v_errno IN (1644, 3819)
            ),
            'PASS',
            'FAIL'
        ),

        IF(
            v_error,
            CONCAT('Err ', v_errno, ': ', v_msg),
            ''
        )
    );

END //

DELIMITER ;
START TRANSACTION;
-- Dung ma tu tang qua bien session, fixture khong phu thuoc ID cu
INSERT INTO XE(BienSo,MauSac,HangSanXuat,DoiXe,Model,NamSanXuat,SoChoNgoi,TrangThai)
VALUES('ZZ-TEST-01','Trắng','TEST','TEST','TEST',2024,45,TRUE);
SET @xe = LAST_INSERT_ID();
INSERT INTO XE(BienSo,MauSac,HangSanXuat,DoiXe,Model,NamSanXuat,SoChoNgoi,TrangThai)
VALUES('ZZ-TEST-02','Trắng','TEST','TEST','TEST',2024,45,FALSE);
SET @xe_nghi = LAST_INSERT_ID();
INSERT INTO XE(BienSo,MauSac,HangSanXuat,DoiXe,Model,NamSanXuat,SoChoNgoi,TrangThai) VALUES('ZZ-TEST-03','Trắng','TEST','TEST','TEST',2024,45,TRUE); SET @xe_khac=LAST_INSERT_ID();
INSERT INTO TAI_XE(HoTen,SoCCCD,SoBangLai,LoaiBangLai,DiaChi,NgaySinh,NgayVaoNghe,SDT,Email,TrangThai) VALUES ('TEST A','ZZCCCD01','ZZBL01','E','TEST','1990-01-01','2015-01-01','09911110001','zztest01@example.com','Đang làm việc');
SET @a = LAST_INSERT_ID();
INSERT INTO TAI_XE(HoTen,SoCCCD,SoBangLai,LoaiBangLai,DiaChi,NgaySinh,NgayVaoNghe,SDT,Email,TrangThai) VALUES ('TEST B','ZZCCCD02','ZZBL02','E','TEST','1990-01-01','2015-01-01','09911110002','zztest02@example.com','Đang làm việc');
SET @b = LAST_INSERT_ID();
INSERT INTO TAI_XE(HoTen,SoCCCD,SoBangLai,LoaiBangLai,DiaChi,NgaySinh,NgayVaoNghe,SDT,Email,TrangThai) VALUES ('TEST C','ZZCCCD03','ZZBL03','E','TEST','1990-01-01','2015-01-01','09911110003','zztest03@example.com','Đang làm việc');
SET @c = LAST_INSERT_ID();
INSERT INTO TAI_XE(HoTen,SoCCCD,SoBangLai,LoaiBangLai,DiaChi,NgaySinh,NgayVaoNghe,SDT,Email,TrangThai) VALUES ('TEST NGHI','ZZCCCD04','ZZBL04','E','TEST','1990-01-01','2015-01-01','09911110004','zztest04@example.com','Đã nghỉ việc');
SET @nghi = LAST_INSERT_ID();
INSERT INTO TUYEN_DUONG(TenTuyenDuong,DiemDi,DiemDen,ChieuDai,DoPhucTap,ThoiGianDi,TrangThai)
VALUES('ZZ TEST TUYEN','TEST A','TEST B',100,1,2,TRUE);
SET @tuyen=LAST_INSERT_ID();
-- Prepared dynamic SQL: values interpolated from controlled test fixture IDs.
SET @base = CONCAT('INSERT INTO CHUYEN_XE(MaXe,MaTaiXe,MaPhuXe,MaTuyenDuong,SoKhach,ThoiGianKhoiHanh,SoKmThucTe,GiaVe,TrangThai) VALUES (');
CALL test_expect('01 vuot suc chua',CONCAT(@base,@xe,',',@a,',',@b,',',@tuyen,",44,'2027-03-01 06:00:00',0,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('02 tai xe trung phu xe',CONCAT(@base,@xe,',',@a,',',@a,',',@tuyen,",10,'2027-03-01 06:00:00',0,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('03 xe ngung hoat dong',CONCAT(@base,@xe_nghi,',',@a,',',@b,',',@tuyen,",10,'2027-03-01 06:00:00',0,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('04 nhan vien nghi viec',CONCAT(@base,@xe,',',@nghi,',',@b,',',@tuyen,",10,'2027-03-01 06:00:00',0,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('05a chuyen hop le',CONCAT(@base,@xe,',',@a,',',@b,',',@tuyen,",10,'2027-03-01 06:00:00',0,100000,'Đã lên lịch')"),FALSE);
-- Lay MaChuyen tu fixture, khong dung LAST_INSERT_ID() sau CALL
SET @chuyen = (SELECT MaChuyen FROM CHUYEN_XE WHERE MaXe=@xe AND MaTaiXe=@a AND MaPhuXe=@b AND ThoiGianKhoiHanh='2027-03-01 06:00:00' ORDER BY MaChuyen DESC LIMIT 1);
CALL test_expect('05b trung lich xe',CONCAT(@base,@xe,',',@b,',',@c,',',@tuyen,",10,'2027-03-01 06:30:00',0,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('05c trung lich nhan vien',CONCAT(@base,@xe_khac,',',@a,',',@c,',',@tuyen,",10,'2027-03-01 06:30:00',0,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('06 bao duong trung chuyen',CONCAT('INSERT INTO BAO_DUONG(MaXe,ThoiGianBaoDuong,NoiDung,ChiPhi,TrangThai) VALUES(',@xe,",'2027-03-01 07:00:00','TEST',1000,'Đang bảo dưỡng')"),TRUE);
CALL test_expect('07 chuyen hoan thanh km=0',CONCAT(@base,@xe,',',@a,',',@b,',',@tuyen,",10,'2027-03-02 06:00:00',0,100000,'Đã hoàn thành')"),TRUE);
CALL test_expect('08 km am',CONCAT(@base,@xe,',',@a,',',@b,',',@tuyen,",10,'2027-03-02 06:00:00',-1,100000,'Đã lên lịch')"),TRUE);
CALL test_expect('09 gia ve <=0',CONCAT(@base,@xe,',',@a,',',@b,',',@tuyen,",10,'2027-03-02 06:00:00',0,0,'Đã lên lịch')"),TRUE);
CALL test_expect('10 ngung xe dang duoc phan cong',CONCAT('UPDATE XE SET TrangThai=FALSE WHERE MaXe=',@xe),TRUE);
CALL test_expect('11 nhan vien nghi khi con chuyen',CONCAT("UPDATE TAI_XE SET TrangThai='Đã nghỉ việc' WHERE MaTaiXe=",@a),TRUE);
CALL test_expect('12 giam so cho duoi so khach',CONCAT('UPDATE XE SET SoChoNgoi=10 WHERE MaXe=',@xe),TRUE);
CALL test_expect('13 doi chuyen sang km duong',CONCAT("UPDATE CHUYEN_XE SET TrangThai='Đã hoàn thành',SoKmThucTe=100 WHERE MaChuyen=",@chuyen),FALSE);
CALL test_expect('14 bao duong sau chuyen hoan thanh',CONCAT('INSERT INTO BAO_DUONG(MaXe,ThoiGianBaoDuong,NoiDung,ChiPhi,TrangThai) VALUES(',@xe,",'2027-03-01 09:00:00','TEST',1000,'Đang bảo dưỡng')"),FALSE);
CALL test_expect('15 khong phan cong khi dang bao duong',CONCAT(@base,@xe,',',@a,',',@b,',',@tuyen,",10,'2027-03-03 06:00:00',0,100000,'Đã lên lịch')"),TRUE);
ROLLBACK;
SELECT * FROM ket_qua_test ORDER BY STT;
SELECT COUNT(*) AS TongTest,SUM(KetQua='PASS') AS PASS,SUM(KetQua='FAIL') AS FAIL FROM ket_qua_test;
DROP PROCEDURE IF EXISTS test_expect;
