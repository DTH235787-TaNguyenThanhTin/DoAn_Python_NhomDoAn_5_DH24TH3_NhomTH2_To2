import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry # <-- Import lịch
import datetime # <-- Import để xử lý ngày
# --- Import CSDL ---
from db_connect import connect_db
import mysql.connector

def create_view(parent_tab, donthuoc_data, benhnhan_data, nhanvien_data):
    #Tạo giao diện cho tab Quản lý Đơn thuốc.Sử dụng 4 danh sách dữ liệu (cache)"""
    
    # --- Biến nội bộ ---
    # Biến lưu trạng thái: 'add' (đang thêm) hoặc 'edit' (đang sửa)
    current_mode = None
    # Biến lưu Mã ĐT (khóa chính) của mục đang được chọn
    selected_item_id = None

    # --- Hàm xử lý ComboBox ---
    def update_comboboxes():
        # Cập nhật danh sách Bệnh nhân và Nhân viên cho ComboBox.
        # Tạo danh sách hiển thị (VD: "BN01 - Nguyễn Văn A")
        bn_display_list = [f"{bn['MaBN']} - {bn['HoTenBN']}" for bn in benhnhan_data]
        nv_display_list = [f"{nv['MaNV']} - {nv['HoTenNV']}" for nv in nhanvien_data]
        
        # Gán danh sách cho combobox
        combo_mabn['values'] = bn_display_list
        combo_manv['values'] = nv_display_list
        # (Đã xóa messagebox.showinfo)

    # --- Các hàm xử lý (nội bộ) ---
    def refresh_tree():
        #Làm mới Treeview, tải lại toàn bộ dữ liệu từ donthuoc_data (cache).
        # Xóa tất cả các hàng cũ
        for item in tree.get_children():
            tree.delete(item)
            
        # Thêm lại từng hàng từ dữ liệu mới
        for dt in donthuoc_data:
            # Định dạng ngày (nếu là date object) để hiển thị YYYY-MM-DD
            ngay_lap_display = dt['NgayLap'].strftime('%Y-%m-%d') if isinstance(dt['NgayLap'], datetime.date) else dt['NgayLap']
            
            # === THAY ĐỔI: Xóa Ghi Chú (dt['GhiChu']) khỏi values ===
            tree.insert("", tk.END, iid=dt['MaDT'], values=(
                dt['MaDT'], dt['MaBN'], dt['MaNV'], ngay_lap_display
            ))
            # ========================================================
            
    def set_form_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các ô nhập liệu.
        pk_state = 'disabled'
        other_state = 'disabled'

        if state == 'add':
            pk_state = 'normal'
            other_state = 'normal'
        elif state == 'edit':
            pk_state = 'disabled' 
            other_state = 'normal'
        elif state == 'normal': 
            pk_state = 'normal'
            other_state = 'normal'
        
        # Áp dụng trạng thái
        entry_madt.config(state=pk_state)
        # (Đã xóa entry_ghichu)
        
        # Trạng thái cho các widget đặc biệt (Lịch, Combobox)
        widget_state = 'normal' if other_state == 'normal' else 'disabled'
        combo_mabn.config(state='readonly' if widget_state == 'normal' else 'disabled')
        combo_manv.config(state='readonly' if widget_state == 'normal' else 'disabled')
        cal_ngaylap.config(state=widget_state)
        
    def set_button_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các nút chức năng.
        btn_them.config(state='normal' if state == 'idle' else 'disabled')
        btn_sua.config(state='normal' if state == 'selected' else 'disabled')
        btn_luu.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        btn_xoa.config(state='normal' if state == 'selected' else 'disabled')
        btn_boqua.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        # (Đã xóa btn_refresh_combos)

    def clear_entries():
        #Xóa trắng các ô nhập liệu và reset trạng thái về 'idle'.
        nonlocal current_mode, selected_item_id
        current_mode = None
        selected_item_id = None
        
        set_form_state('normal') 
        
        entry_madt.delete(0, tk.END)
        # (Đã xóa entry_ghichu.delete)
        combo_mabn.set("")
        combo_manv.set("")
        cal_ngaylap.set_date(datetime.date.today()) 
        
        set_form_state('disabled') 
        set_button_state('idle')
        
        if tree.selection():
            tree.selection_remove(tree.selection())

    def on_add():
        #Hàm xử lý khi nhấn nút 'Thêm'."""
        nonlocal current_mode
        clear_entries() 
        current_mode = 'add' 
        set_form_state('add') 
        set_button_state('add') 
        entry_madt.focus() 

    def on_edit():
        #Hàm xử lý khi nhấn nút 'Sửa'."""
        nonlocal current_mode
        if not selected_item_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một Đơn thuốc để sửa.")
            return
        
        current_mode = 'edit' 
        set_form_state('edit') 
        set_button_state('edit') 
        combo_mabn.focus() 

    def get_ma_from_display(display_text):
        #Hàm trợ giúp: Tách Mã từ chuỗi (VD: "BN01 - A" -> "BN01")."""
        if not display_text: return None 
        return display_text.split(" - ")[0]

    def on_save():
        #Hàm xử lý khi nhấn nút 'Lưu' (cho cả Thêm và Sửa)."""
        nonlocal current_mode, selected_item_id
        
        # 1. Lấy dữ liệu từ Form
        ma_dt = entry_madt.get().strip()
        ma_bn = get_ma_from_display(combo_mabn.get())
        ma_nv = get_ma_from_display(combo_manv.get())
        
        # 2. Kiểm tra dữ liệu bắt buộc
        if not ma_dt or not ma_bn or not ma_nv:
            messagebox.showwarning("Thiếu thông tin", "Mã ĐT, Mã BN, Mã NV là bắt buộc.")
            return

        try:
            # 3. Lấy dữ liệu từ Lịch và xử lý Ghi Chú
            ngay_lap = cal_ngaylap.get_date() 
            # Gán Ghi Chú là None vì đã xóa textbox
            ghi_chu = None 
            
            # 4. Tạo từ điển (dict) để cập nhật danh sách local (cache)
            # (Vẫn giữ GhiChu trong dict để logic nhất quán, nó sẽ là None)
            new_data_dict = {
                'MaDT': ma_dt,
                'MaBN': ma_bn,
                'MaNV': ma_nv,
                'NgayLap': ngay_lap,
                'GhiChu': ghi_chu # Sẽ là None
            }
            
            # 5. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()

            # 6. Xử lý logic Thêm
            if current_mode == 'add':
                # Kiểm tra trùng khóa chính (MaDT)
                if any(item['MaDT'] == ma_dt for item in donthuoc_data):
                    messagebox.showerror("Lỗi", "Mã Đơn thuốc này đã tồn tại.")
                    conn.close()
                    return
                
                # 6a. Thêm vào CSDL
                sql = """
                    INSERT INTO donthuoc (MaDT, MaBN, MaNV, NgayLap, GhiChu)
                    VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (ma_dt, ma_bn, ma_nv, ngay_lap, ghi_chu))
                
                # 6b. Thêm vào cache
                donthuoc_data.append(new_data_dict)
                messagebox.showinfo("Thành công", f"Đã thêm Đơn thuốc: {ma_dt}")
            
            # 7. Xử lý logic Sửa
            elif current_mode == 'edit':
                # 7a. Cập nhật CSDL
                sql = """
                    UPDATE donthuoc SET 
                    MaBN=%s, MaNV=%s, NgayLap=%s, GhiChu=%s
                    WHERE MaDT=%s
                """
                # (ghi_chu sẽ là None)
                cursor.execute(sql, (ma_bn, ma_nv, ngay_lap, ghi_chu, selected_item_id))
                
                # 7b. Cập nhật cache
                for i, item in enumerate(donthuoc_data):
                    if item['MaDT'] == selected_item_id:
                        new_data_dict['MaDT'] = selected_item_id # Giữ lại MaDT
                        donthuoc_data[i] = new_data_dict
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật Đơn thuốc: {selected_item_id}")

            # 8. Lưu thay đổi
            conn.commit()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu:\n{e}")
        finally:
            # 9. Đóng kết nối
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
            
        # 10. Cập nhật giao diện
        refresh_tree()
        clear_entries()

    def on_delete():
        #Hàm xử lý khi nhấn nút 'Xóa'."""
        # 1. Kiểm tra đã chọn
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một Đơn thuốc từ danh sách để Xóa.")
            return
        
        # 2. Xác nhận
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Đơn thuốc {selected_item_id}?"):
            return

        try:
            # 3. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()
            
            # 4. Kiểm tra ràng buộc khóa ngoại trong chitietdonthuoc  # === SỬA LỖI 1 ===
            sql_check = "SELECT COUNT(*) FROM chitietdonthuoc WHERE MaDT = %s" # === SỬA LỖI 2 ===
            cursor.execute(sql_check, (selected_item_id,))
            count = cursor.fetchone()[0]
            
            if count > 0:
                messagebox.showerror("Lỗi", f"Không thể xóa Đơn thuốc này. Đang có {count} chi tiết thuốc liên quan.")
                # ===== THÊM DÒNG NÀY ĐỂ ĐÓNG KẾT NỐI KHI LỖI =====
                conn.close() 
                # ===============================================
                return

            # 5. Tiến hành Xóa
            # 5a. Xóa khỏi CSDL
            sql_delete = "DELETE FROM donthuoc WHERE MaDT = %s"
            cursor.execute(sql_delete, (selected_item_id,))
            conn.commit()
            
            # 5b. Xóa khỏi cache
            item_to_remove = None
            for item in donthuoc_data:
                if item['MaDT'] == selected_item_id:
                    item_to_remove = item
                    break
            if item_to_remove:
                donthuoc_data.remove(item_to_remove)
                
            messagebox.showinfo("Thành công", "Đã xóa Đơn thuốc.")
            
        except mysql.connector.Error as e:
            # 6. Xử lý lỗi đặc biệt: Bảng 'ctdthuoc' không tồn tại
            if e.errno == 1146: # 1146 = Table doesn't exist
                messagebox.showwarning("Cảnh báo", f"Bảng 'chitietdonthuoc' không tồn tại. Bỏ qua kiểm tra khóa ngoại.\nLỗi: {e}") # === SỬA LỖI 3 ===
            else:
                messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            # 7. Luôn đóng kết nối
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                    
        # 8. Cập nhật giao diện
        refresh_tree()
        clear_entries()

    def find_display_by_ma(ma, data_list, key_ma, key_ten):
       #Hàm trợ giúp: Tìm 'BN01 - Nguyễn Văn A' khi biết 'BN01'."""
       for item in data_list:
           if item[key_ma] == ma:
               return f"{item[key_ma]} - {item[key_ten]}"
       return "" 

    def on_item_select(event):
        #Hàm xử lý sự kiện khi người dùng click/chọn một hàng trong Treeview."""
        nonlocal selected_item_id
        
        selected_items = tree.selection()
        if not selected_items:
            clear_entries()
            return
        
        # 1. Lấy ID (MaDT) của hàng đã chọn
        item_id = selected_items[0]
        
        # 2. Tìm dữ liệu đầy đủ của hàng đó trong danh sách local (cache)
        item_data_dict = None
        for item in donthuoc_data:
            if item['MaDT'] == item_id:
                item_data_dict = item
                break
        
        if not item_data_dict: return 

        # 3. Nạp dữ liệu lên form
        set_form_state('normal') 
        
        entry_madt.delete(0, tk.END)
        # (Đã xóa entry_ghichu.delete)
        
        entry_madt.insert(0, item_data_dict['MaDT'])
        # (Đã xóa entry_ghichu.insert)
        
        # Nạp dữ liệu ngày
        ngay_lap = item_data_dict['NgayLap']
        if isinstance(ngay_lap, (datetime.date, datetime.datetime)):
            cal_ngaylap.set_date(ngay_lap)
        elif isinstance(ngay_lap, str): 
            try:
                cal_ngaylap.set_date(datetime.datetime.strptime(ngay_lap, '%Y-%m-%d').date())
            except ValueError:
                cal_ngaylap.set_date(datetime.date.today())
        else:
            cal_ngaylap.set_date(datetime.date.today())
        
        # Xử lý ComboBox
        mabn_display = find_display_by_ma(item_data_dict['MaBN'], benhnhan_data, 'MaBN', 'HoTenBN')
        manv_display = find_display_by_ma(item_data_dict['MaNV'], nhanvien_data, 'MaNV', 'HoTenNV')
        
        combo_mabn.set(mabn_display)
        combo_manv.set(manv_display)
        
        # 4. Lưu lại ID đã chọn
        selected_item_id = item_data_dict['MaDT']
        
        # 5. Khóa form lại
        set_form_state('disabled') 
        # 6. Bật nút 'Sửa', 'Xóa'
        set_button_state('selected') 

    # --- Tạo Form Nhập liệu (UI) ---
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Đơn thuốc")
    form_frame.pack(fill="x", expand=False, padx=10, pady=10) 

    # --- Cột 0, 1 ---
    ttk.Label(form_frame, text="Mã Đơn thuốc:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_madt = ttk.Entry(form_frame, width=30)
    entry_madt.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Bệnh nhân:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    combo_mabn = ttk.Combobox(form_frame, width=28, state="readonly")
    combo_mabn.grid(row=1, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Nhân viên lập:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    combo_manv = ttk.Combobox(form_frame, width=28, state="readonly")
    combo_manv.grid(row=2, column=1, padx=5, pady=5)

    # --- Cột 2, 3 ---
    ttk.Label(form_frame, text="Ngày lập:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    cal_ngaylap = DateEntry(form_frame, width=28, date_pattern='yyyy-mm-dd',
                            background='darkblue', foreground='white', borderwidth=2)
    cal_ngaylap.grid(row=0, column=3, padx=5, pady=5)
    

    # --- Treeview (Bảng dữ liệu) ---
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10) 
    
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    # === THAY ĐỔI: Xóa "GhiChu" khỏi danh sách cột ===
    tree_cols = ("MaDT", "MaBN", "MaNV", "NgayLap")
    # ===============================================
    
    tree = ttk.Treeview(
        tree_frame, columns=tree_cols, show="headings",
        yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Đặt tiêu đề cho các cột
    tree.heading("MaDT", text="Mã Đơn Thuốc")
    tree.heading("MaBN", text="Mã Bệnh Nhân")
    tree.heading("MaNV", text="Mã Nhân Viên")
    tree.heading("NgayLap", text="Ngày Lập")
    # === THAY ĐỔI: Xóa tiêu đề Ghi Chú ===
    # tree.heading("GhiChu", text="Ghi Chú") 
    # =====================================
    
    # Đặt độ rộng và căn lề
    tree.column("MaDT", width=100, anchor="w") 
    tree.column("MaBN", width=100, anchor="w")
    tree.column("MaNV", width=100, anchor="w")
    tree.column("NgayLap", width=100, anchor="c") 
    # === THAY ĐỔI: Xóa cột Ghi Chú ===
    # tree.column("GhiChu", width=200, anchor="w")
    # ==================================

    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_item_select)
    
    # --- Frame cho các nút (Thêm, Sửa, Xóa...) ---
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    btn_them = ttk.Button(button_frame, text="Thêm", command=on_add)
    btn_them.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_sua = ttk.Button(button_frame, text="Sửa", command=on_edit)
    btn_sua.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_luu = ttk.Button(button_frame, text="Lưu", command=on_save)
    btn_luu.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_xoa = ttk.Button(button_frame, text="Xóa", command=on_delete)
    btn_xoa.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_boqua = ttk.Button(button_frame, text="Bỏ qua", command=clear_entries)
    btn_boqua.pack(side=tk.LEFT, padx=5, expand=True)
    
    btn_thoat = ttk.Button(button_frame, text="Thoát", command=parent_tab.winfo_toplevel().destroy)
    btn_thoat.pack(side=tk.LEFT, padx=5, expand=True)

    # --- Khởi tạo ---
    # 1. Tải danh sách BN/NV vào combobox
    update_comboboxes() 
    combo_mabn.set("")
    combo_manv.set("")
    
    # 2. Tải danh sách đơn thuốc vào Treeview
    refresh_tree() 
    # 3. Đặt trạng thái ban đầu
    clear_entries()