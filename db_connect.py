import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import mysql.connector

# ===== Kết nối MySQL =====
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",       # thay bằng user MySQL của bạn
        password="123456",       # thay bằng mật khẩu của bạn
        database="quanlybenhnhan"
    )
# ====== Hàm canh giữa cửa sổ ====== =
def center_window(win, w=700, h=500): 
    ws = win.winfo_screenwidth() 
    hs = win.winfo_screenheight() 
    x = (ws // 2) - (w // 2) 
    y = (hs // 2) - (h // 2) 
    win.geometry(f'{w}x{h}+{x}+{y}') 