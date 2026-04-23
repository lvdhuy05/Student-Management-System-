# Plan trien khai he thong quan ly sinh vien (ban cap nhat)

## 1. Muc tieu
Van hanh he thong SMS tren Django voi 3 role:
- `ADMIN`: quan tri toan bo
- `SINH_VIEN`: dang ky hoc phan + xem bang diem ca nhan
- `GIANG_VIEN`: lop cua toi + diem danh + nhap/sua diem

## 2. Pham vi chuc nang
1. Quan tri sinh vien
2. Quan tri hoc phan va lop hoc phan
3. Dang ky hoc phan theo lop HP
4. Diem danh theo buoi hoc
5. Nhap/sua diem, tinh GPA, xep loai hoc luc
6. Bao cao bang diem va xuat CSV

## 3. Kien truc va cong nghe
- Backend + frontend server-side: Django Template
- CSDL: SQLite (co migration SQL)
- Auth: Django session + RBAC trong app `students`
- UML + tai lieu: thu muc `prod`

## 4. Ke hoach ky thuat (thuc hien trong repo hien tai)

### Phase A - Refactor RBAC
- Chuyen role ve `ADMIN`, `SINH_VIEN`, `GIANG_VIEN`
- Lien ket tai khoan sinh vien voi ho so `Student`
- Update middleware authz/context/template nav theo role

### Phase B - Mo rong model du lieu
- Them `Classroom` (lop hoc phan)
- Mo rong `Enrollment` dang ky theo `Classroom`
- Them `Attendance` diem danh theo ngay hoc
- Tao migration + script SQL

### Phase C - Trien khai nghiep vu theo role
- Admin: CRUD sinh vien, hoc phan, lop hoc phan, dang ky, diem
- Sinh vien: dang ky hoc phan, xem mon da dang ky, xem bang diem
- Giang vien: lop cua toi, diem danh, nhap/sua diem trong lop

### Phase D - Tai lieu va du lieu demo
- Cap nhat UML: class/activity/sequence
- Cap nhat spec va README
- Seed du lieu demo: tai khoan 3 role + lop HP + diem + diem danh

## 5. Tieu chi nghiem thu
- Migration chay thanh cong tren DB dang dung
- Seed demo tao du tai khoan va du lieu nghiep vu
- `python manage.py test` pass
- Truy cap role dung quyen:
  - ADMIN vao duoc quan tri
  - SINH_VIEN chi thao tac du lieu cua minh
  - GIANG_VIEN chi thao tac lop duoc phan cong

## 6. To chuc repo
- `prod/`: spec, UML, SQL script migration, ke hoach
- `code/`: source Django, templates, migrations, seed, tests
