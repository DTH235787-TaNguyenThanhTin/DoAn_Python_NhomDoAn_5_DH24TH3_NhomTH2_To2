import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime
# --- Import CSDL ---
from db_connect import connect_db
import mysql.connector

def create_view(parent_tab, chitietdonthuoc_data, donthuoc_data, thuoc_data, benhnhan_data, nhanvien_data):
    #
    #Tạo giao diện cho tab Chi Tiết Đơn Thuốc (Master-Detail).
    #
    
    # --- Biến nội bộ ---
    current_mode_detail = None 
    selected_detail_pk = None  
    current_master_madt = None 
    
    # --- Hàm Helper (Hàm trợ giúp) ---
    def find_item_by_key(data_list, key, value):
        #Tìm một dict (item) trong list dựa vào key và value.
        for item in data_list:
            if item.get(key) == value:
                return item
        return None # Trả về None nếu không tìm thấy

    # (Các hàm get_ma_from_display, find_display_by_ma... đã được xóa vì không cần thiết nữa)

    # --- Các hàm xử lý (nội bộ) ---
    def refresh_tree(filter_madt):
        #
        #Làm mới Treeview (bảng chi tiết).
        #CHỈ hiển thị các chi tiết (thuốc) thuộc về filter_madt (Mã Đơn Thuốc).
        #
        # Xóa tất cả các hàng cũ
        for item in tree.get_children():
            tree.delete(item)
        
        # Lọc danh sách chitietdonthuoc_data (cache)
        filtered_details = [item for item in chitietdonthuoc_data if item['MaDT'] == filter_madt]
        
        # Thêm lại các hàng đã lọc
        for item in filtered_details:
            # Tìm Tên Thuốc từ Mã Thuốc
            thuoc_item = find_item_by_key(thuoc_data, 'MaThuoc', item['MaThuoc'])
            ten_thuoc = thuoc_item['TenThuoc'] if thuoc_item else "Không rõ"
            
            # Định dạng ngày
            ngay_kham_display = item['NgayKhamBenh'].strftime('%Y-%m-%d') if isinstance(item['NgayKhamBenh'], datetime.date) else item['NgayKhamBenh']
            ngay_tai_kham_display = item['NgayTaiKham'].strftime('%Y-%m-%d') if isinstance(item['NgayTaiKham'], datetime.date) else item['NgayTaiKham']

            # Chèn vào Treeview
            # PK (iid) là 1 chuỗi kết hợp "MaDT_MaThuoc" để đảm bảo duy nhất
            tree.insert("", tk.END, iid=f"{item['MaDT']}_{item['MaThuoc']}", values=(
                item['MaThuoc'], 
                ten_thuoc, 
                item['SoLuong'], 
                item['HuongDanUong'],
                ngay_kham_display,
                ngay_tai_kham_display
            ))
            
    def update_master_comboboxes():
        #Cập nhật combobox Mã Đơn Thuốc (master).
        # Tải danh sách MaDT từ cache
        dt_display_list = [f"{dt['MaDT']}" for dt in donthuoc_data]
        combo_madt.config(values=dt_display_list)
        
    def update_detail_comboboxes():
        #Cập nhật 2 combobox Mã Thuốc và Tên Thuốc (detail).
        # === THAY ĐỔI: Chỉ tải Mã Thuốc ===
        thuoc_display_list = [t['MaThuoc'] for t in thuoc_data]
        combo_mathuoc.config(values=thuoc_display_list)
        # ==================================
        
        # === THAY ĐỔI: Chỉ tải Tên Thuốc ===
        tenthuoc_display_list = [t['TenThuoc'] for t in thuoc_data]
        combo_tenthuoc.config(values=tenthuoc_display_list)
        # ===================================

    # --- Quản lý trạng thái Form ---
    
    def set_master_form_state(state):
        #Bật/tắt các ô thông tin chung (BN, NV). state là 'normal' hoặc 'disabled'.
        entry_ngaycho.config(state=state)
        entry_manv.config(state=state)
        entry_tennv.config(state=state)
        entry_mabn.config(state=state)
        entry_tenbn.config(state=state)
        entry_diachi.config(state=state)
        entry_sdt.config(state=state)
        
    def set_detail_form_state(state):
        #Bật/tắt form chi tiết (thêm thuốc). state là 'add', 'edit', 'normal', 'disabled'.
        pk_state = 'disabled' # Trạng thái cho 2 combo Mã/Tên thuốc
        other_state = 'disabled' # Trạng thái cho các ô còn lại

        if state == 'add':
            # Khi thêm, cho phép chọn (readonly) Mã/Tên
            pk_state = 'readonly' 
            other_state = 'normal'
        elif state == 'edit':
            # Khi sửa, khóa Mã/Tên (vì là khóa chính)
            pk_state = 'disabled' 
            other_state = 'normal'
        elif state == 'normal': 
            # Trạng thái 'normal' (dùng khi clear form)
            pk_state = 'normal'
            other_state = 'normal'
            
        # Áp dụng
        combo_mathuoc.config(state=pk_state)
        combo_tenthuoc.config(state=pk_state) 
        entry_soluong.config(state=other_state)
        entry_huongdan.config(state=other_state)
        cal_ngaykham.config(state='normal' if other_state == 'normal' else 'disabled')
        cal_ngaytaikham.config(state='normal' if other_state == 'normal' else 'disabled')

    def set_detail_button_state(state):
        #Bật/tắt 6 nút Thêm, Sửa, Lưu... (của form chi tiết).
        btn_them.config(state='normal' if state == 'idle' else 'disabled')
        btn_sua.config(state='normal' if state == 'selected' else 'disabled')
        btn_luu.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        btn_xoa.config(state='normal' if state == 'selected' else 'disabled')
        btn_boqua.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        
    def clear_master_form():
        #Xóa trắng form thông tin chung (master).
        set_master_form_state('normal') # Mở khóa để xóa
        entry_ngaycho.delete(0, tk.END)
        entry_manv.delete(0, tk.END)
        entry_tennv.delete(0, tk.END)
        entry_mabn.delete(0, tk.END)
        entry_tenbn.delete(0, tk.END)
        entry_diachi.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        
    def clear_detail_form():
        #Xóa trắng form chi tiết thuốc (hàm Bỏ qua).
        nonlocal current_mode_detail, selected_detail_pk
        # Reset biến trạng thái
        current_mode_detail = None
        selected_detail_pk = None
        
        # Mở khóa tạm thời để xóa
        set_detail_form_state('normal') 
        combo_mathuoc.set("")
        combo_tenthuoc.set("")
        entry_soluong.delete(0, tk.END)
        entry_huongdan.delete(0, tk.END)
        cal_ngaykham.set_date(datetime.date.today())
        cal_ngaytaikham.set_date(datetime.date.today())
        
        # Khóa lại form chi tiết
        set_detail_form_state('disabled') 
        # Đặt lại trạng thái nút (nếu master đang được chọn thì 'idle', nếu không thì 'disabled')
        set_detail_button_state('idle' if current_master_madt else 'disabled') 
        
        # Bỏ chọn hàng trên Treeview
        if tree.selection():
            tree.selection_remove(tree.selection())

    # --- CÁC HÀM NÚT BẤM CHÍNH ---
    
    def on_xem_donthuoc():
        #
        # Nút "Xem Đơn Thuốc".
        # Tải thông tin Master (BN, NV, Ngày) lên Form 1.
        # Lọc và tải Treeview (Detail List) theo Mã ĐT đã chọn.
        #
        nonlocal current_master_madt
        madt = combo_madt.get() # Lấy MaDT từ combobox master
        if not madt:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một Mã Đơn Thuốc.")
            return

        # Tìm đơn thuốc trong cache donthuoc_data
        donthuoc_item = find_item_by_key(donthuoc_data, 'MaDT', madt)
        if not donthuoc_item:
            messagebox.showerror("Lỗi", "Không tìm thấy đơn thuốc này.")
            return
            
        # Lưu lại MaDT đang xem
        current_master_madt = madt 
        
        # 1. Tải thông tin đơn thuốc (Ngày lập)
        clear_master_form() # Mở khóa và xóa form master
        
        ngay_lap_display = donthuoc_item['NgayLap'].strftime('%Y-%m-%d') if isinstance(donthuoc_item['NgayLap'], datetime.date) else donthuoc_item['NgayLap']
        entry_ngaycho.insert(0, ngay_lap_display)

        # 2. Tải thông tin nhân viên (người lập đơn)
        nhanvien_item = find_item_by_key(nhanvien_data, 'MaNV', donthuoc_item['MaNV'])
        if nhanvien_item:
            entry_manv.insert(0, nhanvien_item['MaNV'])
            entry_tennv.insert(0, nhanvien_item['HoTenNV'])

        # 3. Tải thông tin bệnh nhân
        benhnhan_item = find_item_by_key(benhnhan_data, 'MaBN', donthuoc_item['MaBN'])
        if benhnhan_item:
            entry_mabn.insert(0, benhnhan_item['MaBN'])
            entry_tenbn.insert(0, benhnhan_item['HoTenBN'])
            entry_diachi.insert(0, benhnhan_item['DiaChiBN'])
            entry_sdt.insert(0, benhnhan_item['SDTBN'])
            
        # Khóa lại form master SAU KHI đã điền
        set_master_form_state('disabled') 
        
        # 4. Tải chi tiết (Treeview)
        refresh_tree(current_master_madt)
        
        # 5. Kích hoạt các nút chi tiết
        clear_detail_form() # Xóa form chi tiết (nếu có)
        set_detail_button_state('idle') # Bật nút "Thêm" của form chi tiết
    
    # --- CÁC HÀM NÚT BẤM (CHI TIẾT) ---
    def on_add_detail():
        #Nút 'Thêm' (chi tiết) - Kích hoạt chế độ thêm thuốc vào đơn."""
        nonlocal current_mode_detail
        # Phải chọn "Xem Đơn Thuốc" trước
        if not current_master_madt:
            messagebox.showwarning("Lỗi", "Vui lòng 'Xem Đơn Thuốc' trước khi thêm thuốc.")
            return
        
        clear_detail_form() # Xóa form chi tiết
        current_mode_detail = 'add' # Đặt chế độ 'thêm'
        set_detail_form_state('add') # Mở khóa form chi tiết (cho phép chọn Mã Thuốc)
        set_detail_button_state('add') # Bật nút 'Lưu', 'Bỏ qua'
        combo_mathuoc.focus() # Di chuyển con trỏ vào combo Mã Thuốc

    def on_edit_detail():
        #Nút 'Sửa' (chi tiết) - Kích hoạt chế độ sửa thuốc trong đơn."""
        nonlocal current_mode_detail
        # Phải chọn 1 dòng thuốc trong Treeview trước
        if not selected_detail_pk:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một dòng thuốc trong bảng để sửa.")
            return
        
        current_mode_detail = 'edit' # Đặt chế độ 'sửa'
        set_detail_form_state('edit') # Mở khóa form (nhưng khóa Mã/Tên thuốc)
        set_detail_button_state('edit') # Bật nút 'Lưu', 'Bỏ qua'
        entry_soluong.focus() # Di chuyển con trỏ vào ô Số Lượng

    def on_save_detail():
        #Nút 'Lưu' (chi tiết) - Lưu thuốc (thêm mới hoặc cập nhật)."""
        nonlocal current_mode_detail, selected_detail_pk, current_master_madt
        
        # === THAY ĐỔI: Lấy trực tiếp Mã Thuốc từ combobox ===
        ma_thuoc = combo_mathuoc.get().strip()
        if not ma_thuoc:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Mã Thuốc.")
            return
        # ====================================================
            
        try:
            # Lấy Số Lượng (phải là số)
            so_luong = int(entry_soluong.get().strip())
        except ValueError:
            messagebox.showerror("Lỗi Nhập liệu", "Số lượng phải là một con số.")
            return
            
        # Lấy các thông tin còn lại
        huong_dan = entry_huongdan.get().strip() or None # 'or None' để lưu NULL nếu rỗng
        ngay_kham = cal_ngaykham.get_date()
        ngay_tai_kham = cal_ngaytaikham.get_date()
        
        try:
            # 1. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()
            
            # 2. Xử lý logic Thêm
            if current_mode_detail == 'add':
                # Kiểm tra khóa chính (MaDT, MaThuoc) đã tồn tại chưa
                if any(item['MaDT'] == current_master_madt and item['MaThuoc'] == ma_thuoc for item in chitietdonthuoc_data):
                    messagebox.showerror("Lỗi", "Thuốc này đã tồn tại trong đơn. Vui lòng Sửa số lượng.")
                    conn.close()
                    return

                # 2a. Thêm vào CSDL
                sql = """
                    INSERT INTO chitietdonthuoc (MaDT, MaThuoc, SoLuong, HuongDanUong, NgayKhamBenh, NgayTaiKham)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (current_master_madt, ma_thuoc, so_luong, huong_dan, ngay_kham, ngay_tai_kham))
                
                # 2b. Thêm vào cache
                new_item = {
                    'MaDT': current_master_madt, 'MaThuoc': ma_thuoc, 'SoLuong': so_luong,
                    'HuongDanUong': huong_dan, 'NgayKhamBenh': ngay_kham, 'NgayTaiKham': ngay_tai_kham
                }
                chitietdonthuoc_data.append(new_item)
                messagebox.showinfo("Thành công", f"Đã thêm thuốc {ma_thuoc} vào đơn {current_master_madt}.")

            # 3. Xử lý logic Sửa
            elif current_mode_detail == 'edit':
                # 3a. Cập nhật CSDL
                sql = """
                    UPDATE chitietdonthuoc SET
                    SoLuong = %s, HuongDanUong = %s, NgayKhamBenh = %s, NgayTaiKham = %s
                    WHERE MaDT = %s AND MaThuoc = %s
                """
                # (Dùng PK đã lưu trong selected_detail_pk)
                cursor.execute(sql, (so_luong, huong_dan, ngay_kham, ngay_tai_kham, 
                                     selected_detail_pk['madt'], selected_detail_pk['mathuoc']))
                
                # 3b. Cập nhật cache
                for item in chitietdonthuoc_data:
                    if item['MaDT'] == selected_detail_pk['madt'] and item['MaThuoc'] == selected_detail_pk['mathuoc']:
                        item['SoLuong'] = so_luong
                        item['HuongDanUong'] = huong_dan
                        item['NgayKhamBenh'] = ngay_kham
                        item['NgayTaiKham'] = ngay_tai_kham
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật thuốc {selected_detail_pk['mathuoc']}.")
            
            # 4. Lưu CSDL
            conn.commit()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu chi tiết đơn thuốc:\n{e}")
        finally:
            # 5. Luôn đóng CSDL
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
            
        # 6. Cập nhật giao diện
        refresh_tree(current_master_madt)
        clear_detail_form()

    def on_delete_detail():
        #Nút 'Xóa' (chi tiết) - Xóa thuốc khỏi đơn."""
        # Phải chọn 1 dòng thuốc
        if not selected_detail_pk:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dòng thuốc trong bảng để Xóa.")
            return
        
        # Lấy PK từ biến đã lưu
        madt_del = selected_detail_pk['madt']
        mathuoc_del = selected_detail_pk['mathuoc']

        # Xác nhận
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Thuốc {mathuoc_del} khỏi đơn {madt_del}?"):
            return
            
        try:
            # 1. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()
            
            # 2. Xóa khỏi CSDL
            sql_delete = "DELETE FROM chitietdonthuoc WHERE MaDT = %s AND MaThuoc = %s"
            cursor.execute(sql_delete, (madt_del, mathuoc_del))
            conn.commit()
            
            # 3. Xóa khỏi cache
            item_to_remove = None
            for item in chitietdonthuoc_data:
                if item['MaDT'] == madt_del and item['MaThuoc'] == mathuoc_del:
                    item_to_remove = item
                    break
            if item_to_remove:
                chitietdonthuoc_data.remove(item_to_remove)
                
            messagebox.showinfo("Thành công", "Đã xóa chi tiết thuốc.")
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            # 4. Luôn đóng CSDL
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                
        # 5. Cập nhật giao diện
        refresh_tree(current_master_madt)
        clear_detail_form()
        
    def on_thuoc_select(event):
        #Sự kiện khi chọn 1 mục trong COMBO MÃ THUỐC."""
        # === THAY ĐỔI: Lấy Mã Thuốc trực tiếp ===
        ma_thuoc = combo_mathuoc.get()
        if not ma_thuoc:
            combo_tenthuoc.set("")
            return
        # =======================================
            
        # Tìm Thuốc trong cache
        thuoc_item = find_item_by_key(thuoc_data, 'MaThuoc', ma_thuoc)
        
        # === THAY ĐỔI: Tự động điền Tên Thuốc (chỉ Tên) ===
        if thuoc_item:
            combo_tenthuoc.set(thuoc_item['TenThuoc'])
        else:
            combo_tenthuoc.set("")
        # ===============================================

    def on_ten_thuoc_select(event):
        #Sự kiện khi chọn 1 mục trong COMBO TÊN THUỐC."""
        # === THAY ĐỔI: Lấy Tên Thuốc trực tiếp ===
        ten_thuoc = combo_tenthuoc.get()
        if not ten_thuoc:
            combo_mathuoc.set("")
            return
        # =======================================
        
        # Tìm Thuốc trong cache
        thuoc_item = find_item_by_key(thuoc_data, 'TenThuoc', ten_thuoc)
        
        # === THAY ĐỔI: Tự động điền Mã Thuốc (chỉ Mã) ===
        if thuoc_item:
            combo_mathuoc.set(thuoc_item['MaThuoc'])
        else:
            combo_mathuoc.set("")
        # ==============================================

    def on_detail_item_select(event):
        #Sự kiện khi click vào 1 dòng thuốc trong Treeview (bảng chi tiết)."""
        nonlocal selected_detail_pk
        
        selected_items = tree.selection()
        if not selected_items:
            # Nếu click ra ngoài (bỏ chọn)
            clear_detail_form()
            # Bật lại nút 'Thêm' nếu master đang được chọn
            set_detail_button_state('idle' if current_master_madt else 'disabled') 
            return
        
        # 1. Lấy PK (MaDT_MaThuoc)
        item_id_str = selected_items[0]
        madt_sel, mathuoc_sel = item_id_str.split('_')
        # Lưu PK vào biến
        selected_detail_pk = {'madt': madt_sel, 'mathuoc': mathuoc_sel}
        
        # 2. Tìm item đầy đủ trong cache chitietdonthuoc_data
        item_data_dict = None
        for item in chitietdonthuoc_data:
            if item['MaDT'] == madt_sel and item['MaThuoc'] == mathuoc_sel:
                item_data_dict = item
                break
        
        if not item_data_dict: return

        # 3. Nạp dữ liệu lên form chi tiết
        set_detail_form_state('normal') # Mở khóa tạm thời để nạp
        
        # === THAY ĐỔI: Đồng bộ cả 2 ComboBox (chỉ Mã và chỉ Tên) ===
        thuoc_item = find_item_by_key(thuoc_data, 'MaThuoc', item_data_dict['MaThuoc'])
        if thuoc_item:
            # Nạp Mã
            combo_mathuoc.set(thuoc_item['MaThuoc'])
            # Nạp Tên
            combo_tenthuoc.set(thuoc_item['TenThuoc'])
        else:
            # Nếu không tìm thấy thuốc (đã bị xóa?)
            combo_mathuoc.set(item_data_dict['MaThuoc']) # Hiển thị Mã cũ
            combo_tenthuoc.set("Không tìm thấy")
        # ==========================================================
        
        # Nạp các ô còn lại
        entry_soluong.delete(0, tk.END)
        entry_huongdan.delete(0, tk.END)
        entry_soluong.insert(0, item_data_dict['SoLuong'])
        entry_huongdan.insert(0, item_data_dict['HuongDanUong'] or "")
        
        # Xử lý nạp ngày
        ngay_kham = item_data_dict['NgayKhamBenh']
        if isinstance(ngay_kham, (datetime.date, datetime.datetime)):
            cal_ngaykham.set_date(ngay_kham)
        
        ngay_tai_kham = item_data_dict['NgayTaiKham']
        if isinstance(ngay_tai_kham, (datetime.date, datetime.datetime)):
            cal_ngaytaikham.set_date(ngay_tai_kham)
        
        # 4. Khóa form
        set_detail_form_state('disabled') 
        # 5. Bật nút 'Sửa', 'Xóa'
        set_detail_button_state('selected') 

    # --- GIAO DIỆN ---
    
    # --- Frame 1: Thông tin chung (Master) ---
    master_frame = ttk.LabelFrame(parent_tab, text="Thông tin chung")
    master_frame.pack(fill="x", expand=False, padx=10, pady=10)
    
    
    ttk.Label(master_frame, text="Mã Đơn Thuốc:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_madt = ttk.Combobox(master_frame, width=15, state="readonly") 
    combo_madt.grid(row=0, column=1, padx=5, pady=5)
    
    btn_xem_dt = ttk.Button(master_frame, text="Xem Đơn Thuốc", command=on_xem_donthuoc)
    btn_xem_dt.grid(row=0, column=2, padx=5, pady=5)
    
    
    # Các ô thông tin (bị động, chỉ để xem)
    ttk.Label(master_frame, text="Ngày Cho Thuốc:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_ngaycho = ttk.Entry(master_frame, width=18)
    entry_ngaycho.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(master_frame, text="Mã Nhân Viên:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_manv = ttk.Entry(master_frame, width=18)
    entry_manv.grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(master_frame, text="Tên Nhân Viên:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_tennv = ttk.Entry(master_frame, width=18)
    entry_tennv.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(master_frame, text="Mã Bệnh Nhân:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    entry_mabn = ttk.Entry(master_frame, width=30)
    entry_mabn.grid(row=1, column=3, padx=5, pady=5)

    ttk.Label(master_frame, text="Tên Bệnh Nhân:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
    entry_tenbn = ttk.Entry(master_frame, width=30)
    entry_tenbn.grid(row=2, column=3, padx=5, pady=5)

    ttk.Label(master_frame, text="Địa chỉ:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
    entry_diachi = ttk.Entry(master_frame, width=30)
    entry_diachi.grid(row=3, column=3, padx=5, pady=5)

    ttk.Label(master_frame, text="Điện Thoại:").grid(row=4, column=2, padx=5, pady=5, sticky="w")
    entry_sdt = ttk.Entry(master_frame, width=30)
    entry_sdt.grid(row=4, column=3, padx=5, pady=5)

    # --- Frame 2: Thông tin Đơn Thuốc (Detail Form) ---
    detail_form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Đơn Thuốc")
    detail_form_frame.pack(fill="x", expand=False, padx=10, pady=10)
    
    ttk.Label(detail_form_frame, text="Mã Thuốc:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_mathuoc = ttk.Combobox(detail_form_frame, width=28, state="readonly")
    combo_mathuoc.grid(row=0, column=1, padx=5, pady=5)
    # Gán sự kiện khi chọn Mã Thuốc
    combo_mathuoc.bind("<<ComboboxSelected>>", on_thuoc_select)
    
    ttk.Label(detail_form_frame, text="Tên Thuốc:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    combo_tenthuoc = ttk.Combobox(detail_form_frame, width=28, state="readonly")
    combo_tenthuoc.grid(row=0, column=3, padx=5, pady=5)
    # Gán sự kiện khi chọn Tên Thuốc
    combo_tenthuoc.bind("<<ComboboxSelected>>", on_ten_thuoc_select)
    
    ttk.Label(detail_form_frame, text="Số Lượng:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_soluong = ttk.Entry(detail_form_frame, width=30)
    entry_soluong.grid(row=1, column=1, padx=5, pady=5)
    
    ttk.Label(detail_form_frame, text="Hướng Dẫn Uống:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    entry_huongdan = ttk.Entry(detail_form_frame, width=30)
    entry_huongdan.grid(row=1, column=3, padx=5, pady=5)
    
    ttk.Label(detail_form_frame, text="Ngày Khám Bệnh:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    cal_ngaykham = DateEntry(detail_form_frame, width=28, date_pattern='yyyy-mm-dd')
    cal_ngaykham.grid(row=2, column=1, padx=5, pady=5)
    
    ttk.Label(detail_form_frame, text="Ngày Tái Khám:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
    cal_ngaytaikham = DateEntry(detail_form_frame, width=28, date_pattern='yyyy-mm-dd')
    cal_ngaytaikham.grid(row=2, column=3, padx=5, pady=5)

    # --- Frame 3: Treeview (Detail List) ---
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    # Các cột trong bảng chi tiết
    tree_cols = ("MaThuoc", "TenThuoc", "SoLuong", "HuongDan", "NgayKham", "NgayTaiKham")
    tree = ttk.Treeview(
        tree_frame, columns=tree_cols, show="headings",
        yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Đặt tiêu đề
    tree.heading("MaThuoc", text="Mã Thuốc")
    tree.heading("TenThuoc", text="Tên Thuốc")
    tree.heading("SoLuong", text="Số Lượng")
    tree.heading("HuongDan", text="Hướng Dẫn")
    tree.heading("NgayKham", text="Ngày Khám")
    tree.heading("NgayTaiKham", text="Ngày Tái Khám")
    
    # Đặt độ rộng
    tree.column("MaThuoc", width=80)
    tree.column("TenThuoc", width=150)
    tree.column("SoLuong", width=60)
    tree.column("HuongDan", width=200)
    tree.column("NgayKham", width=100)
    tree.column("NgayTaiKham", width=100)

    tree.pack(fill="both", expand=True)
    # Gán sự kiện khi click chọn 1 dòng
    tree.bind("<<TreeviewSelect>>", on_detail_item_select)
    
    # --- Frame 4: Nút bấm (Detail Buttons) ---
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    # (Các nút này chỉ điều khiển form chi tiết)
    btn_them = ttk.Button(button_frame, text="Thêm", command=on_add_detail)
    btn_them.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_sua = ttk.Button(button_frame, text="Sửa", command=on_edit_detail)
    btn_sua.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_luu = ttk.Button(button_frame, text="Lưu", command=on_save_detail)
    btn_luu.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_xoa = ttk.Button(button_frame, text="Xóa", command=on_delete_detail)
    btn_xoa.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_boqua = ttk.Button(button_frame, text="Bỏ qua", command=clear_detail_form)
    btn_boqua.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_thoat = ttk.Button(button_frame, text="Thoát", command=parent_tab.winfo_toplevel().destroy)
    btn_thoat.pack(side=tk.LEFT, padx=5, expand=True)

    # --- Khởi tạo khi mở tab ---
    # 1. Tải dữ liệu vào các combobox
    update_master_comboboxes() # Tải Mã ĐT
    update_detail_comboboxes() # Tải Mã Thuốc / Tên Thuốc
    
    # 2. Xóa và khóa form master
    clear_master_form()
    set_master_form_state('disabled') 
    
    # 3. Xóa và khóa form chi tiết và các nút
    clear_detail_form() 
    # (Hàm clear_detail_form đã tự khóa form và nút)