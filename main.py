import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector

# Import các hàm và module tùy chỉnh của bạn
try:
    from db_connect import connect_db, center_window
    import nhanvien_tab
    import benhnhan_tab
    import khoa_tab
    import chucvu_tab
    import macbenh_tab
    import thuoc_tab
    import donthuoc_tab
    import chitietdonthuoc_tab
except ImportError as e:
    messagebox.showerror("Lỗi Import", f"Không thể import một module cần thiết.\nLỗi: {e}")
    exit()

# ===== LỚP NÚT BẤM (Giữ nguyên) =====
class ShapeButton(tk.Frame):
    def __init__(self, parent, text, command, width, height,
                 bg_color="black", fg_color="white", hover_color="#333333"):
        
        super().__init__(parent, width=width, height=height)
        self.pack_propagate(False)
        self.config(bg=parent.cget('bg')) 

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        
        self.canvas = tk.Canvas(self, width=width, height=height, 
                                bg=parent.cget('bg'), highlightthickness=0)
        self.canvas.pack()
        # Khi frame chứa nút thay đổi kích thước thì cập nhật canvas
        self.bind("<Configure>", self._on_resize)

        self.shape_id = self.canvas.create_rectangle(
            2, 2, width-2, height-2, 
            fill=self.bg_color, outline=self.bg_color
        )
        
        self.text_id = self.canvas.create_text(
            width/2, height/2, text=text, fill=self.fg_color, 
            font=("Times New Roman", 12, "bold")
        )
        self.canvas.bind("<Button-1>", self._on_click)
        self.canvas.bind("<Enter>", self._on_enter)
        self.canvas.bind("<Leave>", self._on_leave)

    def _on_click(self, event):
        if self.command: self.command()
    def _on_enter(self, event):
        self.canvas.itemconfig(self.shape_id, fill=self.hover_color, outline=self.hover_color)
    def _on_leave(self, event):
        self.canvas.itemconfig(self.shape_id, fill=self.bg_color, outline=self.bg_color)
    
    def _on_resize(self, event):
        # Cập nhật kích thước canvas, hình chữ nhật và vị trí text
        try:
            w = event.width
            h = event.height
            self.canvas.config(width=w, height=h)
            self.canvas.coords(self.shape_id, 2, 2, max(4, w-2), max(4, h-2))
            self.canvas.coords(self.text_id, w/2, h/2)
            font_size = max(8, int(h * 0.35))
            self.canvas.itemconfig(self.text_id, font=("Times New Roman", font_size, "bold"))
        except Exception:
            pass
# ===== KẾT THÚC LỚP NÚT BẤM =====


def open_main_window():

    # --- 1. CÀI ĐẶT CỬA SỔ CHÍNH ---
    root = tk.Tk()
    root.title("Hệ Thống Quản Lý Bệnh Nhân")
    center_window(root, 1000, 750) 
    # Cho phép thay đổi kích thước cửa sổ
    root.resizable(True, True)
    
    main_bg = "white"
    sidebar_bg = "#EAF2F8"
    root.config(bg=main_bg)
    sidebar_text_color = "#343a40"

    # ===== TẢI DỮ LIỆU TỪ MYSQL LÊN "CACHE" =====
    # Khởi tạo tất cả các danh sách
    khoa_data = []
    chucvu_data = []
    nhanvien_data = []
    benhnhan_data = []
    macbenh_data = []
    thuoc_data = []
    donthuoc_data = []
    # ===== THAY ĐỔI 1: Đổi tên biến để đồng bộ với tên bảng =====
    chitietdonthuoc_data = []
    # =======================================================
    
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True) # Rất quan trọng: để trả về dạng dict
        
        # Tải dữ liệu các bảng liên quan
        cursor.execute("SELECT * FROM khoa")
        khoa_data.extend(cursor.fetchall())
        
        cursor.execute("SELECT * FROM chucvu")
        chucvu_data.extend(cursor.fetchall())
        
        cursor.execute("SELECT * FROM nhanvien")
        nhanvien_data.extend(cursor.fetchall())
        
        cursor.execute("SELECT * FROM macbenh")
        macbenh_data.extend(cursor.fetchall())
        
        cursor.execute("SELECT * FROM benhnhan")
        benhnhan_data.extend(cursor.fetchall())
        
        cursor.execute("SELECT * FROM thuoc")
        thuoc_data.extend(cursor.fetchall())
        
        cursor.execute("SELECT * FROM donthuoc")
        donthuoc_data.extend(cursor.fetchall())
        
        
        cursor.execute("SELECT * FROM chitietdonthuoc") # Tên bảng này đã đúng
        # ===== THAY ĐỔI 2: Nạp data vào biến đã đổi tên =====
        chitietdonthuoc_data.extend(cursor.fetchall())
        # ==================================================
       
        
        cursor.close()
        conn.close()
        messagebox.showinfo("Khởi động", "Đã tải dữ liệu từ CSDL thành công!")
        
    except mysql.connector.Error as e:
        messagebox.showerror("Lỗi CSDL", f"Không thể tải dữ liệu khi khởi động.\nLỗi: {e}")
        root.destroy()
        return
    # ==========================================

    # --- 2. TẠO CÁC FRAME CHÍNH ---
    frame_sidebar = tk.Frame(root, relief=tk.RIDGE, bd=2, padx=10, pady=10, bg=sidebar_bg)
    frame_sidebar.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)
    frame_sidebar.config(width=220)
    frame_sidebar.pack_propagate(False)

    main_frame = tk.Frame(root, bg=main_bg)
    main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

    # --- 3. CÁC HÀM TRỢ GIÚP (Lồng bên trong) ---
    def clear_main_frame():
        for widget in main_frame.winfo_children():
            widget.destroy()

    def on_logout():
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            root.destroy()

    def _check_db_connection():
        try:
            conn = connect_db()
            conn.close()
            return True
        except Exception as e:
            messagebox.showerror("Lỗi CSDL", f"Không thể kết nối đến CSDL.\nLỗi: {e}")
            return False

    # --- 4. CÁC HÀM CHUYỂN ĐỔI VIEW (ĐÃ SỬA LỖI) ---
    # Các hàm này sẽ truyền (pass) các danh sách dữ liệu vào các tab.

    def show_trangchu_view():
        clear_main_frame()
        tk.Label(main_frame, text="TRANG CHỦ",
                 font=("Times New Roman", 32, "bold"),
                 bg=main_bg, fg="#333").pack(expand=True)
        tk.Label(main_frame, text="Chào mừng đến với Hệ thống Quản lý Bệnh nhân!",
                 font=("Times New Roman", 22),
                 bg=main_bg).pack(expand=True)

    def show_benhnhan_view():
        clear_main_frame()
        benhnhan_tab.create_view(main_frame, benhnhan_data, macbenh_data)
    
    def show_nhanvien_view():
        clear_main_frame()
        nhanvien_tab.create_view(
            main_frame, 
            nhanvien_data, 
            khoa_data, 
            chucvu_data
        )

    def show_khoa_view():
        clear_main_frame()
        khoa_tab.create_view(main_frame, khoa_data)

    def show_chucvu_view():
        clear_main_frame()
        chucvu_tab.create_view(main_frame, chucvu_data)

    def show_macbenh_view():
        clear_main_frame()
        macbenh_tab.create_view(main_frame, macbenh_data)

    def show_thuoc_view():
        clear_main_frame()
        thuoc_tab.create_view(main_frame, thuoc_data)

    def show_donthuoc_view():
        clear_main_frame()
        donthuoc_tab.create_view(main_frame, donthuoc_data, benhnhan_data, nhanvien_data)

    # ===== THAY ĐỔI 3: Sửa lỗi "không hiển thị" =====
    # Xóa bỏ hàm 'def create_view' lồng bên trong
    # và gọi thẳng hàm đã import, truyền các biến data đã tải
    def show_chitietdonthuoc_view():
        clear_main_frame()
        chitietdonthuoc_tab.create_view(
            main_frame, 
            chitietdonthuoc_data,  # Truyền biến đã đổi tên
            donthuoc_data, 
            thuoc_data, 
            benhnhan_data, 
            nhanvien_data
        )
    # ===============================================

    # --- 5. TẠO CÁC NÚT CHO SIDEBAR (Giữ nguyên) ---
    tk.Label(frame_sidebar, text="Menu Quản lý",
             font=("Times New Roman", 18, "bold"),
             bg=sidebar_bg, fg=sidebar_text_color).pack(pady=20, padx=10)

    buttons_info = [
        ("Trang chủ", show_trangchu_view),
        ("Quản lý Bệnh nhân", show_benhnhan_view),
        ("Quản lý Nhân Viên", show_nhanvien_view),
        ("Quản lý Khoa", show_khoa_view),
        ("Quản lý Chức vụ", show_chucvu_view),
        ("Hồ sơ Mắc bệnh", show_macbenh_view),
        ("Quản lý Thuốc", show_thuoc_view),
        ("Quản lý Đơn thuốc", show_donthuoc_view),
        ("Chi tiết Đơn thuốc", show_chitietdonthuoc_view)
    ]
    
    btn_width = 190
    btn_height = 40
    btn_bg_color = "black"
    btn_hover_color = "#333333"

    for text, command in buttons_info:
        btn = ShapeButton(
            frame_sidebar, text=text, command=command,
            width=btn_width, height=btn_height,
            bg_color=btn_bg_color, hover_color=btn_hover_color
        )
        btn.pack(fill="x", pady=4, padx=10)

    logout_btn = ShapeButton(
        frame_sidebar, text="Đăng xuất", command=on_logout,
        width=btn_width, height=btn_height,
        bg_color=btn_bg_color, hover_color=btn_hover_color
    )
    logout_btn.pack(side="bottom", fill="x", pady=20, padx=10)

    # --- 6. KIỂM TRA DB VÀ CHẠY ỨNG DỤNG ---
    show_trangchu_view()
    root.mainloop()

# --- ĐIỂM KHỞI CHẠY CHÍNH CỦA ỨNG DỤNG ---
if __name__ == "__main__":
    open_main_window()