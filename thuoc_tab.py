import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
# --- Import CSDL ---
from db_connect import connect_db
import mysql.connector

def create_view(parent_tab, data_list):
    #Tạo giao diện cho tab Quản lý Thuốc.data_list là một list "cache" được chia sẻ từ file main."""
    
    # --- Biến nội bộ ---
    # Biến lưu trạng thái: 'add' (đang thêm) hoặc 'edit' (đang sửa)
    current_mode = None 
    # Biến lưu Mã Thuốc (khóa chính) của mục đang được chọn
    selected_item_id = None

    # --- Các hàm xử lý (nội bộ) ---
    def refresh_tree():
        #Làm mới Treeview với dữ liệu từ data_list (cache).
        # Xóa tất cả các hàng hiện có trong Treeview
        for item in tree.get_children():
            tree.delete(item)
        # Thêm lại từng hàng từ danh sách data_list
        for item in data_list:
            # iid (item ID) là Mã Thuốc, dùng để định danh hàng
            tree.insert("", tk.END, iid=item['MaThuoc'], values=(item['MaThuoc'], item['TenThuoc'], item['DonViTinh']))
            
    def set_form_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các ô nhập liệu."""
        pk_state = 'disabled' # Trạng thái cho khóa chính (PK)
        other_state = 'disabled' # Trạng thái cho các trường khác
        
        if state == 'add':
            # Khi thêm, cho phép nhập cả Mã (PK) và các trường khác
            pk_state = 'normal'
            other_state = 'normal'
        elif state == 'edit':
            # Khi sửa, khóa Mã (PK), chỉ cho sửa trường khác
            pk_state = 'disabled' 
            other_state = 'normal'
        elif state == 'normal': 
            # Trạng thái 'normal' (dùng khi clear form)
            pk_state = 'normal'
            other_state = 'normal'
            
        # Áp dụng trạng thái cho 3 ô Entry
        entry_mathuoc.config(state=pk_state)
        entry_tenthuoc.config(state=other_state)
        entry_dvt.config(state=other_state)

    def set_button_state(state):
        #Kích hoạt (enable) hoặc vô hiệu hóa (disable) các nút chức năng.
        # 'idle': Trạng thái chờ, chỉ 'Thêm' sáng
        # 'selected': Đã chọn 1 hàng, 'Sửa' và 'Xóa' sáng
        # 'add'/'edit': Đang Thêm/Sửa, 'Lưu' và 'Bỏ qua' sáng
        btn_them.config(state='normal' if state == 'idle' else 'disabled')
        btn_sua.config(state='normal' if state == 'selected' else 'disabled')
        btn_luu.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        btn_xoa.config(state='normal' if state == 'selected' else 'disabled')
        btn_boqua.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        
    def clear_entries():
        #Xóa trắng các ô nhập liệu và reset trạng thái về 'idle'."""
        # 'nonlocal' để sử dụng các biến được định nghĩa ở hàm create_view
        nonlocal current_mode, selected_item_id
        # Reset biến trạng thái
        current_mode = None
        selected_item_id = None
        
        # Tạm thời mở khóa các ô để xóa
        set_form_state('normal') 
        entry_mathuoc.delete(0, tk.END)
        entry_tenthuoc.delete(0, tk.END)
        entry_dvt.delete(0, tk.END)
        
        # Khóa lại các ô
        set_form_state('disabled') 
        # Đặt trạng thái nút về 'idle' (chỉ 'Thêm' sáng)
        set_button_state('idle')
        
        # Bỏ chọn hàng hiện tại trong Treeview (nếu có)
        if tree.selection():
            tree.selection_remove(tree.selection())

    def on_add():
        #Hàm xử lý khi nhấn nút 'Thêm'."""
        nonlocal current_mode
        clear_entries() # Xóa form trước
        current_mode = 'add' # Đặt chế độ là 'thêm'
        set_form_state('add') # Mở khóa form
        set_button_state('add') # Bật nút 'Lưu', 'Bỏ qua'
        entry_mathuoc.focus() # Di chuyển con trỏ chuột vào ô Mã Thuốc

    def on_edit():
        #Hàm xử lý khi nhấn nút 'Sửa'."""
        nonlocal current_mode
        # Kiểm tra xem đã chọn Thuốc nào chưa
        if not selected_item_id:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một loại Thuốc để sửa.")
            return
        
        current_mode = 'edit' # Đặt chế độ là 'sửa'
        set_form_state('edit') # Mở khóa form (trừ Mã Thuốc)
        set_button_state('edit') # Bật nút 'Lưu', 'Bỏ qua'
        entry_tenthuoc.focus() # Di chuyển con trỏ chuột vào ô Tên Thuốc

    def on_save():
        #Hàm xử lý khi nhấn nút 'Lưu' (cho cả Thêm và Sửa)."""
        nonlocal current_mode, selected_item_id
        
        # 1. Lấy dữ liệu từ các ô nhập liệu
        ma_thuoc = entry_mathuoc.get().strip()
        ten_thuoc = entry_tenthuoc.get().strip()
        dvt = entry_dvt.get().strip()
        
        # 2. Kiểm tra dữ liệu (Mã và Tên là bắt buộc)
        if not ma_thuoc or not ten_thuoc:
            messagebox.showwarning("Thiếu thông tin", "Mã Thuốc và Tên Thuốc là bắt buộc.")
            return

        try:
            # 3. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()

            # 4. Xử lý logic Thêm
            if current_mode == 'add':
                # Kiểm tra trùng Mã Thuốc (khóa chính) trong cache
                if any(item['MaThuoc'] == ma_thuoc for item in data_list):
                    messagebox.showerror("Lỗi", "Mã Thuốc này đã tồn tại.")
                    conn.close()
                    return
                
                # 4a. Thêm vào CSDL (dùng 'dvt or None' để nếu dvt rỗng thì chèn NULL)
                sql = "INSERT INTO thuoc (MaThuoc, TenThuoc, DonViTinh) VALUES (%s, %s, %s)"
                cursor.execute(sql, (ma_thuoc, ten_thuoc, dvt or None))
                
                # 4b. Thêm vào cache (nếu CSDL thành công)
                new_item = {'MaThuoc': ma_thuoc, 'TenThuoc': ten_thuoc, 'DonViTinh': dvt or None}
                data_list.append(new_item)
                messagebox.showinfo("Thành công", f"Đã thêm Thuốc: {ma_thuoc}")
            
            # 5. Xử lý logic Sửa
            elif current_mode == 'edit':
                # 5a. Cập nhật CSDL (MaThuoc dùng là selected_item_id)
                sql = "UPDATE thuoc SET TenThuoc = %s, DonViTinh = %s WHERE MaThuoc = %s"
                cursor.execute(sql, (ten_thuoc, dvt or None, selected_item_id))
                
                # 5b. Cập nhật cache
                for item in data_list:
                    if item['MaThuoc'] == selected_item_id:
                        item['TenThuoc'] = ten_thuoc # Cập nhật Tên Thuốc
                        item['DonViTinh'] = dvt or None # Cập nhật DVT
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật Thuốc: {selected_item_id}")

            # 6. Lưu thay đổi vào CSDL
            conn.commit()
            
        except mysql.connector.Error as e:
            # Bắt lỗi nếu có lỗi CSDL
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu dữ liệu:\n{e}")
        finally:
            # 7. Luôn đóng kết nối CSDL
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
            
        # 8. Cập nhật lại giao diện
        refresh_tree() # Tải lại Treeview từ cache
        clear_entries() # Xóa form và reset trạng thái

    def on_delete():
        #Hàm xử lý khi nhấn nút 'Xóa'."""
        # 1. Kiểm tra đã chọn
        if not selected_item_id:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một loại Thuốc từ danh sách để Xóa.")
            return
        
        # 2. Xác nhận
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa Thuốc {selected_item_id}?"):
            return

        try:
            # 3. Kết nối CSDL
            conn = connect_db()
            cursor = conn.cursor()
            
            # 4. (Giả định) Kiểm tra ràng buộc khóa ngoại trong chitietdonthuoc (Chi Tiết Đơn Thuốc) # === SỬA LỖI 1 ===
            sql_check = "SELECT COUNT(*) FROM chitietdonthuoc WHERE MaThuoc = %s" # === SỬA LỖI 2 ===
            cursor.execute(sql_check, (selected_item_id,))
            count = cursor.fetchone()[0] # Lấy số lượng
            
            if count > 0:
                # Nếu có, không cho xóa và thông báo
                messagebox.showerror("Lỗi", f"Không thể xóa Thuốc này. Đang có {count} chi tiết đơn thuốc sử dụng nó.")
                # === THÊM DÒNG NÀY ĐỂ ĐÓNG KẾT NỐI KHI LỖI ===
                conn.close()
                return

            # 5. Nếu không có ràng buộc, tiến hành Xóa
            # 5a. Xóa khỏi CSDL
            sql_delete = "DELETE FROM thuoc WHERE MaThuoc = %s"
            cursor.execute(sql_delete, (selected_item_id,))
            conn.commit()
            
            # 5b. Xóa khỏi cache
            item_to_remove = None
            for item in data_list:
                if item['MaThuoc'] == selected_item_id:
                    item_to_remove = item
                    break
            if item_to_remove:
                data_list.remove(item_to_remove) # Xóa mục khỏi list
                
            messagebox.showinfo("Thành công", "Đã xóa Thuốc.")
            
        except mysql.connector.Error as e:
            # 6. Xử lý lỗi đặc biệt: Bảng 'chitietdonthuoc' không tồn tại # === SỬA LỖI 3 (Tên bảng trong thông báo) ===
            if e.errno == 1146: # 1146 = Table doesn't exist
                messagebox.showwarning("Cảnh báo", f"Bảng 'chitietdonthuoc' không tồn tại. Bỏ qua kiểm tra khóa ngoại.\nLỗi: {e}")
                # (Code có thể cải tiến: Nếu lỗi 1146, nên thử chạy lại DELETE)
            else:
                # Các lỗi CSDL khác
                messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            # 7. Luôn đóng kết nối
            if 'conn' in locals() and conn.is_connected():
                cursor.close()
                conn.close()
                
        # 8. Cập nhật giao diện
        refresh_tree()
        clear_entries()

    def on_item_select(event):
        #Hàm xử lý sự kiện khi người dùng click/chọn một hàng trong Treeview."""
        nonlocal selected_item_id
        
        # Lấy danh sách các mục đang được chọn
        selected_items = tree.selection()
        if not selected_items:
            # Nếu người dùng click vào khoảng trống (bỏ chọn), thì xóa form
            clear_entries()
            return
        
        # 1. Lấy ID của hàng đã chọn
        item_id = selected_items[0] # iid (chính là MaThuoc)
        # 2. Lấy dữ liệu của hàng đó (tuple: (MaThuoc, TenThuoc, DonViTinh))
        item_data = tree.item(item_id, "values")
        
        # 3. Nạp dữ liệu lên form
        set_form_state('normal') # Mở khóa tạm thời để nạp
        entry_mathuoc.delete(0, tk.END)
        entry_tenthuoc.delete(0, tk.END)
        entry_dvt.delete(0, tk.END)
        
        entry_mathuoc.insert(0, item_data[0])
        entry_tenthuoc.insert(0, item_data[1])
        # Xử lý DonViTinh có thể NULL (trống)
        entry_dvt.insert(0, item_data[2] or "") 
        
        # 4. Lưu lại ID đã chọn
        selected_item_id = item_data[0] # Lưu MaThuoc
        
        # 5. Khóa form lại
        set_form_state('disabled') 
        # 6. Bật nút 'Sửa', 'Xóa'
        set_button_state('selected') 

    # --- Tạo Form Nhập liệu (UI) ---
    # Tạo một khung (LabelFrame) bao bọc các ô nhập liệu
    form_frame = ttk.LabelFrame(parent_tab, text="Thông tin Thuốc")
    form_frame.pack(fill="x", expand=False, padx=10, pady=10) # fill="x" co giãn theo chiều ngang

    # sticky="w" (west) để căn lề trái
    # ===== SỬA LỖI TẠI ĐÂY (Lỗi sticky) =====
    ttk.Label(form_frame, text="Mã Thuốc:").grid(row=0, column=0, padx=5, pady=5, sticky="w") # LỖI GỐC: sticky="c"
    entry_mathuoc = ttk.Entry(form_frame, width=40)
    entry_mathuoc.grid(row=0, column=1, padx=5, pady=5)

    # ===== SỬA LỖI TẠI ĐÂY (Lỗi sticky) =====
    ttk.Label(form_frame, text="Tên Thuốc:").grid(row=1, column=0, padx=5, pady=5, sticky="w") # LỖI GỐC: sticky="c"
    entry_tenthuoc = ttk.Entry(form_frame, width=40)
    entry_tenthuoc.grid(row=1, column=1, padx=5, pady=5)
    
    # ===== SỬA LỖI TẠI ĐÂY (Lỗi sticky) =====
    ttk.Label(form_frame, text="Đơn vị tính:").grid(row=2, column=0, padx=5, pady=5, sticky="w") # LỖI GỐC: sticky="c"
    entry_dvt = ttk.Entry(form_frame, width=40)
    entry_dvt.grid(row=2, column=1, padx=5, pady=5)
    
    # --- Treeview (Bảng dữ liệu) ---
    # Tạo khung chứa Treeview và thanh cuộn
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10) # fill="both", expand=True để lấp đầy
    
    # Thanh cuộn dọc (Y)
    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")

    # Tạo Treeview
    tree = ttk.Treeview(
        tree_frame,
        columns=("MaThuoc", "TenThuoc", "DonViTinh"),
        show="headings", # Chỉ hiển thị tiêu đề
        yscrollcommand=tree_scroll_y.set # Gắn thanh cuộn Y
    )
    # Kết nối ngược lại từ thanh cuộn đến Treeview
    tree_scroll_y.config(command=tree.yview)

    # Đặt tiêu đề cho các cột
    tree.heading("MaThuoc", text="Mã Thuốc")
    tree.heading("TenThuoc", text="Tên Thuốc")
    tree.heading("DonViTinh", text="Đơn Vị Tính")
    # Đặt độ rộng và căn lề
    tree.column("MaThuoc", width=100, anchor="c") # anchor "c" (center) cho mã
    tree.column("TenThuoc", width=300, anchor="c")
    tree.column("DonViTinh", width=100, anchor="c")

    tree.pack(fill="both", expand=True)
    # Gán sự kiện: khi click vào 1 hàng (select), gọi hàm on_item_select
    tree.bind("<<TreeviewSelect>>", on_item_select)
    
    # --- Frame cho các nút (Thêm, Sửa, Xóa...) ---
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    # ===== SỬA LỖI TẠI ĐÂY (Lỗi side) =====
    # Các nút chức năng
    # expand=True để các nút tự chia đều không gian
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
    
    # Nút Thoát: winfo_toplevel().destroy() để đóng toàn bộ cửa sổ chính
    btn_thoat = ttk.Button(button_frame, text="Thoát", command=parent_tab.winfo_toplevel().destroy)
    btn_thoat.pack(side=tk.LEFT, padx=5, expand=True) # LỖI GỐC: side=tk.CENTER

    # --- Khởi tạo ---
    # 1. Tải dữ liệu từ cache lên Treeview khi mở tab
    refresh_tree()
    # 2. Xóa form và đặt trạng thái ban đầu
    clear_entries() # Đặt trạng thái ban đầu