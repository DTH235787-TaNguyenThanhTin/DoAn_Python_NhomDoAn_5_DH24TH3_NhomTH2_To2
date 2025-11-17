import tkinter as tk
from tkinter import ttk, messagebox
# from tkcalendar import DateEntry # Dù không dùng nhưng vẫn giữ lại
import mysql.connector
import customtkinter
# Import các hàm và module tùy chỉnh của bạn (Giả định các file này đã tồn tại)
try:
    # Cần đảm bảo các file này tồn tại trong môi trường chạy của bạn
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
    # Nếu chạy trong môi trường có thể dừng, bạn nên dùng exit()
    # exit() 

# ===== CÁC HÀM HỖ TRỢ CHO HIỆU ỨNG ĐỘNG MÀU SẮC =====

def hex_to_rgb(hex_color):
    """Chuyển đổi màu hex (#RRGGBB) sang tuple RGB."""
    if not hex_color.startswith('#') or len(hex_color) != 7:
        return 0, 0, 0 
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Chuyển đổi tuple RGB sang màu hex (#RRGGBB)."""
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

# ===== LỚP NÚT BẤM CÓ GÓC BO TRÒN VÀ HIỆU ỨNG ĐỘNG (ShapeButton Cải Tiến) =====
class ShapeButton(tk.Frame):
    def __init__(self, parent, text, command, width, height, radius=10,
                 bg_color="#1E90FF", fg_color="white", hover_color="#4682B4"):
        
        super().__init__(parent, width=width, height=height)
        self.pack_propagate(False)
        self.config(bg=parent.cget('bg')) 

        self.command = command
        self.bg_color = bg_color
        self.hover_color = hover_color
        self.fg_color = fg_color
        self.radius = radius
        self.width = width
        self.height = height
        
        self.current_color = bg_color   # Màu hiện tại của nút
        self.animation_id = None        # ID để quản lý và hủy animation
        self.shape_ids = [] 
        
        self.canvas = tk.Canvas(self, width=width, height=height, 
                                bg=parent.cget('bg'), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", self._on_resize)
        
        # Text ID được tạo trước
        self.text_id = self.canvas.create_text(
            width/2, height/2, text=text, fill=self.fg_color, 
            font=("Times New Roman", 12, "bold")
        )

        # Vẽ nút bo tròn lần đầu
        self.shape_ids = self._draw_rounded_rectangle(self.bg_color)
        
        # Liên kết sự kiện với tất cả các thành phần của nút (hình dạng và văn bản)
        self._bind_events(self.shape_ids)
        self._bind_events(self.text_id)

    def _animate_color_transition(self, target_color, duration=150, steps=10):
        """Tạo hiệu ứng chuyển màu mượt mà."""
        
        # Hủy animation cũ nếu đang chạy
        if self.animation_id:
            self.after_cancel(self.animation_id)

        start_rgb = hex_to_rgb(self.current_color)
        target_rgb = hex_to_rgb(target_color)
        
        # Tính toán bước nhảy màu cho mỗi kênh RGB
        step_r = (target_rgb[0] - start_rgb[0]) / steps
        step_g = (target_rgb[1] - start_rgb[1]) / steps
        step_b = (target_rgb[2] - start_rgb[2]) / steps
        
        step_ms = duration // steps

        # Hàm đệ quy để thực hiện từng bước chuyển màu
        def step(current_step, current_rgb_float):
            # Nếu đã hết bước hoặc target bị thay đổi nhanh chóng, kết thúc
            if current_step >= steps:
                self.current_color = target_color
                self._set_color(target_color)
                self.animation_id = None
                return

            # Tính toán màu tiếp theo (dùng float để tăng độ chính xác)
            next_r_float = current_rgb_float[0] + step_r
            next_g_float = current_rgb_float[1] + step_g
            next_b_float = current_rgb_float[2] + step_b
            
            # Chuyển sang int và giới hạn trong khoảng 0-255
            next_rgb_int = (
                max(0, min(255, int(next_r_float))),
                max(0, min(255, int(next_g_float))),
                max(0, min(255, int(next_b_float)))
            )
            
            next_color_hex = rgb_to_hex(next_rgb_int)
            self._set_color(next_color_hex)
            self.current_color = next_color_hex 

            # Lên lịch cho bước tiếp theo
            self.animation_id = self.after(step_ms, lambda: step(current_step + 1, (next_r_float, next_g_float, next_b_float)))

        # Bắt đầu animation
        start_rgb_float = (float(start_rgb[0]), float(start_rgb[1]), float(start_rgb[2]))
        step(0, start_rgb_float)

    def _draw_rounded_rectangle(self, color):
        """Vẽ hình chữ nhật bo tròn trên canvas và trả về danh sách các ID hình dạng."""
        
        w, h, r = self.width, self.height, self.radius
        
        if r > w/2: r = w/2
        if r > h/2: r = h/2

        # 1. Xóa hình cũ nếu có (Quan trọng cho việc resize)
        for shape_id in self.shape_ids:
            try:
                self.canvas.delete(shape_id)
            except tk.TclError:
                pass # Bỏ qua lỗi nếu item đã bị xóa

        # Tọa độ cơ sở
        x1, y1 = 0, 0
        x2, y2 = w, h
        
        new_shape_ids = []
        
        # 1. Vẽ hai hình chữ nhật chính (một ngang, một dọc)
        new_shape_ids.append(self.canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=color, outline=color))
        new_shape_ids.append(self.canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=color, outline=color))

        # 2. Vẽ 4 góc bo tròn bằng hình bầu dục (oval)
        new_shape_ids.append(self.canvas.create_oval(x1, y1, x1 + 2*r, y1 + 2*r, fill=color, outline=color)) # Top-left
        new_shape_ids.append(self.canvas.create_oval(x2 - 2*r, y1, x2, y1 + 2*r, fill=color, outline=color)) # Top-right
        new_shape_ids.append(self.canvas.create_oval(x1, y2 - 2*r, x1 + 2*r, y2, fill=color, outline=color)) # Bottom-left
        new_shape_ids.append(self.canvas.create_oval(x2 - 2*r, y2 - 2*r, x2, y2, fill=color, outline=color)) # Bottom-right
        
        # Đảm bảo văn bản luôn được đưa lên lớp trên cùng sau khi vẽ tất cả các hình nền.
        self.canvas.tag_raise(self.text_id)

        return new_shape_ids

    def _bind_events(self, tags):
        """Liên kết sự kiện cho các tag hoặc một ID đơn lẻ."""
        if isinstance(tags, list):
            for tag in tags:
                self.canvas.tag_bind(tag, "<Button-1>", self._on_click)
                self.canvas.tag_bind(tag, "<Enter>", self._on_enter)
                self.canvas.tag_bind(tag, "<Leave>", self._on_leave)
        else:
            self.canvas.tag_bind(tags, "<Button-1>", self._on_click)
            self.canvas.tag_bind(tags, "<Enter>", self._on_enter)
            self.canvas.tag_bind(tags, "<Leave>", self._on_leave)


    def _on_click(self, event):
        if self.command: 
            # Dừng animation hover
            if self.animation_id:
                self.after_cancel(self.animation_id)
                self.animation_id = None
            
            # 1. Thực hiện lệnh
            self.command() 
            
            # 2. Hiệu ứng Pulse (nhấp nháy màu tối hơn)
            # Chọn màu tối hơn một chút so với màu hover
            click_pulse_color = "#333333" if hex_to_rgb(self.hover_color)[0] > 100 else "#AAAAAA" 
            
            self._set_color(click_pulse_color)
            self.current_color = click_pulse_color
            self.update_idletasks()
            
            # 3. Trở lại trạng thái hover sau 100ms
            self.after(100, lambda: self._animate_color_transition(self.hover_color)) 

    def _on_enter(self, event):
        self._animate_color_transition(self.hover_color)

    def _on_leave(self, event):
        self._animate_color_transition(self.bg_color)
        
    def _set_color(self, color):
        """Đặt màu nền cho tất cả các hình dạng."""
        for shape_id in self.shape_ids:
            try:
                self.canvas.itemconfig(shape_id, fill=color, outline=color)
            except tk.TclError:
                pass # Bỏ qua lỗi nếu item không tồn tại

    # ===== HÀM ĐÃ SỬA LỖI =====
    def _on_resize(self, event):
        # Cập nhật kích thước canvas, hình chữ nhật và vị trí text
        try:
            w = event.width
            h = event.height
            if w < 10 or h < 10: return 

            self.width = w
            self.height = h
            self.canvas.config(width=w, height=h)
            
            # Cập nhật vị trí Text
            self.canvas.coords(self.text_id, w/2, h/2)
            font_size = max(8, int(h * 0.35))
            self.canvas.itemconfig(self.text_id, font=("Times New Roman", font_size, "bold"))
            
            # Vẽ lại nút bo tròn
            # _draw_rounded_rectangle sẽ tự động xóa các ID cũ bên trong nó.
            # Chúng ta vẽ lại với MÀU HIỆN TẠI (current_color) để giữ
            # trạng thái (ví dụ: đang hover) khi resize.
            self.shape_ids = self._draw_rounded_rectangle(self.current_color)
            
            # Gỡ ràng buộc khỏi IDs cũ (ĐÃ BỊ XÓA)
            # Dòng code cũ (bên dưới) gây ra lỗi "item X doesn't exist"
            # vì các ID trong 'old_ids' đã bị xóa bởi _draw_rounded_rectangle.
            # 
            # for shape_id in old_ids:
            #     self.canvas.tag_unbind(shape_id, "<Button-1>")
            #     self.canvas.tag_unbind(shape_id, "<Enter>")
            #     self.canvas.tag_unbind(shape_id, "<Leave>")
            
            # Liên kết lại sự kiện cho IDs MỚI
            self._bind_events(self.shape_ids)
            
            # Ràng buộc cho self.text_id (văn bản) vẫn còn nguyên
            # vì nó không bao giờ bị xóa.

        except Exception as e:
            # Bỏ qua lỗi nếu canvas/widget bị hủy trong quá trình resize nhanh
            # print(f"Lỗi khi resize ShapeButton: {e}") # Bỏ comment nếu cần debug
            pass
# ===== KẾT THÚC LỚP NÚT BẤM =====


def open_main_window():

    # --- ĐỊNH NGHĨA MÀU SẮC CHO NÚT SIDEBAR ---
    btn_bg_color = "#3498DB"      # Màu xanh dương
    btn_hover_color = "#2980B9"   # Màu xanh dương đậm hơn
    # --- END FIX ---
    
    # --- 1. CÀI ĐẶT CỬA SỔ CHÍNH ---
    root = tk.Tk()
    root.title("Hệ Thống Quản Lý Bệnh Nhân")
    # Tùy chỉnh theme cho CustomTkinter nếu bạn muốn sử dụng nó ở nơi khác
    # customtkinter.set_appearance_mode("Light") 
    
    # Giả định center_window được import và hoạt động
    center_window(root, 1000, 750) 
    root.resizable(True, True)
    
    main_bg = "white"
    sidebar_bg = "#EAF2F8"
    root.config(bg=main_bg)
    sidebar_text_color = "#343a40"

    # ===== TẢI DỮ LIỆU TỪ MYSQL LÊN "CACHE" (ĐÃ KHÔI PHỤC) =====
    # Khởi tạo tất cả các danh sách
    khoa_data = []
    chucvu_data = []
    nhanvien_data = []
    benhnhan_data = []
    macbenh_data = []
    thuoc_data = []
    donthuoc_data = []
    chitietdonthuoc_data = []
    
    try:
        # --- KHÔI PHỤC KẾT NỐI CSDL ---
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
        chitietdonthuoc_data.extend(cursor.fetchall())
        
        
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

    # --- 3. CÁC HÀM TRỢ GIÚP (Giữ nguyên) ---
    def clear_main_frame():
        for widget in main_frame.winfo_children():
            widget.destroy()

    def on_logout():
        if messagebox.askyesno("Đăng xuất", "Bạn có chắc muốn đăng xuất?"):
            root.destroy()

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
        nhanvien_tab.create_view(main_frame, nhanvien_data, khoa_data, chucvu_data)

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

    def show_chitietdonthuoc_view():
        clear_main_frame()
        chitietdonthuoc_tab.create_view(
            main_frame, 
            chitietdonthuoc_data, 
            donthuoc_data, 
            thuoc_data, 
            benhnhan_data, 
            nhanvien_data
        )

    # --- 5. TẠO CÁC NÚT CHO SIDEBAR (Giữ nguyên logic) ---
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
    btn_width = 180
    btn_height = 40

    for text, command in buttons_info:
        btn = ShapeButton(
            frame_sidebar, text=text, command=command,
            width=btn_width, height=btn_height,
            bg_color=btn_bg_color, hover_color=btn_hover_color,
            radius=15 # Đặt bán kính bo góc
        )
        btn.pack(fill="x", pady=4, padx=10)

    logout_btn = ShapeButton(
        frame_sidebar, text="Đăng xuất", command=on_logout,
        width=btn_width, height=btn_height,
        bg_color="#E74C3C", hover_color="#C0392B", # Màu đỏ cho nút đăng xuất
        radius=15
    )
    logout_btn.pack(side="bottom", fill="x", pady=20, padx=10)

    # --- 6. KIỂM TRA DB VÀ CHẠY ỨNG DỤNG ---
    show_trangchu_view()
    root.mainloop()

# --- ĐIỂM KHỞI CHẠY CHÍNH CỦA ỨNG DỤNG ---
if __name__ == "__main__":
    open_main_window()