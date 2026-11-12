-- BTL CSDL PROJECT 5 Hoàng Huy Đại B24DCCN090
-- Hệ thống quản lí vận tải hành khách
-- File: 01_create_database.sql : tạo cơ sở dữ liệu và các bảng dữ liệu


-- 1. Tạo database
CREATE DATABASE IF NOT EXISTS QL_VAN_TAI
CHARACTER SET utf8mb4
COLLATE utf8mb4_general_ci;

-- 2. Sử dụng database
USE QL_VAN_TAI;


-- 3. Kiểm tra database
SHOW DATABASES;

-- 4. Kiểm tra database dang sử dụng
SELECT DATABASE();