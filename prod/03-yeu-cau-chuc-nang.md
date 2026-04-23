# 03 - Yeu cau chuc nang he thong quan ly sinh vien

## 1. Muc tieu
Xay dung he thong quan ly sinh vien voi 3 role chinh:
- `ADMIN`: quan tri toan bo he thong
- `SINH_VIEN`: xem bang diem, dang ky hoc phan, xem mon da dang ky
- `GIANG_VIEN`: quan ly lop cua toi, diem danh, nhap/sua diem cho sinh vien trong lop

## 2. Pham vi nghiep vu
- Quan tri sinh vien: them/sua/xoa mem, tim kiem
- Quan tri hoc phan va lop hoc phan
- Dang ky hoc phan theo lop HP
- Nhap/sua diem va tinh GPA tu dong
- Diem danh theo buoi hoc
- Bao cao bang diem ca nhan va xuat CSV

## 3. Thuc the du lieu chinh
- `UserProfile(user, role, status, student?)`
- `Student(ma_sv, ho_ten, ..., trang_thai)`
- `Course(ma_hp, ten_hp, so_tin_chi)`
- `Classroom(ma_lop_hp, course, giang_vien, hoc_ky, nam_hoc, si_so_toi_da, trang_thai)`
- `Enrollment(student, classroom, course, hoc_ky, nam_hoc, trang_thai)`
- `Grade(enrollment, diem_chuyen_can, diem_qua_trinh, diem_thi, diem_tong_ket_10, diem_he_4, diem_chu, lan_hoc)`
- `Attendance(classroom, enrollment, ngay_hoc, trang_thai, ghi_chu)`
- `GPASemester`, `AcademicStanding`, `ClassificationRule`, `AuditLog`

## 4. Yeu cau chuc nang chi tiet

### 4.1 ADMIN
- Quan tri ho so sinh vien, hoc phan, lop hoc phan.
- Tao dang ky hoc phan cho sinh vien.
- Nhap/sua diem.
- Theo doi audit log va bao cao.

### 4.2 SINH_VIEN
- Xem danh sach mon da dang ky.
- Dang ky hoc phan theo lop HP con mo.
- Xem bang diem va GPA cua chinh minh.

Rang buoc dang ky:
- Khong dang ky trung hoc phan trong cung hoc ky + nam hoc.
- Khong dang ky lop HP da du si so toi da hoac da dong.

### 4.3 GIANG_VIEN
- Xem "Lop cua toi" (lop HP duoc phan cong).
- Xem danh sach sinh vien trong tung lop.
- Diem danh theo ngay hoc.
- Nhap/sua diem cho sinh vien trong lop do.

Rang buoc quyen:
- Giang vien chi thao tac du lieu thuoc lop HP do minh phu trach.

### 4.4 Tinh diem, GPA, xep loai
Cong thuc diem tong ket:
- `diem_tong_ket_10 = diem_chuyen_can * 0.1 + diem_qua_trinh * 0.3 + diem_thi * 0.6`

Rang buoc diem:
- Moi cot diem trong khoang `0 -> 10`.
- Moi ban ghi diem gan voi 1 dang ky hoc phan hop le.
- Cho phep nhieu lan hoc, GPA tinh theo lan moi nhat cua tung hoc phan.

Cong thuc GPA:
- `GPA = SUM(diem_he_4 * so_tin_chi) / SUM(so_tin_chi)`
- Lam tron 2 chu so thap phan.

Nguong xep loai mac dinh:
- `>= 3.60`: Xuat sac
- `3.20 - 3.59`: Gioi
- `2.50 - 3.19`: Kha
- `2.00 - 2.49`: Trung binh
- `< 2.00`: Yeu

### 4.5 Bao cao
- Bao cao bang diem ca nhan tren web.
- Xuat CSV bang diem.

## 5. Yeu cau phi chuc nang
- RBAC theo role.
- Toan ven du lieu bang rang buoc khoa ngoai + unique constraints.
- Ghi audit log cho thao tac nghiep vu.
- He thong van hanh tren SQLite va co the chuyen sang SQL engine khac.

## 6. Tieu chi nghiem thu
- Chuc nang 3 role hoat dong dung quyen.
- Luong dang ky hoc phan, diem danh, nhap/sua diem van hanh thong suot.
- GPA va xep loai cap nhat dung sau moi lan luu diem.
- Bao cao bang diem va file CSV xuat dung du lieu.
