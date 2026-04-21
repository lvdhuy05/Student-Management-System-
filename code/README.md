# SMS - Student Management System (Django)

Du an Django duoc xay dung dua tren UML trong `prod/uml`.

## 1. Chuc nang da co
- Them / sua / xoa mem sinh vien
- Tim kiem sinh vien theo keyword, khoa, nganh, lop, trang thai
- Tao hoc phan va dang ky hoc phan
- Nhap diem (chuyen can, qua trinh, diem thi), tu dong tinh diem tong ket + diem he 4 + diem chu
- Tu dong tinh GPA tich luy, GPA hoc ky va xep loai hoc luc
- Bao cao bang diem tren giao dien va xuat CSV
- Audit log thao tac

## 2. Cong nghe
- Backend: Django 6
- CSDL SQL: SQLite (mac dinh, co the doi sang MySQL/PostgreSQL trong `settings.py`)
- Frontend: Django Template + HTML/CSS

## 3. Cau truc chinh
```text
code/
  manage.py
  sms_project/            # settings + root urls
  students/               # app nghiep vu chinh
  templates/              # giao dien html
  static/css/styles.css   # giao dien css
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

Mac dinh he thong da luu SQLite o thu muc `%TEMP%\\sms_project\\db.sqlite3` de tranh loi OneDrive.
Ban van co the override bang bien `SMS_SQLITE_PATH` neu muon dung file CSDL rieng.

## 5. URL chinh
- `/` : Trang chủ
- `/students/` : Danh sach + tim kiem sinh vien
- `/students/create/` : Them sinh vien
- `/grades/input/` : Nhap diem
- `/courses/create/` : Tao hoc phan
- `/enrollments/create/` : Tao dang ky hoc phan
- `/reports/transcript/<ma_sv>/` : Bao cao bang diem
- `/accounts/login/` : Dang nhap

## 6. Tai khoan demo (sau khi chay seed)
- `admin / 123456` (ADMIN)
- `daotao / 123456` (DAO_TAO)
- `giangvien / 123456` (GIANG_VIEN)
- `covan / 123456` (CO_VAN)

## 7. Test
```bash
python manage.py test
```
