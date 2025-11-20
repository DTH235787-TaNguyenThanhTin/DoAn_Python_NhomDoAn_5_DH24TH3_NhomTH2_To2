import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry # <-- Import lịch
import datetime # <-- Import để xử lý ngày
# --- Import CSDL ---
from db_connect import connect_db
import mysql.connector

def create_view(parent_tab, benhnhan_data, macbenh_data):
    #Tạo giao diện cho tab Quản lý Bệnh nhân Sử dụng benhnhan_data và macbenh_data (để làm combobox)
    # --- Biến nội bộ ----
    current_mode = None 
    selected_item_id = None 
    # === THAY ĐỔI: Quay lại dùng BooleanVar cho checkbox ===
    # Biến đặc biệt của Tkinter để theo dõi trạng thái (True/False) của checkbox
    # Mặc định là False (Nữ)
    var_is_male = tk.BooleanVar(value=False) 

    # --- Hàm xử lý ComboBox ---
    def update_mabenh_combobox():
        #Cập nhật danh sách bệnh cho ComboBox 'Mắc bệnh'."""
        mabenh_display_list = [f"{b['MaBenh']} - {b['LoaiBenh']}" for b in macbenh_data]
        combo_mabenh['values'] = mabenh_display_list

    # --- Các hàm xử lý (nội bộ) ---
    def refresh_tree():
        #Làm mới Treeview, tải lại toàn bộ dữ liệu từ benhnhan_data."""
        for item in tree.get_children():
            tree.delete(item)
        
        for bn in benhnhan_data:
            ngay_sinh_display = bn['NgaySinh'].strftime('%Y-%m-%d') if isinstance(bn['NgaySinh'], datetime.date) else bn['NgaySinh']
            
            tree.insert("", tk.END, iid=bn['MaBN'], values=(
                bn['MaBN'], bn['HoTenBN'], bn['GioiTinhBN'], bn['TuoiBN'],
                bn['SDTBN'], ngay_sinh_display, bn['DiaChiBN'], bn['MaBenh']
            ))
            
    def set_form_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các ô nhập liệu."""
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
        
        entry_mabn.config(state=pk_state)
        entry_hoten.config(state=other_state)
        entry_tuoi.config(state=other_state)
        entry_sdt.config(state=other_state)
        entry_diachi.config(state=other_state)
        
        widget_state = 'normal' if other_state == 'normal' else 'disabled'
        
        # === THAY ĐỔI: Áp dụng cho Checkbox Giới tính ===
        chk_gioitinh.config(state=widget_state)
        # ===============================================
        
        combo_mabenh.config(state='readonly' if widget_state == 'normal' else 'disabled')
        cal_ngaysinh.config(state=widget_state)
        
    def set_button_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các nút chức năng."""
        btn_them.config(state='normal' if state == 'idle' else 'disabled')
        btn_sua.config(state='normal' if state == 'selected' else 'disabled')
        btn_luu.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        btn_xoa.config(state='normal' if state == 'selected' else 'disabled')
        btn_boqua.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')

    def clear_entries():
        #Xóa trắng các ô nhập liệu và reset trạng thái về 'idle'."""
        nonlocal current_mode, selected_item_id
        current_mode = None
        selected_item_id = None
        
        set_form_state('normal') 
        
        entry_mabn.delete(0, tk.END)
        entry_hoten.delete(0, tk.END)
        entry_tuoi.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        entry_diachi.delete(0, tk.END)
        
        # === THAY ĐỔI: Reset Checkbox ===
        var_is_male.set(False) # Đặt về Nữ (bỏ tích)
        # ==================================
        
        combo_mabenh.set("")
        cal_ngaysinh.set_date(datetime.date.today()) 
        
        set_form_state('disabled') 
        set_button_state('idle')
        
        if tree.selection():
            tree.selection_remove(tree.selection())

    def on_add():
        #Hàm xử lý khi nhấn nút 'Thêm'
        nonlocal current_mode
        clear_entries() 
        current_mode = 'add' 
        set_form_state('add') 
        set_button_state('add') 
        entry_mabn.focus() 

    def on_edit():
        #Hàm xử lý khi nhấn nút 'Sửa'
        nonlocal current_mode
        if not selected_item_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một Bệnh nhân để sửa.")
            return
        
        current_mode = 'edit' 
        set_form_state('edit') 
        set_button_state('edit') 
        entry_hoten.focus() 

    def get_ma_from_display(display_text):
        # Hàm trợ giúp: Tách Mã Bệnh từ chuỗi hiển thị
        if not display_text: return None 
        return display_text.split(" - ")[0]

    def on_save():
        #Hàm xử lý khi nhấn nút 'Lưu' (cho cả Thêm và Sửa).
        nonlocal current_mode, selected_item_id
        
        ma_bn = entry_mabn.get().strip()
        ho_ten = entry_hoten.get().strip()
        tuoi_str = entry_tuoi.get().strip()
        sdt = entry_sdt.get().strip()
        diachi = entry_diachi.get().strip()
        
        # === THAY ĐỔI: Lấy giá trị từ Checkbox ===
        # var_is_male.get() trả về True nếu được tích, False nếu không
        gioitinh = "Nam" if var_is_male.get() else "Nữ"
        # ==========================================
        
        # Kiểm tra dữ liệu (giới tính luôn có giá trị 'Nam' hoặc 'Nữ' nên không cần kiểm tra)
        if not all([ma_bn, ho_ten, tuoi_str, sdt, diachi]):
            messagebox.showwarning("Thiếu thông tin", "Vui lòng nhập tất cả các trường (trừ Mã Bệnh).")
            return

        try:
            tuoi_bn = int(tuoi_str) 
            ngay_sinh = cal_ngaysinh.get_date() 
            ma_benh = get_ma_from_display(combo_mabenh.get()) 
            
            new_data_dict = {
                'MaBN': ma_bn,
                'HoTenBN': ho_ten,
                'GioiTinhBN': gioitinh, # Đã lấy từ checkbox
                'TuoiBN': tuoi_bn,
                'SDTBN': sdt,
                'NgaySinh': ngay_sinh,
                'DiaChiBN': diachi,
                'MaBenh': ma_benh
            }
            
            conn = connect_db()
            cursor = conn.cursor()

            if current_mode == 'add':
                if any(item['MaBN'] == ma_bn for item in benhnhan_data):
                    messagebox.showerror("Lỗi", "Mã Bệnh nhân này đã tồn tại.")
                    conn.close()
                    return
                
                sql = """
                    INSERT INTO benhnhan (MaBN, HoTenBN, GioiTinhBN, TuoiBN, SDTBN, NgaySinh, DiaChiBN, MaBenh)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (ma_bn, ho_ten, gioitinh, tuoi_bn, sdt, ngay_sinh, diachi, ma_benh))
                
                benhnhan_data.append(new_data_dict)
                messagebox.showinfo("Thành công", f"Đã thêm Bệnh nhân: {ma_bn}")
            
            elif current_mode == 'edit':
                sql = """
                    UPDATE benhnhan SET 
                    HoTenBN=%s, GioiTinhBN=%s, TuoiBN=%s, SDTBN=%s, NgaySinh=%s, DiaChiBN=%s, MaBenh=%s
                    WHERE MaBN=%s
                """
                cursor.execute(sql, (ho_ten, gioitinh, tuoi_bn, sdt, ngay_sinh, diachi, ma_benh, selected_item_id))
                
                for i, item in enumerate(benhnhan_data):
                    if item['MaBN'] == selected_item_id:
                        new_data_dict['MaBN'] = selected_item_id 
                        benhnhan_data[i] = new_data_dict
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật Bệnh nhân: {selected_item_id}")

            conn.commit()
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu:\n{e}")
        except ValueError:
            messagebox.showerror("Lỗi Nhập liệu", "Tuổi BN phải là một con số.")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
            
        refresh_tree()
        clear_entries()

    def on_delete():
        #Hàm xử lý khi nhấn nút 'Xóa'."""
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một Bệnh nhân từ danh sách để Xóa.")
            return
        
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Bệnh nhân {selected_item_id}?"):
            return

        try:
            conn = connect_db()
            cursor = conn.cursor()
            
            sql_delete = "DELETE FROM benhnhan WHERE MaBN = %s"
            cursor.execute(sql_delete, (selected_item_id,))
            conn.commit()
            
            item_to_remove = None
            for item in benhnhan_data:
                if item['MaBN'] == selected_item_id:
                    item_to_remove = item
                    break
            if item_to_remove:
                benhnhan_data.remove(item_to_remove)
                
            messagebox.showinfo("Thành công", "Đã xóa Bệnh nhân.")
            
        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                
        refresh_tree()
        clear_entries()

    def find_display_by_ma(ma, data_list, key_ma, key_ten):
        # Hàm trợ giúp: Tìm chuỗi hiển thị từ mã
        for item in data_list:
            if item[key_ma] == ma:
                return f"{item[key_ma]} - {item[key_ten]}"
        return "" 

    def on_item_select(event):
        # Hàm xử lý khi chọn một mục trong Treeview
        nonlocal selected_item_id
        
        selected_items = tree.selection()
        if not selected_items:
            clear_entries()
            return
        
        item_id = selected_items[0]
        
        item_data_dict = None
        for item in benhnhan_data:
            if item['MaBN'] == item_id:
                item_data_dict = item
                break
        
        if not item_data_dict: return 

        set_form_state('normal') 
        
        entry_mabn.delete(0, tk.END)
        entry_hoten.delete(0, tk.END)
        entry_tuoi.delete(0, tk.END)
        entry_sdt.delete(0, tk.END)
        entry_diachi.delete(0, tk.END)

        entry_mabn.insert(0, item_data_dict['MaBN'])
        entry_hoten.insert(0, item_data_dict['HoTenBN'])
        entry_tuoi.insert(0, item_data_dict['TuoiBN'])
        entry_sdt.insert(0, item_data_dict['SDTBN'])
        entry_diachi.insert(0, item_data_dict['DiaChiBN'])
        
        # === THAY ĐỔI: Đặt giá trị Checkbox ===
        # Nếu 'GioiTinhBN' trong dữ liệu là "Nam" -> .set(True) (tích)
        # Nếu là "Nữ" (hoặc khác) -> .set(False) (bỏ tích)
        var_is_male.set(item_data_dict['GioiTinhBN'] == "Nam")
        # =======================================
        
        ngay_sinh = item_data_dict['NgaySinh']
        if isinstance(ngay_sinh, (datetime.date, datetime.datetime)):
            cal_ngaysinh.set_date(ngay_sinh)
        elif isinstance(ngay_sinh, str):
            try:
                cal_ngaysinh.set_date(datetime.datetime.strptime(ngay_sinh, '%Y-%m-%d').date())
            except ValueError:
                cal_ngaysinh.set_date(datetime.date.today()) 
        else:
            cal_ngaysinh.set_date(datetime.date.today())
        
        mabenh_display = ""
        if item_data_dict['MaBenh']:
            mabenh_display = find_display_by_ma(item_data_dict['MaBenh'], macbenh_data, 'MaBenh', 'LoaiBenh')
        combo_mabenh.set(mabenh_display)
        
        selected_item_id = item_data_dict['MaBN']
        
        set_form_state('disabled') 
        set_button_state('selected') 

    # --- Tạo Form Nhập liệu (UI) ---
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Bệnh nhân")
    form_frame.pack(fill="x", expand=False, padx=10, pady=10) 

    # --- Cột 0 và 1 ---
    ttk.Label(form_frame, text="Mã BN:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    entry_mabn = ttk.Entry(form_frame, width=30)
    entry_mabn.grid(row=0, column=1, padx=5, pady=5)

    ttk.Label(form_frame, text="Họ tên:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_hoten = ttk.Entry(form_frame, width=30)
    entry_hoten.grid(row=1, column=1, padx=5, pady=5)

    
    ttk.Label(form_frame, text="Giới tính:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    chk_gioitinh = ttk.Checkbutton(
        form_frame,
        text="Nam ", # Thêm khoảng trắng cho đẹp
        variable=var_is_male, # Liên kết với biến BooleanVar
        onvalue=True,         # Giá trị khi tích
        offvalue=False        # Giá trị khi không tích
    )
    chk_gioitinh.grid(row=2, column=1, padx=5, pady=5, sticky="w") # sticky="w" để căn trái
    # ===============================================

    ttk.Label(form_frame, text="Tuổi:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_tuoi = ttk.Entry(form_frame, width=30)
    entry_tuoi.grid(row=3, column=1, padx=5, pady=5)

    # --- Cột 2 và 3 ---
    ttk.Label(form_frame, text="SĐT:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    entry_sdt = ttk.Entry(form_frame, width=30)
    entry_sdt.grid(row=0, column=3, padx=5, pady=5)
    
    ttk.Label(form_frame, text="Ngày sinh:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    cal_ngaysinh = DateEntry(form_frame, width=28, date_pattern='yyyy-mm-d',
                             background='darkblue', foreground='white', borderwidth=2)
    cal_ngaysinh.grid(row=1, column=3, padx=5, pady=5)
    
    ttk.Label(form_frame, text="Địa chỉ:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
    entry_diachi = ttk.Entry(form_frame, width=30)
    entry_diachi.grid(row=2, column=3, padx=5, pady=5)

    ttk.Label(form_frame, text="Mắc bệnh:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
    combo_mabenh = ttk.Combobox(form_frame, width=28, state="readonly")
    combo_mabenh.grid(row=3, column=3, padx=5, pady=5)
    
   

    # --- Treeview (Bảng dữ liệu) ---
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10) 
    
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    tree_cols = ("MaBN", "HoTen", "GioiTinh", "Tuoi", "SDT", "NgaySinh", "DiaChi", "MaBenh")
    tree = ttk.Treeview(
        tree_frame, columns=tree_cols, show="headings",
        yscrollcommand=tree_scroll_y.set, 
        xscrollcommand=tree_scroll_x.set  
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    tree.heading("MaBN", text="Mã BN")
    tree.heading("HoTen", text="Họ Tên")
    tree.heading("GioiTinh", text="Giới Tính")
    tree.heading("Tuoi", text="Tuổi")
    tree.heading("SDT", text="SĐT")
    tree.heading("NgaySinh", text="Ngày Sinh")
    tree.heading("DiaChi", text="Địa Chỉ")
    tree.heading("MaBenh", text="Mã Bệnh")
    
    tree.column("MaBN", width=80, anchor="w") 
    tree.column("HoTen", width=150, anchor="w")
    tree.column("GioiTinh", width=60, anchor="c") 
    tree.column("Tuoi", width=50, anchor="c")
    tree.column("SDT", width=100, anchor="w")
    tree.column("NgaySinh", width=100, anchor="c")
    tree.column("DiaChi", width=200, anchor="w")
    tree.column("MaBenh", width=80, anchor="w")

    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_item_select)
    
    # --- Frame cho các nút chức năng (Thêm, Sửa, Xóa...) ---
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
    
    

    # --- Khởi tạo khi mở tab ---
    update_mabenh_combobox() 
    combo_mabenh.set("") 
    
    refresh_tree() 
    
    clear_entries()