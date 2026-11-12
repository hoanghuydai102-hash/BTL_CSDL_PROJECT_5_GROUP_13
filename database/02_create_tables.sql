-- File: 02_create_tables.sql
-- Tao cac bang du lieu trong QL_VAN_TAI

USE QL_VAN_TAI;

-- 1. TAO BANG XE
CREATE TABLE IF NOT EXISTS XE (
    MaXe INT AUTO_INCREMENT PRIMARY KEY,
    BienSo VARCHAR(15) NOT NULL UNIQUE,
    MauSac VARCHAR(30) NOT NULL,
    HangSanXuat VARCHAR(50) NOT NULL,
    DoiXe VARCHAR(50) NOT NULL,
    Model VARCHAR(50) NOT NULL,
    NamSanXuat YEAR NOT NULL,
    SoChoNgoi INT NOT NULL,
    TrangThai BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_xe_socho 
    CHECK (SoChoNgoi > 2)
) ENGINE=InnoDB;


-- 2. TAO BANG TAI_XE
CREATE TABLE IF NOT EXISTS TAI_XE (
    MaTaiXe INT AUTO_INCREMENT PRIMARY KEY,
    HoTen VARCHAR(100) NOT NULL,
    SoCCCD VARCHAR(20) NOT NULL UNIQUE,
    SoBangLai VARCHAR(20) NOT NULL UNIQUE,
    LoaiBangLai VARCHAR(10) NOT NULL,
    DiaChi VARCHAR(200) NOT NULL,
    NgaySinh DATE NOT NULL,
    NgayVaoNghe DATE NOT NULL,
    SDT VARCHAR(15) NOT NULL UNIQUE,
    Email VARCHAR(100) NOT NULL UNIQUE,
    TrangThai ENUM(
        'Đang làm việc', 
        'Nghỉ phép', 
        'Tạm nghỉ', 
        'Đã nghỉ việc'
    ) NOT NULL DEFAULT 'Đang làm việc',

    CONSTRAINT chk_taixe_ngay 
    CHECK (NgaySinh < NgayVaoNghe)
) ENGINE=InnoDB;


-- 3. TAO BANG TUYEN_DUONG
CREATE TABLE IF NOT EXISTS TUYEN_DUONG (
    MaTuyenDuong INT AUTO_INCREMENT PRIMARY KEY,
    TenTuyenDuong VARCHAR(100) NOT NULL UNIQUE,
    DiemDi VARCHAR(100) NOT NULL,
    DiemDen VARCHAR(100) NOT NULL,
    ChieuDai DECIMAL(10,2) NOT NULL,
    DoPhucTap TINYINT NOT NULL,
    ThoiGianDi DECIMAL(5,2) NOT NULL,
    TrangThai BOOLEAN NOT NULL DEFAULT TRUE,

    CONSTRAINT chk_tuyen_chieudai 
    CHECK (ChieuDai > 0),

    CONSTRAINT chk_tuyen_dophuctap 
    CHECK (DoPhucTap IN (1, 2, 3)),

    CONSTRAINT chk_tuyen_thoigian 
    CHECK (ThoiGianDi > 0),

    CONSTRAINT chk_tuyen_diem 
    CHECK (DiemDi <> DiemDen)
) ENGINE=InnoDB;


-- 4. TAO BANG CHUYEN_XE
CREATE TABLE IF NOT EXISTS CHUYEN_XE (
    MaChuyen INT AUTO_INCREMENT PRIMARY KEY,
    MaXe INT NOT NULL,
    MaTaiXe INT NOT NULL,
    MaPhuXe INT NOT NULL,
    MaTuyenDuong INT NOT NULL,
    SoKhach INT NOT NULL,
    ThoiGianKhoiHanh DATETIME NOT NULL,
    SoKmThucTe DECIMAL(10,2) NOT NULL DEFAULT 0,
    GiaVe DECIMAL(15,2) NOT NULL,
    TrangThai ENUM(
        'Đã lên lịch', 
        'Đang chạy', 
        'Đã hoàn thành', 
        'Đã hủy'
    ) NOT NULL DEFAULT 'Đã lên lịch',

    CONSTRAINT fk_chuyen_xe 
    FOREIGN KEY (MaXe) REFERENCES XE(MaXe) 
    ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_chuyen_tai_xe 
    FOREIGN KEY (MaTaiXe) REFERENCES TAI_XE(MaTaiXe) 
    ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_chuyen_phu_xe 
    FOREIGN KEY (MaPhuXe) REFERENCES TAI_XE(MaTaiXe) 
    ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT fk_chuyen_tuyen 
    FOREIGN KEY (MaTuyenDuong) REFERENCES TUYEN_DUONG(MaTuyenDuong) 
    ON DELETE RESTRICT ON UPDATE CASCADE,

    CONSTRAINT chk_chuyen_sokhach 
    CHECK (SoKhach >= 0),

    CONSTRAINT chk_chuyen_giave 
    CHECK (GiaVe > 0),

    CONSTRAINT chk_chuyen_km 
    CHECK (SoKmThucTe >= 0)
) ENGINE=InnoDB;


-- 5. TAO BANG BAO_DUONG
CREATE TABLE IF NOT EXISTS BAO_DUONG (
    MaBaoDuong INT AUTO_INCREMENT PRIMARY KEY,
    MaXe INT NOT NULL,
    ThoiGianBaoDuong DATETIME NOT NULL,
    NoiDung VARCHAR(200) NOT NULL,
    ChiPhi DECIMAL(15,2) NOT NULL,

    TrangThai ENUM(
        'Đang chờ',
        'Đang bảo dưỡng',
        'Hoàn thành'
    ) NOT NULL DEFAULT 'Đang chờ',

    CONSTRAINT fk_baoduong_xe
        FOREIGN KEY (MaXe)
        REFERENCES XE(MaXe)
        ON DELETE RESTRICT
        ON UPDATE CASCADE,

    CONSTRAINT chk_baoduong_chiphi
        CHECK (ChiPhi >= 0)
) ENGINE=InnoDB;


-- 6. KIEM TRA CAC BANG
SHOW TABLES;