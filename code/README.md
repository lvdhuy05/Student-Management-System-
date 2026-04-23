# SMS - Student Management System (Django)

Du an Django duoc xay dung dua tren UML trong `prod/uml`.

## 1. Chuc nang hien tai
- Phan quyen 3 role: `ADMIN`, `SINH_VIEN`, `GIANG_VIEN`
- Quan tri sinh vien (them, sua, xoa mem, tim kiem)
- Quan tri hoc phan va lop hoc phan
- Dang ky hoc phan theo lop HP
- Sinh vien tu dang ky va xem mon da dang ky
- Giang vien xem lop cua toi, diem danh theo buoi, nhap/sua diem theo danh sach lop
- Tu dong tinh diem tong ket, diem he 4, diem chu
- Tu dong tinh GPA tich luy, GPA hoc ky va xep loai hoc luc
- Bao cao bang diem tren giao dien va xuat CSV
- Audit log thao tac

## 2. Cong nghe
- Backend: Django 6
- CSDL SQL: SQLite (mac dinh)
- Frontend: Django Template + HTML/CSS

## 3. Cau truc chinh
```text
code/
  manage.py
  sms_project/
  students/
  templates/
  static/css/styles.css
  requirements.txt
```

## 4. Chay local
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py seed_demo_data --reset
python manage.py runserver
```

Mac dinh he thong luu SQLite o `%TEMP%\\sms_project\\db.sqlite3` de tranh loi OneDrive.
Ban van co the override bang bien `SMS_SQLITE_PATH` neu muon dung file CSDL rieng.

## 5. URL chinh
- `/` : Trang chu
- `/students/` : Danh sach sinh vien (ADMIN)
- `/classes/` : Danh sach lop hoc phan (ADMIN)
- `/classes/my/` : Lop cua toi (GIANG_VIEN)
- `/classes/<id>/` : Chi tiet lop + diem danh + danh sach nhap/sua diem
- `/my/enrollments/` : Mon da dang ky + dang ky hoc phan (SINH_VIEN)
- `/grades/input/` : Nhap/sua diem (ADMIN, GIANG_VIEN)
- `/reports/my-transcript/` : Bang diem cua toi (SINH_VIEN)
- `/reports/transcript/<ma_sv>/` : Bao cao bang diem theo sinh vien

## 6. Tai khoan demo (sau khi seed)
- `admin / 123456` (ADMIN)
- `giangvien / 123456` (GIANG_VIEN)
- `giangvien2 / 123456` (GIANG_VIEN)
- `sv001 / 123456` (SINH_VIEN)
- `sv002 / 123456` (SINH_VIEN)
- `sv003 / 123456` (SINH_VIEN)
- `sv004 / 123456` (SINH_VIEN)

## 7. Test
```bash
python manage.py test
```
