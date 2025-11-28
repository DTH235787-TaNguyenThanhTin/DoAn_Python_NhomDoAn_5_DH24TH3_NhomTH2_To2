import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkcalendar import DateEntry
import datetime
# --- Import CSDL ---
from db_connect import connect_db 
import mysql.connector

# Ghi chú: Đã điều chỉnh tham số đầu vào để khớp với cách gọi trong main.py
def create_view(parent_tab, chitietbenhnhan_data, benhnhan_data, macbenh_data, nhanvien_data):
    """
    Tạo giao diện cho tab Chi Tiết Bệnh Nhân (Lịch sử khám/điều trị) (Master-Detail).
    Master: Bệnh Nhân (MaBN)
    Detail: Chi Tiết Bệnh Nhân (Lần khám/điều trị)
    """

    # --- Biến nội bộ ---
    current_mode_detail = None
    # Khóa chính của chitietbenhnhan là MaCTBN (ID tự tăng)
    selected_detail_pk = None # Lưu khóa chính MaCTBN của dòng đang chọn
    current_master_mabn = None # Mã Bệnh Nhân đang được xem

    # --- Hàm Helper (Hàm trợ giúp) ---
    def find_item_by_key(data_list, key, value):
        # Tìm một dict (item) trong list dựa vào key và value.
        for item in data_list:
            if item.get(key) == value:
                return item
        return None # Trả về None nếu không tìm thấy

    # --- Các hàm xử lý (nội bộ) ---
    def refresh_tree(filter_mabn):
        """
        Làm mới Treeview (bảng lịch sử khám).
        CHỈ hiển thị các chi tiết (lần khám) thuộc về filter_mabn (Mã Bệnh Nhân).
        """
        # Xóa tất cả các hàng cũ
        for item in tree.get_children():
            tree.delete(item)

        # Lọc danh sách chitietbenhnhan_data (cache)
        filtered_details = [item for item in chitietbenhnhan_data if item['MaBN'] == filter_mabn]

        # Thêm lại các hàng đã lọc
        for item in filtered_details:
            # Tìm Tên Bệnh và Tên Nhân Viên từ Mã tương ứng
            macbenh_item = find_item_by_key(macbenh_data, 'MaBenh', item['MaBenh'])
            loai_benh = macbenh_item['LoaiBenh'] if macbenh_item else "Không rõ"

            nhanvien_item = find_item_by_key(nhanvien_data, 'MaNV', item['MaNV'])
            ten_nv = nhanvien_item['HoTenNV'] if nhanvien_item else "Không rõ"

            # Định dạng ngày
            ngay_kham_display = item['NgayKham'].strftime('%Y-%m-%d') if isinstance(item['NgayKham'], (datetime.date, datetime.datetime)) else item['NgayKham']

            # Chèn vào Treeview
            # PK (iid) là MaCTBN (phải là string)
            tree.insert("", tk.END, iid=str(item['MaCTBN']), values=(
                item['MaCTBN'],
                item['MaBenh'],
                loai_benh,
                item['MaNV'],
                ten_nv,
                ngay_kham_display,
                item['ChanDoan'],
                item['KetQua']
            ))

    def update_master_comboboxes():
        """Cập nhật combobox Mã Bệnh Nhân (master)."""
        # Tải danh sách MaBN từ cache
        bn_display_list = [f"{bn['MaBN']}" for bn in benhnhan_data]
        combo_mabn_master.config(values=bn_display_list)

    def update_detail_comboboxes():
        """Cập nhật 2 combobox Mã Bệnh và Tên Bệnh (detail)."""
        # Tải danh sách MaBenh
        mabenh_display_list = [mb['MaBenh'] for mb in macbenh_data]
        combo_mabenh.config(values=mabenh_display_list)

        # Tải danh sách Tên Bệnh
        loaibenh_display_list = [mb['LoaiBenh'] for mb in macbenh_data]
        combo_loaibenh.config(values=loaibenh_display_list)

        # Tải danh sách Mã Nhân Viên (Bác sĩ khám)
        manv_display_list = [nv['MaNV'] for nv in nhanvien_data]
        combo_manv.config(values=manv_display_list)

    # --- Quản lý trạng thái Form ---

    def set_master_form_state(state):
        """Bật/tắt các ô thông tin bệnh nhân. state là 'normal' hoặc 'disabled'."""
        final_state = 'normal'
        if state == 'disabled':
            final_state = 'readonly' # Dùng 'readonly' để người dùng có thể copy text

        # Các ô thông tin Bệnh Nhân
        entry_tenbn.config(state=final_state)
        entry_gtbn.config(state=final_state)
        entry_tuoibn.config(state=final_state)
        entry_sdtbn.config(state=final_state)
        entry_ngaysinhbn.config(state=final_state)
        entry_diachibn.config(state=final_state)
        entry_mabenh_bn.config(state=final_state)


    def set_detail_form_state(state):
        """Bật/tắt form chi tiết (lần khám). state là 'add', 'edit', 'normal', 'disabled'."""
        pk_state = 'disabled' # Trạng thái cho Mã Bệnh, Mã NV
        other_state = 'disabled' # Trạng thái cho các ô còn lại

        if state == 'add':
            # Khi thêm, cho phép chọn Mã Bệnh, Mã NV (readonly)
            pk_state = 'readonly'
            other_state = 'normal'
        elif state == 'edit':
            # Khi sửa, khóa Mã Bệnh, Mã NV (vì là khóa chính/tham chiếu không nên sửa)
            pk_state = 'disabled'
            other_state = 'normal'
        elif state == 'normal':
            # Trạng thái 'normal' (dùng khi clear form)
            pk_state = 'normal'
            other_state = 'normal'

        # Áp dụng cho các Combobox (PK)
        combo_mabenh.config(state=pk_state)
        combo_loaibenh.config(state=pk_state)
        combo_manv.config(state=pk_state)

        # Áp dụng cho các ô còn lại
        entry_chandoan.config(state=other_state)
        entry_ketqua.config(state=other_state)

        # state cho DateEntry là 'normal' hoặc 'disabled'
        date_state = 'normal' if other_state == 'normal' else 'disabled'
        cal_ngaykham.config(state=date_state)

    def set_detail_button_state(state):
        """Bật/tắt 5 nút Thêm, Sửa, Lưu, Xóa, Bỏ qua (của form chi tiết)."""
        btn_them.config(state='normal' if state == 'idle' else 'disabled')
        btn_sua.config(state='normal' if state == 'selected' else 'disabled')
        btn_luu.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')
        btn_xoa.config(state='normal' if state == 'selected' else 'disabled')
        btn_boqua.config(state='normal' if state == 'add' or state == 'edit' else 'disabled')

    def clear_master_form():
        """Xóa trắng form thông tin Bệnh Nhân (master)."""
        set_master_form_state('normal')
        entry_tenbn.delete(0, tk.END)
        entry_gtbn.delete(0, tk.END)
        entry_tuoibn.delete(0, tk.END)
        entry_sdtbn.delete(0, tk.END)
        entry_ngaysinhbn.delete(0, tk.END)
        entry_diachibn.delete(0, tk.END)
        entry_mabenh_bn.delete(0, tk.END)
        set_master_form_state('disabled')

    def clear_detail_form():
        """Xóa trắng form chi tiết lần khám (hàm Bỏ qua)."""
        nonlocal current_mode_detail, selected_detail_pk
        # Reset biến trạng thái
        current_mode_detail = None
        selected_detail_pk = None

        # Mở khóa tạm thời để xóa
        set_detail_form_state('normal')
        combo_mabenh.set("")
        combo_loaibenh.set("")
        combo_manv.set("")
        entry_chandoan.delete(0, tk.END)
        entry_ketqua.delete(0, tk.END)
        cal_ngaykham.set_date(datetime.date.today())

        # Khóa lại form chi tiết
        set_detail_form_state('disabled')
        # Đặt lại trạng thái nút
        set_detail_button_state('idle' if current_master_mabn else 'disabled')

        # Bỏ chọn hàng trên Treeview
        if tree.selection():
            tree.selection_remove(tree.selection())

    # --- CÁC HÀM NÚT BẤM CHÍNH ---

    def on_xem_benhnhan():
        """
        Nút "Xem Bệnh Nhân".
        Tải thông tin Master (Bệnh Nhân) lên Form 1.
        Lọc và tải Treeview (Lịch sử khám) theo Mã BN đã chọn.
        """
        nonlocal current_master_mabn
        mabn = combo_mabn_master.get() # Lấy MaBN từ combobox master
        if not mabn:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một Mã Bệnh Nhân.")
            return

        # Tìm bệnh nhân trong cache benhnhan_data
        benhnhan_item = find_item_by_key(benhnhan_data, 'MaBN', mabn)
        if not benhnhan_item:
            messagebox.showerror("Lỗi", "Không tìm thấy bệnh nhân này.")
            return

        # Lưu lại MaBN đang xem
        current_master_mabn = mabn

        # 1. Tải thông tin bệnh nhân
        clear_master_form() # Xóa và khóa lại form master
        set_master_form_state('normal') # Mở khóa để nạp

        # Định dạng ngày sinh
        ngay_sinh_display = benhnhan_item['NgaySinh'].strftime('%Y-%m-%d') if isinstance(benhnhan_item['NgaySinh'], (datetime.date, datetime.datetime)) else benhnhan_item['NgaySinh']

        # Tìm Loại Bệnh hiện tại
        mabenh_bn = benhnhan_item['MaBenh']
        mabenh_item = find_item_by_key(macbenh_data, 'MaBenh', mabenh_bn)
        loai_benh_hientai = mabenh_item['LoaiBenh'] if mabenh_item else mabenh_bn

        entry_tenbn.insert(0, benhnhan_item['HoTenBN'] or "")
        entry_gtbn.insert(0, benhnhan_item['GioiTinhBN'] or "")
        entry_tuoibn.insert(0, benhnhan_item['TuoiBN'] or "")
        entry_sdtbn.insert(0, benhnhan_item['SDTBN'] or "")
        entry_ngaysinhbn.insert(0, ngay_sinh_display or "")
        entry_diachibn.insert(0, benhnhan_item['DiaChiBN'] or "")
        entry_mabenh_bn.insert(0, loai_benh_hientai or "")

        # Khóa lại form master SAU KHI đã điền
        set_master_form_state('disabled')

        # 2. Tải chi tiết (Treeview)
        refresh_tree(current_master_mabn)

        # 3. Kích hoạt các nút chi tiết
        clear_detail_form() # Xóa form chi tiết (nếu có)
        set_detail_button_state('idle') # Bật nút "Thêm" của form chi tiết

    # --- CÁC HÀM NÚT BẤM (CHI TIẾT LẦN KHÁM) ---
    def on_add_detail():
        """Nút 'Thêm' (chi tiết) - Kích hoạt chế độ thêm lần khám."""
        nonlocal current_mode_detail
        # Phải chọn "Xem Bệnh Nhân" trước
        if not current_master_mabn:
            messagebox.showwarning("Lỗi", "Vui lòng 'Xem Bệnh Nhân' trước khi thêm lịch sử khám.")
            return

        clear_detail_form() # Xóa form chi tiết
        current_mode_detail = 'add' # Đặt chế độ 'thêm'
        set_detail_form_state('add') # Mở khóa form chi tiết
        set_detail_button_state('add') # Bật nút 'Lưu', 'Bỏ qua'
        combo_mabenh.focus() # Di chuyển con trỏ vào combo Mã Bệnh

    def on_edit_detail():
        """Nút 'Sửa' (chi tiết) - Kích hoạt chế độ sửa lần khám."""
        nonlocal current_mode_detail
        # Phải chọn 1 dòng trong Treeview trước
        if not selected_detail_pk:
            messagebox.showwarning("Lỗi", "Vui lòng chọn một dòng lịch sử khám trong bảng để sửa.")
            return

        current_mode_detail = 'edit' # Đặt chế độ 'sửa'
        set_detail_form_state('edit') # Mở khóa form (nhưng khóa Mã Bệnh, Mã NV)
        set_detail_button_state('edit') # Bật nút 'Lưu', 'Bỏ qua'
        cal_ngaykham.focus() # Di chuyển con trỏ vào ô Ngày Khám

    def on_save_detail():
        """Nút 'Lưu' (chi tiết) - Lưu chi tiết lần khám (thêm mới hoặc cập nhật)."""
        nonlocal current_mode_detail, selected_detail_pk, current_master_mabn

        # Lấy dữ liệu từ Form
        mabenh = combo_mabenh.get().strip()
        manv = combo_manv.get().strip()
        ngay_kham = cal_ngaykham.get_date()
        chan_doan = entry_chandoan.get().strip() or None
        ket_qua = entry_ketqua.get().strip() or None

        # Kiểm tra dữ liệu bắt buộc
        if not mabenh:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Mã Bệnh.")
            return
        if not manv:
            messagebox.showwarning("Thiếu thông tin", "Vui lòng chọn Mã Nhân Viên (Bác sĩ).")
            return
        if not ngay_kham:
            messagebox.showwarning("Thiếu thông tin", "Ngày khám là bắt buộc.")
            return

        conn = None
        cursor = None
        try:
            # 1. Kết nối CSDL
            conn = connect_db()
            if conn is None:
                messagebox.showerror("Lỗi", "Không thể kết nối CSDL.")
                return
            cursor = conn.cursor()

            # 2. Xử lý logic Thêm
            if current_mode_detail == 'add':
                # 2a. Thêm vào CSDL
                sql = """
                    INSERT INTO chitietbenhnhan (MaBN, MaBenh, MaNV, NgayKham, ChanDoan, KetQua)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """
                cursor.execute(sql, (current_master_mabn, mabenh, manv, ngay_kham, chan_doan, ket_qua))
                new_id = cursor.lastrowid # Lấy ID tự tăng

                # 2b. Thêm vào cache
                new_item = {
                    'MaCTBN': new_id, 'MaBN': current_master_mabn, 'MaBenh': mabenh,
                    'MaNV': manv, 'NgayKham': ngay_kham, 'ChanDoan': chan_doan, 'KetQua': ket_qua
                }
                chitietbenhnhan_data.append(new_item)
                messagebox.showinfo("Thành công", f"Đã thêm lần khám mới (ID: {new_id}) cho BN {current_master_mabn}.")

            # 3. Xử lý logic Sửa
            elif current_mode_detail == 'edit':
                # Lấy MaCTBN đã lưu
                mactbn_edit = selected_detail_pk

                # 3a. Cập nhật CSDL
                sql = """
                    UPDATE chitietbenhnhan SET
                    NgayKham = %s, ChanDoan = %s, KetQua = %s
                    WHERE MaCTBN = %s
                """
                # Lưu ý: Không sửa MaBenh, MaNV vì đây là chi tiết lần khám cố định
                cursor.execute(sql, (ngay_kham, chan_doan, ket_qua, mactbn_edit))

                # 3b. Cập nhật cache
                for item in chitietbenhnhan_data:
                    if item['MaCTBN'] == mactbn_edit:
                        item['NgayKham'] = ngay_kham
                        item['ChanDoan'] = chan_doan
                        item['KetQua'] = ket_qua
                        break
                messagebox.showinfo("Thành công", f"Đã cập nhật chi tiết lần khám (ID: {mactbn_edit}).")

            # 4. Lưu CSDL
            conn.commit()

            # 5. Cập nhật giao diện
            refresh_tree(current_master_mabn)
            clear_detail_form()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi lưu chi tiết bệnh nhân:\n{e}")
        finally:
            # 6. Luôn đóng CSDL
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    def on_delete_detail():
        """Nút 'Xóa' (chi tiết) - Xóa lần khám khỏi lịch sử."""
        if not selected_detail_pk:
            messagebox.showwarning("Chưa chọn", "Vui lòng chọn một dòng lịch sử khám trong bảng để Xóa.")
            return

        # Lấy PK từ biến đã lưu (MaCTBN)
        mactbn_del = selected_detail_pk

        # Xác nhận
        if not messagebox.askyesno("Xác nhận", f"Bạn có chắc muốn xóa lần khám ID {mactbn_del} của bệnh nhân {current_master_mabn}?"):
            return

        conn = None
        cursor = None
        try:
            # 1. Kết nối CSDL
            conn = connect_db()
            if conn is None:
                messagebox.showerror("Lỗi", "Không thể kết nối CSDL.")
                return
            cursor = conn.cursor()

            # 2. Xóa khỏi CSDL
            sql_delete = "DELETE FROM chitietbenhnhan WHERE MaCTBN = %s"
            cursor.execute(sql_delete, (mactbn_del,))
            conn.commit()

            # 3. Xóa khỏi cache
            item_to_remove = None
            for item in chitietbenhnhan_data:
                if item['MaCTBN'] == mactbn_del:
                    item_to_remove = item
                    break
            if item_to_remove:
                chitietbenhnhan_data.remove(item_to_remove)

            messagebox.showinfo("Thành công", f"Đã xóa chi tiết lần khám ID {mactbn_del}.")

            # 4. Cập nhật giao diện
            refresh_tree(current_master_mabn)
            clear_detail_form()

        except mysql.connector.Error as e:
            messagebox.showerror("Lỗi CSDL", f"Lỗi khi xóa dữ liệu:\n{e}")
        finally:
            # 5. Luôn đóng CSDL
            if cursor: cursor.close()
            if conn and conn.is_connected(): conn.close()

    # --- Sự kiện Combobox Bệnh và Nhân Viên ---
    def on_mabenh_select(event):
        """Sự kiện khi chọn 1 mục trong COMBO MÃ BỆNH."""
        mabenh = combo_mabenh.get()
        thuoc_item = find_item_by_key(macbenh_data, 'MaBenh', mabenh)
        if thuoc_item:
            combo_loaibenh.set(thuoc_item['LoaiBenh'])
        else:
            combo_loaibenh.set("")

    def on_loaibenh_select(event):
        """Sự kiện khi chọn 1 mục trong COMBO LOẠI BỆNH."""
        loaibenh = combo_loaibenh.get()
        thuoc_item = find_item_by_key(macbenh_data, 'LoaiBenh', loaibenh)
        if thuoc_item:
            combo_mabenh.set(thuoc_item['MaBenh'])
        else:
            combo_mabenh.set("")

    def on_manv_select(event):
        """Sự kiện khi chọn 1 mục trong COMBO MÃ NV (Bác sĩ)."""
        # Đây là Mã NV, ta có thể dùng để điền Tên NV (tùy chọn)
        manv = combo_manv.get()
        nhanvien_item = find_item_by_key(nhanvien_data, 'MaNV', manv)
        if nhanvien_item:
            # Có thể thêm một Label/Entry Tên NV nếu cần
            print(f"Bác sĩ được chọn: {nhanvien_item['HoTenNV']}")
        # Tuy nhiên, trong form chi tiết này chỉ cần lưu MaNV là đủ

    def on_detail_item_select(event):
        """Sự kiện khi click vào 1 dòng lịch sử khám trong Treeview."""
        nonlocal selected_detail_pk

        selected_items = tree.selection()

        if current_mode_detail in ('add', 'edit'):
            return

        if not selected_items:
            clear_detail_form()
            set_detail_button_state('idle' if current_master_mabn else 'disabled')
            return

        # 1. Lấy PK (MaCTBN)
        item_id_str = selected_items[0]
        try:
            mactbn_sel = int(item_id_str)
        except ValueError:
            return # Bỏ qua nếu không phải ID hợp lệ

        # Lưu PK vào biến
        selected_detail_pk = mactbn_sel

        # 2. Tìm item đầy đủ trong cache chitietbenhnhan_data
        item_data_dict = find_item_by_key(chitietbenhnhan_data, 'MaCTBN', mactbn_sel)

        if not item_data_dict: return

        # 3. Nạp dữ liệu lên form chi tiết
        set_detail_form_state('normal')

        # Nạp Mã Bệnh/Loại Bệnh
        mabenh_item = find_item_by_key(macbenh_data, 'MaBenh', item_data_dict['MaBenh'])
        if mabenh_item:
            combo_mabenh.set(mabenh_item['MaBenh'])
            combo_loaibenh.set(mabenh_item['LoaiBenh'])
        else:
            combo_mabenh.set(item_data_dict['MaBenh'])
            combo_loaibenh.set("Không rõ")

        # Nạp Mã NV
        combo_manv.set(item_data_dict['MaNV'])

        # Nạp các ô còn lại
        entry_chandoan.delete(0, tk.END)
        entry_ketqua.delete(0, tk.END)
        entry_chandoan.insert(0, item_data_dict['ChanDoan'] or "")
        entry_ketqua.insert(0, item_data_dict['KetQua'] or "")

        # Xử lý nạp ngày
        ngay_kham = item_data_dict['NgayKham']
        if isinstance(ngay_kham, (datetime.date, datetime.datetime)):
            cal_ngaykham.set_date(ngay_kham)
        else:
            cal_ngaykham.set_date(datetime.date.today())

        # 4. Khóa form
        set_detail_form_state('disabled')
        # 5. Bật nút 'Sửa', 'Xóa'
        set_detail_button_state('selected')

    # --- GIAO DIỆN ---
# --- Frame 4: Nút bấm (Detail Buttons) ---
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    # ===== SỬA LỖI BỐ CỤC: Đổi side=tk.CENTER thành side=tk.LEFT =====
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

    # --- Frame 1: Thông tin Bệnh Nhân (Master) ---
    master_frame = ttk.LabelFrame(parent_tab, text="Thông tin Bệnh Nhân")
    master_frame.pack(fill="x", expand=False, padx=10, pady=10)

    # Dòng 0: Chọn Mã Bệnh Nhân
    ttk.Label(master_frame, text="Mã Bệnh Nhân:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_mabn_master = ttk.Combobox(master_frame, width=15, state="readonly")
    combo_mabn_master.grid(row=0, column=1, padx=5, pady=5, sticky="w")

    btn_xem_bn = ttk.Button(master_frame, text="Xem Bệnh Nhân", command=on_xem_benhnhan)
    btn_xem_bn.grid(row=0, column=2, padx=5, pady=5, sticky="w")

    # Các ô thông tin Bệnh Nhân (chỉ để xem)
    ttk.Label(master_frame, text="Tên BN:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    entry_tenbn = ttk.Entry(master_frame, width=30)
    entry_tenbn.grid(row=1, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(master_frame, text="Giới Tính:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_gtbn = ttk.Entry(master_frame, width=30)
    entry_gtbn.grid(row=2, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(master_frame, text="Tuổi:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_tuoibn = ttk.Entry(master_frame, width=30)
    entry_tuoibn.grid(row=3, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(master_frame, text="SĐT:").grid(row=4, column=0, padx=5, pady=5, sticky="w")
    entry_sdtbn = ttk.Entry(master_frame, width=30)
    entry_sdtbn.grid(row=4, column=1, padx=5, pady=5, sticky="w")

    ttk.Label(master_frame, text="Ngày Sinh:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    entry_ngaysinhbn = ttk.Entry(master_frame, width=30)
    entry_ngaysinhbn.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    ttk.Label(master_frame, text="Địa chỉ:").grid(row=2, column=2, padx=5, pady=5, sticky="w")
    entry_diachibn = ttk.Entry(master_frame, width=30)
    entry_diachibn.grid(row=2, column=3, padx=5, pady=5, sticky="w")

    ttk.Label(master_frame, text="Mã Bệnh Hiện Tại:").grid(row=3, column=2, padx=5, pady=5, sticky="w")
    entry_mabenh_bn = ttk.Entry(master_frame, width=30)
    entry_mabenh_bn.grid(row=3, column=3, padx=5, pady=5, sticky="w")

    # --- Frame 2: Chi Tiết Lần Khám (Detail Form) ---
    detail_form_frame = ttk.LabelFrame(parent_tab, text="Thêm/Sửa Lịch Sử Khám")
    detail_form_frame.pack(fill="x", expand=False, padx=10, pady=10)

    # Dòng 0: Mã Bệnh và Mã NV
    ttk.Label(detail_form_frame, text="Mã Bệnh:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
    combo_mabenh = ttk.Combobox(detail_form_frame, width=15, state="readonly")
    combo_mabenh.grid(row=0, column=1, padx=5, pady=5, sticky="w")
    combo_mabenh.bind("<<ComboboxSelected>>", on_mabenh_select)

    ttk.Label(detail_form_frame, text="Loại Bệnh:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
    combo_loaibenh = ttk.Combobox(detail_form_frame, width=30, state="readonly")
    combo_loaibenh.grid(row=0, column=3, padx=5, pady=5, sticky="w")
    combo_loaibenh.bind("<<ComboboxSelected>>", on_loaibenh_select)

    ttk.Label(detail_form_frame, text="Mã NV (Bác sĩ):").grid(row=1, column=0, padx=5, pady=5, sticky="w")
    combo_manv = ttk.Combobox(detail_form_frame, width=15, state="readonly")
    combo_manv.grid(row=1, column=1, padx=5, pady=5, sticky="w")
    combo_manv.bind("<<ComboboxSelected>>", on_manv_select)

    ttk.Label(detail_form_frame, text="Ngày Khám:").grid(row=1, column=2, padx=5, pady=5, sticky="w")
    cal_ngaykham = DateEntry(detail_form_frame, width=28, date_pattern='yyyy-mm-dd', state='disabled')
    cal_ngaykham.grid(row=1, column=3, padx=5, pady=5, sticky="w")

    # Dòng 2: Chẩn Đoán và Kết Quả
    ttk.Label(detail_form_frame, text="Chẩn Đoán:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
    entry_chandoan = ttk.Entry(detail_form_frame, width=30)
    entry_chandoan.grid(row=2, column=1, columnspan=3, padx=5, pady=5, sticky="ew") # Chiếm 3 cột

    ttk.Label(detail_form_frame, text="Kết Quả:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
    entry_ketqua = ttk.Entry(detail_form_frame, width=30)
    entry_ketqua.grid(row=3, column=1, columnspan=3, padx=5, pady=5, sticky="ew") # Chiếm 3 cột

    # --- Frame 3: Treeview (Lịch Sử Khám) ----
    tree_frame = ttk.Frame(parent_tab)
    tree_frame.pack(fill="both", expand=True, padx=10, pady=10)

    tree_scroll_y = ttk.Scrollbar(tree_frame, orient="vertical")
    tree_scroll_y.pack(side="right", fill="y")
    tree_scroll_x = ttk.Scrollbar(tree_frame, orient="horizontal")
    tree_scroll_x.pack(side="bottom", fill="x")

    # Các cột trong bảng chi tiết bệnh nhân
    tree_cols = ("MaCTBN", "MaBenh", "LoaiBenh", "MaNV", "TenNV", "NgayKham", "ChanDoan", "KetQua")
    tree = ttk.Treeview(
        tree_frame, columns=tree_cols, show="headings",
        yscrollcommand=tree_scroll_y.set, xscrollcommand=tree_scroll_x.set
    )
    tree_scroll_y.config(command=tree.yview)
    tree_scroll_x.config(command=tree.xview)

    # Đặt tiêu đề
    tree.heading("MaCTBN", text="ID Lần Khám")
    tree.heading("MaBenh", text="Mã Bệnh")
    tree.heading("LoaiBenh", text="Loại Bệnh")
    tree.heading("MaNV", text="Mã BS")
    tree.heading("TenNV", text="Tên BS")
    tree.heading("NgayKham", text="Ngày Khám")
    tree.heading("ChanDoan", text="Chẩn Đoán")
    tree.heading("KetQua", text="Kết Quả")

    # Đặt độ rộng
    tree.column("MaCTBN", width=80, anchor="c")
    tree.column("MaBenh", width=70, anchor="c")
    tree.column("LoaiBenh", width=120, anchor="w")
    tree.column("MaNV", width=60, anchor="c")
    tree.column("TenNV", width=120, anchor="w")
    tree.column("NgayKham", width=90, anchor="c")
    tree.column("ChanDoan", width=150, anchor="w")
    tree.column("KetQua", width=150, anchor="w")

    tree.pack(fill="both", expand=True)
    tree.bind("<<TreeviewSelect>>", on_detail_item_select)

    # --- Frame 4: Nút bấm (Detail Buttons) ---
    button_frame = tk.Frame(parent_tab)
    button_frame.pack(pady=10, fill="x")

    # ===== SỬA LỖI BỐ CỤC: Đổi side=tk.CENTER thành side=tk.LEFT =====
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
    update_master_comboboxes() # Tải Mã BN
    update_detail_comboboxes() # Tải Mã Bệnh / Loại Bệnh / Mã NV

    # 2. Xóa và khóa form master
    clear_master_form()

    # 3. Xóa và khóa form chi tiết và các nút
    clear_detail_form()