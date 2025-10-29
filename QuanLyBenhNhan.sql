-- Xóa nếu database đã tồn tại
DROP DATABASE IF EXISTS quanlybenhnhan;

-- Tạo lại database
CREATE DATABASE quanlybenhnhan;
USE quanlybenhnhan;

-- Tạo bảng benhnhan
CREATE TABLE benhnhan (
    MaBN VARCHAR(10) PRIMARY KEY,
    HoBN VARCHAR(50),
    TenBN VARCHAR(50),
    GioiTinh VARCHAR(10),
    TuoiBN INT,
    SDTBN INT,
    NgaySinh DATETIME,
    DiaChi VARCHAR(100)
);
CREATE TABLE macbenh(
	MaBenh VARCHAR(10) PRIMARY KEY,
    LoaiBenh VARCHAR(50)
);