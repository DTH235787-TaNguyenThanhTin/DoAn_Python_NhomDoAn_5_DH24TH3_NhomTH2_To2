-- Xóa database cũ nếu tồn tại
DROP DATABASE IF EXISTS quanlybenhnhan;

-- Tạo database với bộ ký tự chuẩn (rất tốt, nên giữ lại)
CREATE DATABASE quanlybenhnhan 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE quanlybenhnhan;

-- Bảng Bệnh Nhân
CREATE TABLE benhnhan (
    MaBN VARCHAR(10) NOT NULL PRIMARY KEY,
    HoTenBN NVARCHAR(50) NOT NULL,
    GioiTinhBN NVARCHAR(10) NOT NULL,
    TuoiBN INT NOT NULL,
    SDTBN VARCHAR(10) NOT NULL, -- Giữ VARCHAR cho SĐT vì nó không phải chữ viết
    NgaySinh DATE NOT NULL,
    DiaChiBN NVARCHAR(100) NOT NULL,
    MaBenh VARCHAR(10) NULL
);

-- Bảng Mã Bệnh
CREATE TABLE macbenh (
    MaBenh VARCHAR(10) NOT NULL PRIMARY KEY,
    LoaiBenh NVARCHAR(50) NULL
);

-- Bảng Chức Vụ
CREATE TABLE chucvu (
    MaCV VARCHAR(10) NOT NULL PRIMARY KEY,
    TenCV NVARCHAR(100) NULL
);

-- Bảng Khoa
CREATE TABLE khoa (
    MaKhoa VARCHAR(10) NOT NULL PRIMARY KEY,
    TenKhoa NVARCHAR(100) NULL
);

-- Bảng Nhân Viên
CREATE TABLE nhanvien (
    MaNV VARCHAR(10) NOT NULL PRIMARY KEY,
    HoTenNV NVARCHAR(100) NULL,
    TuoiNV INT NULL,
    GioiTinhNV NVARCHAR(10) NULL,
    SDTNV VARCHAR(10) NULL, -- Giữ VARCHAR cho SĐT
    MaKhoa VARCHAR(10) NULL,
    MaCV VARCHAR(10) NULL,
    CONSTRAINT FK_NhanVien_ChucVu FOREIGN KEY (MaCV) REFERENCES chucvu(MaCV),
    CONSTRAINT FK_NhanVien_Khoa FOREIGN KEY (MaKhoa) REFERENCES khoa(MaKhoa)
);

-- Bảng Thuốc
CREATE TABLE thuoc (
    MaThuoc VARCHAR(10) NOT NULL PRIMARY KEY,
    TenThuoc NVARCHAR(100) NULL,
    DonViTinh NVARCHAR(50) NULL
);

-- Bảng Đơn Thuốc
CREATE TABLE donthuoc (
    MaDT VARCHAR(10) NOT NULL PRIMARY KEY,
    MaBN VARCHAR(10) NOT NULL,
    MaNV VARCHAR(10) NOT NULL,
    NgayLap DATE NOT NULL DEFAULT (CURRENT_DATE),
    GhiChu NVARCHAR(255) NULL,
    CONSTRAINT FK_DonThuoc_BenhNhan FOREIGN KEY (MaBN) REFERENCES benhnhan(MaBN),
    CONSTRAINT FK_DonThuoc_NhanVien FOREIGN KEY (MaNV) REFERENCES nhanvien(MaNV)
);

-- Bảng Chi Tiết Đơn Thuốc
CREATE TABLE chitietdonthuoc (
    MaDT VARCHAR(10) NOT NULL,
    MaThuoc VARCHAR(10) NOT NULL,
    SoLuong INT NOT NULL,
    HuongDanUong NVARCHAR(200) NULL,
    NgayKhamBenh DATE NULL,
    NgayTaiKham DATE NULL,
    PRIMARY KEY (MaDT, MaThuoc),
    CONSTRAINT FK_CTDT_DonThuoc FOREIGN KEY (MaDT) REFERENCES donthuoc(MaDT) ON DELETE CASCADE,
    CONSTRAINT FK_CTDT_Thuoc FOREIGN KEY (MaThuoc) REFERENCES thuoc(MaThuoc)
);

-- Thêm khóa ngoại cho Bệnh Nhân - Mã Bệnh
ALTER TABLE benhnhan
ADD CONSTRAINT FK_BenhNhan_MacBenh FOREIGN KEY (MaBenh) REFERENCES macbenh(MaBenh);
CREATE TABLE chitietbenhnhan (
    MaCTBN INT NOT NULL PRIMARY KEY AUTO_INCREMENT, -- Khóa chính tự tăng (Được code Python dùng)
    MaBN VARCHAR(10) NOT NULL,
    MaBenh VARCHAR(10) NOT NULL,
    MaNV VARCHAR(10) NOT NULL, -- Bác sĩ/Nhân viên khám (Được code Python dùng)
    NgayKham DATE NOT NULL,
    ChanDoan NVARCHAR(255) NULL,
    KetQua NVARCHAR(255) NULL,
    
    -- Khóa ngoại liên kết với Bệnh nhân
    CONSTRAINT FK_CTBN_BenhNhan FOREIGN KEY (MaBN) REFERENCES benhnhan(MaBN) ON DELETE CASCADE,
    -- Khóa ngoại liên kết với Mã Bệnh
    CONSTRAINT FK_CTBN_MacBenh FOREIGN KEY (MaBenh) REFERENCES macbenh(MaBenh),
    -- Khóa ngoại liên kết với Bác sĩ (Nhân viên)
    CONSTRAINT FK_CTBN_NhanVien FOREIGN KEY (MaNV) REFERENCES nhanvien(MaNV)
);