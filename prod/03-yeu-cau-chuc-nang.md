# 03 - Yeu cau chuc nang he thong quan ly sinh vien

## 1. Muc tieu
Xay dung he thong quan ly sinh vien cho phong dao tao, tap trung vao 5 nhom chuc nang:
- Them / sua / xoa sinh vien
- Nhap diem, tinh GPA
- Xep loai hoc luc
- Tim kiem sinh vien
- Xuat bao cao

## 2. Doi tuong su dung
- Quan tri he thong: quan ly tai khoan, phan quyen.
- Can bo dao tao: quan ly ho so sinh vien, nhap/sua diem, xuat bao cao.
- Giang vien: nhap diem hoc phan duoc phan cong.
- Co van hoc tap (read-only): tra cuu thong tin sinh vien, ket qua hoc tap.

## 3. Thuc the du lieu chinh
- SinhVien(ma_sv, ho_ten, ngay_sinh, gioi_tinh, email, so_dien_thoai, khoa, nganh, lop, khoa_hoc, trang_thai)
- HocPhan(ma_hp, ten_hp, so_tin_chi)
- DangKyHocPhan(id, ma_sv, ma_hp, hoc_ky, nam_hoc)
- Diem(id, dang_ky_id, diem_qua_trinh, diem_thi, diem_tong_ket_10, diem_he_4, diem_chu, lan_hoc)
- GPAHocKy(id, ma_sv, hoc_ky, nam_hoc, gpa_he_4, tong_tin_chi_tich_luy)
- NguoiDung(id, username, vai_tro, trang_thai)

## 4. Yeu cau chuc nang chi tiet

### 4.1 Them / sua / xoa sinh vien
Mo ta:
- Tao moi ho so sinh vien voi ma sinh vien duy nhat.
- Cap nhat thong tin ho so.
- Khoa mem (soft delete) thay vi xoa cung de bao toan lich su hoc tap.

Rule:
- `ma_sv` duy nhat toan he thong.
- Email dung dinh dang va khong trung.
- Khong cho xoa cung neu sinh vien da co lich su diem.

API goi y:
- `POST /api/students`
- `GET /api/students/{ma_sv}`
- `PUT /api/students/{ma_sv}`
- `DELETE /api/students/{ma_sv}` (soft delete)

Tieu chi chap nhan:
- Tao moi thanh cong khi du lieu hop le.
- Bao loi ro rang khi trung `ma_sv` hoac email.
- Ban ghi bi xoa mem khong hien trong danh sach mac dinh, nhung van co the truy vet lich su.

### 4.2 Nhap diem, tinh GPA
Mo ta:
- Nhap diem qua trinh va diem thi cho tung hoc phan.
- Tu dong tinh diem tong ket he 10, quy doi he 4 va diem chu.
- Tu dong tinh GPA hoc ky va GPA tich luy.

Cong thuc:
- `diem_tong_ket_10 = diem_qua_trinh * 0.4 + diem_thi * 0.6`
- Quy doi he 4 theo bang quy tac (co cau hinh).
- `GPA = SUM(diem_he_4 * so_tin_chi) / SUM(so_tin_chi)`
- Lam tron 2 chu so thap phan.

Rule:
- Diem trong khoang `0 -> 10`.
- Moi ban ghi diem phai gan voi 1 dang ky hoc phan hop le.
- Cho phep nhap lai diem (lan hoc), tinh GPA theo ket qua moi nhat cua hoc phan.

API goi y:
- `POST /api/grades`
- `PUT /api/grades/{id}`
- `POST /api/gpa/recalculate/{ma_sv}`

Tieu chi chap nhan:
- He thong tu dong cap nhat GPA sau khi luu diem.
- Kiem tra va chan diem ngoai mien gia tri.
- Co lich su thay doi diem (audit log) theo nguoi thao tac va thoi gian.

### 4.3 Xep loai hoc luc
Mo ta:
- Xep loai hoc luc theo GPA tich luy.

Rule mac dinh (co cau hinh):
- `>= 3.60`: Xuat sac
- `3.20 - 3.59`: Gioi
- `2.50 - 3.19`: Kha
- `2.00 - 2.49`: Trung binh
- `< 2.00`: Yeu

API goi y:
- `GET /api/students/{ma_sv}/academic-standing`
- `POST /api/academic-standing/recalculate`

Tieu chi chap nhan:
- Xep loai phan anh dung nguong cau hinh.
- Tu dong cap nhat khi GPA thay doi.

### 4.4 Tim kiem sinh vien
Mo ta:
- Tim nhanh theo ma SV, ho ten, lop, khoa, nganh, trang thai.
- Ho tro loc + sap xep + phan trang.

Rule:
- Tim khong phan biet hoa thuong cho ho ten.
- Ho tro tim gan dung theo tu khoa (contains).
- Tra ve ket qua trong <= 2 giay voi tap du lieu 100k sinh vien.

API goi y:
- `GET /api/students?keyword=&khoa=&nganh=&lop=&trang_thai=&page=&size=&sort=`

Tieu chi chap nhan:
- Ket qua tim dung bo loc.
- Phan trang chinh xac tong ban ghi va tong trang.

### 4.5 Xuat bao cao
Mo ta:
- Xuat bao cao PDF/Excel cho cac nhu cau dao tao.

Loai bao cao:
- Bang diem ca nhan theo hoc ky/nam hoc.
- Danh sach sinh vien theo lop/khoa.
- Bao cao phan bo hoc luc theo khoa hoc, nganh.
- Danh sach sinh vien canh bao hoc vu.

Rule:
- Chi tai khoan co quyen moi duoc xuat bao cao.
- Bao cao luu vet nguoi xuat, thoi gian xuat.

API goi y:
- `GET /api/reports/transcript/{ma_sv}`
- `GET /api/reports/students`
- `GET /api/reports/academic-standing`
- `GET /api/reports/academic-warning`

Tieu chi chap nhan:
- File xuat dung mau, du lieu dung bo loc.
- Thoi gian tao bao cao <= 30 giay voi bo du lieu 10k ban ghi.

## 5. Yeu cau phi chuc nang
- Bao mat: RBAC, JWT/Session, ma hoa ket noi HTTPS.
- Toan ven du lieu: rang buoc khoa ngoai, transaction khi nhap diem + cap nhat GPA.
- Kha nang mo rong: tach backend API va frontend web.
- Audit: ghi nhat ky thao tac voi du lieu diem va ho so.
- Sao luu: backup CSDL hang ngay.

## 6. Tieu chi nghiem thu tong the
- 100% chuc nang trong pham vi co test case nghiem thu.
- Khong co loi nghiem trong (P1/P2) tai UAT.
- Doi dao tao co the van hanh quy trinh nhap diem, tim kiem va xuat bao cao tren du lieu that.
