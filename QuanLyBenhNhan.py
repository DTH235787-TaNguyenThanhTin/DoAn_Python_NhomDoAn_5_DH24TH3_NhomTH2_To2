import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector

# ====== Kết nối MySQL ======
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        port=3306,
        password="123456",  # sửa nếu cần
        database="quanlybenhnhan"
    )

# ====== Canh giữa cửa sổ ======
def center_window(win, w=900, h=550):
    ws = win.winfo_screenwidth()
    hs = win.winfo_screenheight()
    x = (ws // 2) - (w // 2)
    y = (hs // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

# ====== Giao diện chính ======
root = tk.Tk()
root.title("Quản lý bệnh nhân")
center_window(root)
root.resizable(False, False)

lbl_title = tk.Label(root, text="QUẢN LÝ BỆNH NHÂN", font=("Arial", 18, "bold"))
lbl_title.pack(pady=10)

# ====== Frame nhập ======
frame_info = tk.LabelFrame(root, text="Thông tin bệnh nhân", font=("Arial", 10, "bold"))
frame_info.pack(pady=5, padx=10, fill="x")

tk.Label(frame_info, text="Mã BN").grid(row=0, column=0, padx=5, pady=5, sticky="w")
entry_ma = tk.Entry(frame_info, width=10)
entry_ma.grid(row=0, column=1, padx=5, pady=5)

tk.Label(frame_info, text="Họ BN").grid(row=0, column=2, padx=5, pady=5, sticky="w")
entry_hobn = tk.Entry(frame_info, width=20)
entry_hobn.grid(row=0, column=3, padx=5, pady=5)

tk.Label(frame_info, text="Tên BN").grid(row=0, column=4, padx=5, pady=5, sticky="w")
entry_tenbn = tk.Entry(frame_info, width=15)
entry_tenbn.grid(row=0, column=5, padx=5, pady=5)

tk.Label(frame_info, text="Giới tính").grid(row=1, column=0, padx=5, pady=5, sticky="w")
gender_var = tk.StringVar(value="Nam")
tk.Radiobutton(frame_info, text="Nam", variable=gender_var, value="Nam").grid(row=1, column=1, sticky="w")
tk.Radiobutton(frame_info, text="Nữ", variable=gender_var, value="Nữ").grid(row=1, column=1, padx=60, sticky="w")

tk.Label(frame_info, text="Ngày sinh").grid(row=1, column=2, padx=5, pady=5, sticky="w")
date_entry = DateEntry(frame_info, width=12, background="darkblue", foreground="white", date_pattern="yyyy-mm-dd")
date_entry.grid(row=1, column=3, padx=5, pady=5, sticky="w")

tk.Label(frame_info, text="Tuổi").grid(row=1, column=4, padx=5, pady=5, sticky="w")
entry_tuoi = tk.Entry(frame_info, width=10)
entry_tuoi.grid(row=1, column=5, padx=5, pady=5)

tk.Label(frame_info, text="SĐT").grid(row=2, column=0, padx=5, pady=5, sticky="w")
entry_sdt = tk.Entry(frame_info, width=15)
entry_sdt.grid(row=2, column=1, padx=5, pady=5)

tk.Label(frame_info, text="Địa chỉ").grid(row=2, column=2, padx=5, pady=5, sticky="w")
entry_diachi = tk.Entry(frame_info, width=40)
entry_diachi.grid(row=2, column=3, columnspan=3, padx=5, pady=5, sticky="w")

# ====== Bảng danh sách ======
columns = ("MaBN", "HoBN", "TenBN", "GioiTinh", "TuoiBN", "SDTBN", "NgaySinh", "DiaChi")
tree = ttk.Treeview(root, columns=columns, show="headings", height=10)
tree.pack(padx=10, pady=10, fill="both")

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, width=110)

# ====== Chức năng ======
def clear_input():
    entry_ma.delete(0, tk.END)
    entry_hobn.delete(0, tk.END)
    entry_tenbn.delete(0, tk.END)
    entry_tuoi.delete(0, tk.END)
    entry_sdt.delete(0, tk.END)
    entry_diachi.delete(0, tk.END)
    gender_var.set("Nam")
    date_entry.set_date("2000-01-01")

def load_data():
    for i in tree.get_children():
        tree.delete(i)
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM benhnhan")
    for row in cur.fetchall():
        tree.insert("", tk.END, values=row)
    conn.close()

def them_bn():
    ma = entry_ma.get()
    ho = entry_hobn.get()
    ten = entry_tenbn.get()
    gt = gender_var.get()
    tuoi = entry_tuoi.get()
    sdt = entry_sdt.get()
    ns = date_entry.get()
    dc = entry_diachi.get()

    if not ma or not ho or not ten:
        messagebox.showwarning("Thiếu dữ liệu", "Vui lòng nhập đầy đủ thông tin.")
        return

    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO benhnhan (MaBN, HoBN, TenBN, GioiTinh, TuoiBN, SDTBN, NgaySinh, DiaChi)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (ma, ho, ten, gt, tuoi or None, sdt, ns, dc))
        conn.commit()
        conn.close()
        load_data()
        clear_input()
        messagebox.showinfo("Thành công", "Đã thêm bệnh nhân.")
    except Exception as e:
        messagebox.showerror("Lỗi", str(e))

def xoa_bn():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn bệnh nhân để xóa.")
        return
    ma = tree.item(selected)["values"][0]
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM benhnhan WHERE MaBN=%s", (ma,))
    conn.commit()
    conn.close()
    load_data()

def sua_bn():
    selected = tree.selection()
    if not selected:
        messagebox.showwarning("Chưa chọn", "Hãy chọn bệnh nhân để sửa.")
        return
    values = tree.item(selected)["values"]
    entry_ma.delete(0, tk.END)
    entry_ma.insert(0, values[0])
    entry_hobn.delete(0, tk.END)
    entry_hobn.insert(0, values[1])
    entry_tenbn.delete(0, tk.END)
    entry_tenbn.insert(0, values[2])
    gender_var.set(values[3])
    entry_tuoi.delete(0, tk.END)
    entry_tuoi.insert(0, values[4])
    entry_sdt.delete(0, tk.END)
    entry_sdt.insert(0, values[5])
    date_entry.set_date(values[6])
    entry_diachi.delete(0, tk.END)
    entry_diachi.insert(0, values[7])

def luu_bn():
    ma = entry_ma.get()
    ho = entry_hobn.get()
    ten = entry_tenbn.get()
    gt = gender_var.get()
    tuoi = entry_tuoi.get()
    sdt = entry_sdt.get()
    ns = date_entry.get()
    dc = entry_diachi.get()

    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        UPDATE benhnhan 
        SET HoBN=%s, TenBN=%s, GioiTinh=%s, TuoiBN=%s, SDTBN=%s, NgaySinh=%s, DiaChi=%s 
        WHERE MaBN=%s
    """, (ho, ten, gt, tuoi or None, sdt, ns, dc, ma))
    conn.commit()
    conn.close()
    load_data()
    clear_input()

# ====== Nút chức năng ======
frame_btn = tk.Frame(root)
frame_btn.pack(pady=5)

tk.Button(frame_btn, text="Thêm", width=10, command=them_bn).grid(row=0, column=0, padx=5)
tk.Button(frame_btn, text="Lưu", width=10, command=luu_bn).grid(row=0, column=1, padx=5)
tk.Button(frame_btn, text="Sửa", width=10, command=sua_bn).grid(row=0, column=2, padx=5)
tk.Button(frame_btn, text="Xóa", width=10, command=xoa_bn).grid(row=0, column=3, padx=5)
tk.Button(frame_btn, text="Hủy", width=10, command=clear_input).grid(row=0, column=4, padx=5)
tk.Button(frame_btn, text="Thoát", width=10, command=root.quit).grid(row=0, column=5, padx=5)

# ====== Load dữ liệu ban đầu ======
load_data()
root.mainloop()
