-- Xóa nếu database đã tồn tại
DROP DATABASE IF EXISTS quanlybenhnhan;

-- Tạo lại database
CREATE DATABASE quanlybenhnhan;
USE quanlybenhnhan;


CREATE TABLE benhnhan (
    MaBN VARCHAR(10) PRIMARY KEY,
    HoBN VARCHAR(50),
    TenBN VARCHAR(50),
    GioiTinh VARCHAR(10),
    TuoiBN INT,
    SDTBN INT,
    NgaySinh DATE,
    DiaChi VARCHAR(100)
);

CREATE TABLE macbenh (
    MaBenh VARCHAR(10) PRIMARY KEY,
    LoaiBenh VARCHAR(10)
);
CREATE TABLE dieutri (
    NgayBDDieuTri DATE,
    NgayXuatVien DATE
);
CREATE TABLE BHYT (
    MaBHYT VARCHAR(20) PRIMARY KEY,
    NgayBDBHYT DATE,
    NgayHHBHYT DATE,
    QueQuan VARCHAR(100)
);
CREATE TABLE Khoa (
    MaKhoa VARCHAR(10) PRIMARY KEY,
    TenKhoa VARCHAR(100)
);
CREATE TABLE ChucVu (
    MaCV VARCHAR(10) PRIMARY KEY,
    TenCV VARCHAR(100)
);
CREATE TABLE NhanVien (
    MaNV VARCHAR(10) PRIMARY KEY,
    HoTenNV VARCHAR(100),
    TuoiNV INT,
    GioiTinhNV VARCHAR(10),
    SDTNV VARCHAR(15),
    MaKhoa VARCHAR(10),
    MaCV VARCHAR(10),
    FOREIGN KEY (MaKhoa) REFERENCES Khoa(MaKhoa),
    FOREIGN KEY (MaCV) REFERENCES ChucVu(MaCV)
);
CREATE TABLE DonThuoc (
    MaDT VARCHAR(10) PRIMARY KEY,
    TenDT VARCHAR(100),
    CachSuDung VARCHAR(200),
    DonViTinh VARCHAR(50)
);
CREATE TABLE Thuoc (
    MaThuoc VARCHAR(10) PRIMARY KEY,
    TenThuoc VARCHAR(100)
);
