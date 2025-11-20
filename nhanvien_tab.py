import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# --- Import CSDL ---
from db_connect import connect_db
import mysql.connector

def create_view(parent_tab, nhanvien_data, khoa_data, chucvu_data):
    #Tạo giao diện cho tab Quản lý Nhân viên. Sử dụng 3 danh sách dữ liệu: nhanvien_data, khoa_data, chucvu_data
    # --- Biến nội bộ ---
    # Biến lưu trạng thái: 'add' (thêm), 'edit' (sửa), or None (bình thường)
    current_mode = None
    # Biến lưu Mã NV (PK) của hàng đang được chọn trong Treeview
    selected_item_id = None
    # Biến True/False của Tkinter, liên kết với checkbox Giới tính
    var_is_male = tk.BooleanVar(value=False) # Mặc định là Nữ (không tích)

    # --- Hàm xử lý ComboBox ----
    def update_comboboxes():
        #Cập nhật danh sách cho 2 combobox Khoa và Chức vụ.
        # Tạo danh sách hiển thị .
        khoa_display_list = [f"{k['MaKhoa']} - {k['TenKhoa']}" for k in khoa_data]
        chucvu_display_list = [f"{c['MaCV']} - {c['TenCV']}" for c in chucvu_data]
        
        # Gán danh sách giá trị cho các combobox
        combo_khoa_nv['values'] = khoa_display_list
        combo_chucvu_nv['values'] = chucvu_display_list
        # (Đã xóa messagebox theo yêu cầu)

    # --- Các hàm xử lý (nội bộ) ---
    def refresh_tree():
        #Làm mới Treeview, tải lại toàn bộ dữ liệu từ nhanvien_data.
        # Xóa tất cả các hàng cũ
        for item in tree.get_children():
            tree.delete(item)
        # Thêm lại dữ liệu từ danh sách local
        for nv in nhanvien_data:
            tree.insert("", tk.END, iid=nv['MaNV'], values=(
                nv['MaNV'], nv['HoTenNV'], nv['TuoiNV'], nv['GioiTinhNV'],
                nv['SDTNV'], nv['MaKhoa'], nv['MaCV']
            ))
            
    def set_form_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các ô nhập liệu.
        # Mặc định, khóa chính (PK) và các trường khác đều bị vô hiệu hóa
        pk_state = 'disabled'
        other_state = 'disabled'

        if state == 'add':
            # Khi thêm, cho phép nhập Mã NV (PK) và các trường khác
            pk_state = 'normal'
            other_state = 'normal'
        elif state == 'edit':
            # Khi sửa, khóa Mã NV, chỉ cho sửa trường khác
            pk_state = 'disabled'
            other_state = 'normal'
        elif state == 'normal':
            # Trạng thái 'normal' (dùng khi clear form) cũng mở khóa
            pk_state = 'normal'
            other_state = 'normal'
        
        # Áp dụng trạng thái cho Entry
        entry_manv.config(state=pk_state)
        entry_hoten_nv.config(state=other_state)
        entry_tuoi.config(state=other_state)
        entry_sdt.config(state=other_state)
        # Áp dụng trạng thái cho Checkbutton
        chk_gioitinh_nam.config(state=other_state)
        
        # Trạng thái cho combobox ('readonly' khi bật, 'disabled' khi tắt)
        combo_state = 'readonly' if other_state == 'normal' else 'disabled'
        combo_khoa_nv.config(state=combo_state)
        combo_chucvu_nv.config(state=combo_state)
        
    def set_button_state(state):
        #Kích hoạt hoặc vô hiệu hóa các nút chức năng tùy theo trạng thái.
        # 'idle': Trạng thái chờ, chỉ 'Thêm' sáng
        # 'selected': Đã chọn 1 hàng, 'Sửa' và 'Xóa' sáng
        # 'add'/'edit': Đang Thêm/Sửa, 'Lưu' và 'Bỏ qua' sáng
        btn_them.config(state='normal' if state == 'idle' else 'disabled')
        btn_sua.config(state='normal' if state == 'selected' else 'disabled')
        btn_luu.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        btn_xoa.config(state='normal' if state == 'selected' else 'disabled')
        btn_boqua.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        # (Đã xóa nút btn_refresh_combos)

    def clear_entries():
        #Xóa trắng các ô nhập liệu và reset trạng thái về 'idle'.
        nonlocal current_mode, selected_item_id
        # Reset biến trạng thái
        current_mode = None
        selected_item_id = None
        
        # Mở khóa tạm thời để xóa nội dung
        set_form_state('normal') 
        
        # Xóa nội dung các ô
        entry_manv.delete(0, tk.END)
        entry_hoten_nv.delete(0, tk.END)
        entry_tuoi.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        var_is_male.set(False) # Reset checkbox về 'Nữ' (không tích)
        combo_khoa_nv.set("") # Xóa combobox
        combo_chucvu_nv.set("")
        
        # Khóa lại các ô
        set_form_state('disabled') 
        # Đặt trạng thái nút về 'idle'
        set_button_state('idle')
        
        # Bỏ chọn hàng trên Treeview
        if tree.selection():
            tree.selection_remove(tree.selection())

    def on_add():
        #Hàm xử lý khi nhấn nút 'Thêm'."""
        nonlocal current_mode
        clear_entries() # Xóa form
        current_mode = 'add' # Đặt chế độ 'thêm'
        set_form_state('add') # Mở khóa form
        set_button_state('add') # Bật nút 'Lưu', 'Bỏ qua'
        entry_manv.focus() # Chuyển con trỏ vào ô Mã NV

    def on_edit():
        #Hàm xử lý khi nhấn nút 'Sửa'."""
        nonlocal current_mode
        # Phải chọn một nhân viên trước
        if not selected_item_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một Nhân viên để sửa.")
            return
        
        current_mode = 'edit' # Đặt chế độ 'sửa'
        set_form_state('edit') # Mở khóa form (trừ Mã NV)
        set_button_state('edit') # Bật nút 'Lưu', 'Bỏ qua'
        entry_hoten_nv.focus() # Chuyển con trỏ vào ô Họ tên

    def get_ma_from_display(display_text):
        #Hàm trợ giúp: Tách Mã từ chuỗi """
        if not display_text: return None # Trả về None nếu rỗng
        return display_text.split(" - ")[0]

    def on_save():
        #Hàm xử lý khi nhấn nút 'Lưu' (cho cả Thêm và Sửa)."""
        nonlocal current_mode, selected_item_id
        
        # 1. Lấy dữ liệu từ Form
        ma_nv = entry_manv.get().strip()
        ho_ten = entry_hoten_nv.get().strip()
        
        # 2. Kiểm tra dữ liệu bắt buộc
        if not ma_nv or not ho_ten:
            messagebox.showwarning("Thiếu thông tin", "Mã NV và Họ Tên là bắt buộc.")
            return

        # 3. Thu thập toàn bộ dữ liệu (kể cả các trường không bắt buộc)
        # Dùng 'or None' để đảm bảo giá trị là NULL nếu ô rỗng
        # Dùng 'if...else' để xử lý tuổi
        try:
            tuoi_value = int(entry_tuoi.get().strip()) if entry_tuoi.get().strip() else None
        except ValueError:
             messagebox.showerror("Lỗi Nhập liệu", "Tuổi NV phải là một con số.")
             return # Thêm return ở đây để dừng hàm on_save khi tuổi sai
            
        
        data_tuple = (
            ho_ten,
            tuoi_value,
            "Nam" if var_is_male.get() else "Nữ", # Lấy từ checkbox
            entry_sdt.get().strip() or None,
            get_ma_from_display(combo_khoa_nv.get()), # Tách mã Khoa
            get_ma_from_display(combo_chucvu_nv.get()), # Tách mã Chức vụ
            ma_nv # MaNV ở cuối cùng cho câu lệnh INSERT hoặc WHERE
        )
        
        # 4. Tạo từ điển (dict) để cập nhật danh sách local (cache)
        new_data_dict = {
            'MaNV': ma_nv,
            'HoTenNV': data_tuple[0],
            'TuoiNV': data_tuple[1],
            'GioiTinhNV': data_tuple[2],
            'SDTNV': data_tuple[3],
            'MaKhoa': data_tuple[4],
            'MaCV': data_tuple[5]
        }

        try:
            # 5. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()

            # 6. Xử lý logic Thêm hoặc Sửa
            if current_mode == 'add':
                # Kiểm tra trùng khóa chính (MaNV)
                if any(item['MaNV'] == ma_nv for item in nhanvien_data):
                    messagebox.showerror("Lỗi", "Mã Nhân viên này đã tồn tại.")
                    conn.close()
                    return
                
                # Câu lệnh SQL INSERT
                sql = """
                    INSERT INTO nhanvien (HoTenNV, TuoiNV, GioiTinhNV, SDTNV, MaKhoa, MaCV, MaNV)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                # Đảo lại thứ tự tuple cho đúng SQL
                sql_tuple = (
                    data_tuple[0], # HoTenNV
                    data_tuple[1], # TuoiNV
                    data_tuple[2], # GioiTinhNV
                    data_tuple[3], # SDTNV
                    data_tuple[4], # MaKhoa
                    data_tuple[5], # MaCV
                    data_tuple[6]  # MaNV
                )
                cursor.execute(sql, sql_tuple)
                
                # Thêm vào danh sách local
                nhanvien_data.append(new_data_dict)
                messagebox.showinfo("Thành công", f"Đã thêm Nhân viên: {ma_nv}")
            
            elif current_mode == 'edit':
                # Câu lệnh SQL UPDATE
                sql = """
                    UPDATE nhanvien SET 
                    HoTenNV = %s, TuoiNV = %s, GioiTinhNV = %s, SDTNV = %s, MaKhoa = %s, MaCV = %s
                    WHERE MaNV = %s
                """
                # Dùng data_tuple vì MaNV đã ở cuối
                cursor.execute(sql, data_tuple)
                
                # Cập nhật lại danh sách local
                for i, item in enumerate(nhanvien_data):
                    if item['MaNV'] == selected_item_id:
                        # Thay thế dict cũ bằng dict mới
                        # Đảm bảo MaNV là đúng (nếu lỡ new_data_dict bị sai)
                        new_data_dict['MaNV'] = selected_item_id
                        nhanvien_data[i] = new_data_dict
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật Nhân viên: {selected_item_id}")

            # 7. Lưu thay đổi
            conn.commit()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu:\n{e}")
        # Bắt lỗi ValueError nếu người dùng nhập chữ vào ô Tuổi
        except ValueError:
            messagebox.showerror("Lỗi Nhập liệu", "Tuổi NV phải là một con số.")
        finally:
            # 8. Đóng kết nối
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
            
        # 9. Cập nhật giao diện
        refresh_tree()
        clear_entries()

    def on_delete():
        #Hàm xử lý khi nhấn nút 'Xóa'."""
        # 1. Kiểm tra đã chọn
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một Nhân viên từ danh sách để Xóa.")
            return
        
        # 2. Xác nhận
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Nhân viên {selected_item_id}?"):
            return

        try:
            # 3. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()
            
            # (Lưu ý: Nếu MaNV là khóa ngoại ở bảng khác, CSDL sẽ báo lỗi)
            # === THÊM: Kiểm tra ràng buộc khóa ngoại (ví dụ: bảng donthuoc) ===
            sql_check = "SELECT COUNT(*) FROM donthuoc WHERE MaNV = %s"
            cursor.execute(sql_check, (selected_item_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                messagebox.showerror("Lỗi", f"Không thể xóa Nhân viên này. Đang có {count} đơn thuốc liên quan.")
                conn.close()
                return
            # ==============================================================

            # 4. Câu lệnh SQL DELETE
            sql_delete = "DELETE FROM nhanvien WHERE MaNV = %s"
            cursor.execute(sql_delete, (selected_item_id,))
            conn.commit()
            
            # 5. Xóa khỏi danh sách local
            item_to_remove = None
            for item in nhanvien_data:
                if item['MaNV'] == selected_item_id:
                    item_to_remove = item
                    break
            if item_to_remove:
                nhanvien_data.remove(item_to_remove)
                
            messagebox.showinfo("Thành công", "Đã xóa Nhân viên.")
            
        except mysql.connector.Error as e:
            # Bắt lỗi (ví dụ: không thể xóa do ràng buộc khóa ngoại khác)
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            # 6. Đóng kết nối
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                    
        # 7. Cập nhật giao diện
        refresh_tree()
        clear_entries()

    def find_display_by_ma(ma, data_list, key_ma, key_ten):
        #Hàm trợ giúp: Tìm chuỗi khi biết Mã ."""
        if not ma: return "" # Thêm kiểm tra nếu ma là None
        for item in data_list:
            if item[key_ma] == ma:
                # Trả về chuỗi "Mã - Tên"
                return f"{item[key_ma]} - {item[key_ten]}"
        return "" # Trả về rỗng nếu không tìm thấy

    def on_item_select(event):
        #Hàm xử lý sự kiện khi người dùng click/chọn một hàng trong Treeview."""
        nonlocal selected_item_id
        
        # Lấy danh sách các mục đang được chọn (thường chỉ là 1)
        selected_items = tree.selection()
        if not selected_items:
            # Nếu người dùng click vào khoảng trống (bỏ chọn), thì xóa form
            # clear_entries() # Tạm khóa dòng này, giữ lại form khi bỏ chọn
            return
        
        # 1. Lấy ID (MaNV) của hàng đã chọn
        item_id = selected_items[0]
        
        # 2. Tìm dữ liệu đầy đủ của hàng đó trong danh sách local
        item_data_dict = None
        for item in nhanvien_data:
            if item['MaNV'] == item_id:
                item_data_dict = item
                break
        
        if not item_data_dict: return # Không tìm thấy (lỗi hiếm gặp)

        # 3. Nạp dữ liệu lên form
        set_form_state('normal') # Mở khóa tạm thời để nạp
        
        # Xóa dữ liệu cũ
        entry_manv.delete(0, tk.END)
        entry_hoten_nv.delete(0, tk.END)
        entry_tuoi.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)

        # Nạp dữ liệu mới
        entry_manv.insert(0, item_data_dict['MaNV'])
        entry_hoten_nv.insert(0, item_data_dict['HoTenNV'])
        
        # Xử lý nếu TuoiNV/SDTNV là None (NULL), nạp vào chuỗi rỗng
        entry_tuoi.insert(0, item_data_dict['TuoiNV'] or "")
        entry_sdt.insert(0, item_data_dict['SDTNV'] or "")
        
        # Đặt checkbox: .set(True) nếu là "Nam", ngược lại .set(False)
        var_is_male.set(item_data_dict['GioiTinhNV'] == "Nam")
            
        # Tìm chuỗi hiển thị cho combobox từ Mã Khoa và Mã CV
        khoa_display = find_display_by_ma(item_data_dict['MaKhoa'], khoa_data, 'MaKhoa', 'TenKhoa')
        cv_display = find_display_by_ma(item_data_dict['MaCV'], chucvu_data, 'MaCV', 'TenCV')
        
        # Đặt giá trị cho combobox
        combo_khoa_nv.set(khoa_display)
        combo_chucvu_nv.set(cv_display)
        
        # 4. Lưu lại ID đã chọn
        selected_item_id = item_data_dict['MaNV']
        
        # 5. Khóa form lại
        set_form_state('disabled') 
        # 6. Bật nút 'Sửa', 'Xóa'
        set_button_state('selected') 

    # --- Tạo Form Nhập liệu (UI) ---
    # Tạo một khung (LabelFrame) bao bọc các ô nhập liệu
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Nhân viên")
    form_frame.pack(fill="x", expand=False, padx=10, pady=10) # fill="x" co giãn theo chiều ngang

    # (Grid các entry... giống như cũ)
    # sticky="w" (west) để căn lề trái
    ttk.Label(form_frame, text="Mã NV:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_manv = ttk.Entry(form_frame, width=40)
    entry_manv.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Họ tên:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_hoten_nv = ttk.Entry(form_frame, width=40)
    entry_hoten_nv.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Tuổi:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_tuoi = ttk.Entry(form_frame, width=40)
    entry_tuoi.grid(row=2, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="SĐT:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_sdt = ttk.Entry(form_frame, width=40)
    entry_sdt.grid(row=3, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Giới tính:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    # Checkbutton liên kết với biến var_is_male
    chk_gioitinh_nam = ttk.Checkbutton(
        form_frame, text="Nam", variable=var_is_male,
        onvalue=True, offvalue=False
    )
    chk_gioitinh_nam.grid(row=4, column=1, padx=5, pady=5, sticky="w")
    
    ttk.Label(form_frame, text="Khoa:").grid(row=5, column=0, padx=5, pady=5, sticky="w")
    # Combobox, state="readonly" để không cho người dùng gõ
    combo_khoa_nv = ttk.Combobox(form_frame, width=38, state="readonly")
    combo_khoa_nv.grid(row=5, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Chức vụ:").grid(row=6, column=0, padx=5, pady=5, sticky="w")
    combo_chucvu_nv = ttk.Combobox(form_frame, width=38, state="readonly")
    combo_chucvu_nv.grid(row=6, column=1, padx=5, pady=5)
    
   
    # --- Treeview (Bảng dữ liệu) ---
    # Tạo khung chứa Treeview và thanh cuộn
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10) # fill="both", expand=True để lấp đầy
    
    # Thanh cuộn dọc (Y)
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    # Thanh cuộn ngang (X)
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    # Tạo Treeview
    tree = ttk.Treeview(
        tree_frame,
        columns=("MaNV", "HoTen", "Tuoi", "GioiTinh", "SDT", "MaKhoa", "MaCV"),
        show="headings", # Chỉ hiển thị tiêu đề, ẩn cột đầu tiên (cột #0)
        yscrollcommand=tree_scroll_y.set, # Gắn thanh cuộn Y
        xscrollcommand=tree_scroll_x.set 	# Gắn thanh cuộn X
    )
    # Kết nối ngược lại từ thanh cuộn đến Treeview
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Đặt tiêu đề cho các cột
    tree.heading("MaNV", text="Mã NV")
    tree.heading("HoTen", text="Họ Tên")
    tree.heading("Tuoi", text="Tuổi")
    tree.heading("GioiTinh", text="Giới Tính")
    tree.heading("SDT", text="SĐT")
    tree.heading("MaKhoa", text="Mã Khoa")
    tree.heading("MaCV", text="Mã CV")
    
    # Đặt độ rộng và căn lề
    tree.column("MaNV", width=80, anchor="c") # anchor "c" (center) cho mã
    tree.column("HoTen", width=150, anchor="c")
    tree.column("Tuoi", width=50, anchor="c") # anchor "c" (center) là căn giữa
    tree.column("GioiTinh", width=60, anchor="c")
    
    # ===== SỬA LỖI TẠI ĐÂY (Lỗi anchor) =====
    tree.column("SDT", width=100, anchor="c") # LỖI GỐC: anchor="C"
    
    tree.column("MaKhoa", width=80, anchor="c")
    tree.column("MaCV", width=80, anchor="c")

    tree.pack(fill="both", expand=True)
    # Gán sự kiện: khi click vào 1 hàng (select), gọi hàm on_item_select
    tree.bind("<<TreeviewSelect>>", on_item_select)
    
    # --- Frame cho các nút (Thêm, Sửa, Xóa...) ---
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    # ===== SỬA LỖI TẠI ĐÂY (Lỗi side) =====
    # Các nút chức năng
    # Sử dụng side=tk.LEFT thay vì tk.CENTER
    btn_them = ttk.Button(button_frame, text="Thêm", command=on_add)
    btn_them.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER
    
    btn_sua = ttk.Button(button_frame, text="Sửa", command=on_edit)
    btn_sua.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER
    
    btn_luu = ttk.Button(button_frame, text="Lưu", command=on_save)
    btn_luu.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER
    
    btn_xoa = ttk.Button(button_frame, text="Xóa", command=on_delete)
    btn_xoa.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER
    
    btn_boqua = ttk.Button(button_frame, text="Bỏ qua", command=clear_entries)
    btn_boqua.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER
    
    
    btn_thoat = ttk.Button(button_frame, text="Thoát", command=parent_tab.winfo_toplevel().destroy)
    btn_thoat.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER

    # --- Khởi tạo ---
    # 1. Tải danh sách vào combobox
    update_comboboxes()
    combo_khoa_nv.set("")
    combo_chucvu_nv.set("")
    
    # 2. Tải dữ liệu nhân viên vào Treeview
    refresh_tree()
    
    # 3. Đặt trạng thái ban đầu (khóa form, bật nút 'Thêm')
    clear_entries()