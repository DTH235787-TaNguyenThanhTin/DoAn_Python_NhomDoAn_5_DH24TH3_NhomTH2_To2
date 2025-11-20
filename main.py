import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector
from PIL import Image, ImageTk # Đảm bảo đã import PIL/Pillow ở đầu file


   # pip install mysql-connector-python tkcalendar




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

# ===== CÁC HÀM HỖ TRỢ CHO HIỆU ỨNG ĐỘNG MÀU SẮC (Giữ nguyên) =====

def hex_to_rgb(hex_color):
    """Chuyển đổi màu hex (#RRGGBB) sang tuple RGB."""
    if not hex_color.startswith('#') or len(hex_color) != 7:
        return 0, 0, 0 
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def rgb_to_hex(rgb):
    """Chuyển đổi tuple RGB sang màu hex (#RRGGBB)."""
    return '#%02x%02x%02x' % (int(rgb[0]), int(rgb[1]), int(rgb[2]))

# ===== LỚP NÚT BẤM CÓ GÓC BO TRÒN VÀ HIỆU ỨNG ĐỘNG (ShapeButton Cải Tiến - Giữ nguyên) =====
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
        
        self.current_color = bg_color   
        self.animation_id = None        
        self.shape_ids = [] 
        
        self.canvas = tk.Canvas(self, width=width, height=height, 
                                bg=parent.cget('bg'), highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.bind("<Configure>", self._on_resize)
        
        self.text_id = self.canvas.create_text(
            width/2, height/2, text=text, fill=self.fg_color, 
            font=("Times New Roman", 12, "bold")
        )

        self.shape_ids = self._draw_rounded_rectangle(self.bg_color)
        
        self._bind_events(self.shape_ids)
        self._bind_events(self.text_id)

    def _animate_color_transition(self, target_color, duration=150, steps=10):
        if self.animation_id:
            self.after_cancel(self.animation_id)

        start_rgb = hex_to_rgb(self.current_color)
        target_rgb = hex_to_rgb(target_color)
        
        step_r = (target_rgb[0] - start_rgb[0]) / steps
        step_g = (target_rgb[1] - start_rgb[1]) / steps
        step_b = (target_rgb[2] - start_rgb[2]) / steps
        
        step_ms = duration // steps

        def step(current_step, current_rgb_float):
            if current_step >= steps:
                self.current_color = target_color
                self._set_color(target_color)
                self.animation_id = None
                return

            next_r_float = current_rgb_float[0] + step_r
            next_g_float = current_rgb_float[1] + step_g
            next_b_float = current_rgb_float[2] + step_b
            
            next_rgb_int = (
                max(0, min(255, int(next_r_float))),
                max(0, min(255, int(next_g_float))),
                max(0, min(255, int(next_b_float)))
            )
            
            next_color_hex = rgb_to_hex(next_rgb_int)
            self._set_color(next_color_hex)
            self.current_color = next_color_hex 

            self.animation_id = self.after(step_ms, lambda: step(current_step + 1, (next_r_float, next_g_float, next_b_float)))

        start_rgb_float = (float(start_rgb[0]), float(start_rgb[1]), float(start_rgb[2]))
        step(0, start_rgb_float)

    def _draw_rounded_rectangle(self, color):
        w, h, r = self.width, self.height, self.radius
        
        if r > w/2: r = w/2
        if r > h/2: r = h/2

        for shape_id in self.shape_ids:
            try:
                self.canvas.delete(shape_id)
            except tk.TclError:
                pass 

        x1, y1 = 0, 0
        x2, y2 = w, h
        
        new_shape_ids = []
        
        new_shape_ids.append(self.canvas.create_rectangle(x1 + r, y1, x2 - r, y2, fill=color, outline=color))
        new_shape_ids.append(self.canvas.create_rectangle(x1, y1 + r, x2, y2 - r, fill=color, outline=color))

        new_shape_ids.append(self.canvas.create_oval(x1, y1, x1 + 2*r, y1 + 2*r, fill=color, outline=color))
        new_shape_ids.append(self.canvas.create_oval(x2 - 2*r, y1, x2, y1 + 2*r, fill=color, outline=color))
        new_shape_ids.append(self.canvas.create_oval(x1, y2 - 2*r, x1 + 2*r, y2, fill=color, outline=color))
        new_shape_ids.append(self.canvas.create_oval(x2 - 2*r, y2 - 2*r, x2, y2, fill=color, outline=color))
        
        self.canvas.tag_raise(self.text_id)

        return new_shape_ids

    def _bind_events(self, tags):
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
            if self.animation_id:
                self.after_cancel(self.animation_id)
                self.animation_id = None
            
            self.command() 

            click_pulse_color = "#333333" if hex_to_rgb(self.hover_color)[0] > 100 else "#AAAAAA" 
            
            self._set_color(click_pulse_color)
            self.current_color = click_pulse_color
            self.update_idletasks()
                    
            self.after(100, lambda: self._animate_color_transition(self.hover_color)) 

    def _on_enter(self, event):
        self._animate_color_transition(self.hover_color)

    def _on_leave(self, event):
        self._animate_color_transition(self.bg_color)
        
    def _set_color(self, color):
        for shape_id in self.shape_ids:
            try:
                self.canvas.itemconfig(shape_id, fill=color, outline=color)
            except tk.TclError:
                pass 

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
            
            self.shape_ids = self._draw_rounded_rectangle(self.current_color)
            
            self._bind_events(self.shape_ids)

        except Exception as e:
            # Bỏ qua lỗi nếu canvas/widget bị hủy trong quá trình resize nhanh
            # print(f"Lỗi khi resize ShapeButton: {e}") # Bỏ comment nếu cần debug
            pass
# ===== KẾT THÚC LỚP NÚT BẤM =====



def open_main_window():

    # --- ĐỊNH NGHĨA MÀU SẮC CHO NÚT SIDEBAR ---
    btn_bg_color = "#16C92E"      
    btn_hover_color = "#083307"   
    
    # --- 1. CÀI ĐẶT CỬA SỔ CHÍNH ---
    root = tk.Tk()
    root.title("Hệ Thống Quản Lý Bệnh Nhân")
    
    # === THAY ĐỔI: Phóng to (Maximize) cửa sổ khi khởi động ===
    try:
        root.state('zoomed') # Dùng cho Windows
    except tk.TclError:
        root.attributes('-zoomed', True) # Dùng cho Mac/Linux
    
    # Không dùng center_window vì đã phóng to
    root.resizable(True, True)
    
    main_bg = "white"
    sidebar_bg = "#1287E0"
    root.config(bg=main_bg)
    sidebar_text_color = "#0e355c"

    # ===== TẢI DỮ LIỆU TỪ MYSQL LÊN "CACHE" (Giữ nguyên) =====
    khoa_data = []
    chucvu_data = []
    nhanvien_data = []
    benhnhan_data = []
    macbenh_data = []
    thuoc_data = []
    donthuoc_data = []
    chitietdonthuoc_data = []
    
    try:
        conn = connect_db()
        cursor = conn.cursor(dictionary=True) 
        
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
        
        
        cursor.execute("SELECT * FROM chitietdonthuoc") 
        chitietdonthuoc_data.extend(cursor.fetchall())
        
        
        cursor.close()
        conn.close()
        messagebox.showinfo("Khởi động", "Đã tải dữ liệu từ CSDL thành công!")
        
    except mysql.connector.Error as e:
        messagebox.showerror("Lỗi CSDL", f"Không thể tải dữ liệu khi khởi động.\nLỗi: {e}")
        root.destroy()
        return
    # ==========================================

    # --- 2. TẠO CÁC FRAME CHÍNH (Giữ nguyên) ---
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

    # --- HÀM SHOW TRANG CHỦ: ảnh làm background full, chữ nằm trên ảnh ---
    def show_trangchu_view():
        clear_main_frame()

        # Tạo canvas chiếm toàn bộ main_frame để vẽ ảnh nền và chữ lên trên
        canvas = tk.Canvas(main_frame, bg=main_bg, highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        # Các text sẽ được vẽ trên canvas (vị trí tương đối)
        title_font = ("Times New Roman", 34, "bold")
        subtitle_font = ("Times New Roman", 20)

        # Hàm tải ảnh (thử nhiều đường dẫn) và thay đổi kích thước theo canvas
        try:
            from PIL import Image, ImageTk

            def load_image_for_canvas(w, h):
                candidates = ["hero.jpg", "hero.png", "assets/hero.jpg", "assets/hero.png", "assets/back.jpg", "assets/back.png"]
                for p in candidates:
                    try:
                        img = Image.open(p)
                        # resize to cover canvas while keeping aspect (cover behavior)
                        img_ratio = img.width / img.height
                        canvas_ratio = w / h if h > 0 else img_ratio
                        if canvas_ratio > img_ratio:
                            # canvas is wider relative -> fit width
                            new_w = w
                            new_h = int(w / img_ratio)
                        else:
                            new_h = h
                            new_w = int(h * img_ratio)
                        img = img.resize((new_w, new_h), Image.LANCZOS)
                        return img
                    except Exception:
                        continue
                return None

            # Keep references on canvas to avoid GC
            canvas._bg_image = None

            def on_resize(event):
                w, h = event.width, event.height
                img = load_image_for_canvas(w, h)
                canvas.delete("bg")
                if img is not None:
                    # center-crop logic: image may be larger than canvas, so compute offset
                    photo = ImageTk.PhotoImage(img)
                    canvas._bg_image = photo
                    canvas.create_image(w//2, h//2, image=photo, anchor="center", tags=("bg",))
                # draw text on top (remove old)
                canvas.delete("title")
                # shadow for readability
                canvas.create_text(w//2+2, int(h*0.12)+2, text="TRANG CHỦ", font=title_font, fill="#000000", tags=("title",))
                canvas.create_text(w//2, int(h*0.12), text="TRANG CHỦ", font=title_font, fill="#ffffff", tags=("title",))
                canvas.create_text(w//2+1, int(h*0.22)+1, text="Chào mừng đến với Hệ thống Quản lý Bệnh nhân!", font=subtitle_font, fill="#000000", tags=("subtitle",))
                canvas.create_text(w//2, int(h*0.22), text="Chào mừng đến với Hệ thống Quản lý Bệnh nhân!", font=subtitle_font, fill="#ffffff", tags=("subtitle",))

            # gắn sự kiện resize để cập nhật ảnh
            canvas.bind("<Configure>", on_resize)

        except ImportError:
            # Nếu không có Pillow, chỉ hiển thị text và hướng dẫn
            canvas.create_text(500, 80, text="TRANG CHỦ", font=title_font, fill="#333", tags=("title",))
            canvas.create_text(500, 140, text="Chào mừng đến với Hệ thống Quản lý Bệnh nhân!", font=subtitle_font, fill="#333", tags=("subtitle",))
            canvas.create_text(500, 220, text="[Cài Pillow hoặc đặt 'hero.png' vào thư mục để có ảnh nền]", font=("Times New Roman", 14), fill="#666")

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
            radius=15 
        )
        btn.pack(fill="x", pady=4, padx=10)
        
    logout_btn = ShapeButton(
        frame_sidebar, text="Đăng xuất", command=on_logout,
        width=btn_width, height=btn_height,
        bg_color="#3D140F", hover_color="#4D1610", 
        radius=15
    )
    logout_btn.pack(side="bottom", fill="x", pady=20, padx=10)

    # --- 6. KIỂM TRA DB VÀ CHẠY ỨNG DỤNG ---
    show_trangchu_view()
    root.mainloop()

# --- ĐIỂM KHỞI CHẠY CHÍNH CỦA ỨNG DỤNG ---
if __name__ == "__main__":
    open_main_window()