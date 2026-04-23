# 04 - Thiet ke UML

Tai lieu nay mo ta UML sau khi chuyen he thong ve 3 role:
- `ADMIN`: quan tri toan bo
- `SINH_VIEN`: xem bang diem, dang ky hoc phan, xem mon da dang ky
- `GIANG_VIEN`: lop cua toi, diem danh, nhap/sua diem cho sinh vien trong lop

## 1. Danh sach file UML
- Class diagram: `prod/uml/class-diagram.puml`
- Activity diagram: `prod/uml/activity-diagram.puml`
- Sequence diagram: `prod/uml/sequence-diagram.puml`
- SQL schema migration: `prod/sql/0003-role-rbac.sql`

## 2. Class Diagram
Class diagram bo sung cac thanh phan nghiep vu moi:
- `Classroom` (lop hoc phan) gan `Course` va `Giang vien`
- `Enrollment` dang ky theo `Classroom`
- `Attendance` diem danh theo ngay hoc cho tung `Enrollment`
- `UserProfile` lien ket role va lien ket 1-1 voi `Student` cho role sinh vien
- `Grade` + `GPA` + `AcademicStanding` giu nguyen luong tinh diem va hoc luc

Mo file PlantUML:
```text
prod/uml/class-diagram.puml
```

## 3. Activity Diagram
Activity diagram mo ta luong tong the theo role:
1. Dang nhap + kiem tra RBAC
2. Nhanh `ADMIN`: quan tri du lieu va thao tac toan he thong
3. Nhanh `SINH_VIEN`: dang ky hoc phan va xem bang diem ca nhan
4. Nhanh `GIANG_VIEN`: vao lop cua toi, diem danh, nhap/sua diem

Mo file PlantUML:
```text
prod/uml/activity-diagram.puml
```

## 4. Sequence Diagram
Sequence diagram mo ta chi tiet luong giang vien:
1. Mo chi tiet lop hoc phan
2. Submit diem danh theo ngay hoc
3. Nhap/sua diem sinh vien
4. Trigger tinh lai GPA + xep loai hoc luc

Mo file PlantUML:
```text
prod/uml/sequence-diagram.puml
```

## 5. Ghi chu dong bo voi code
- Model va migration da duoc cap nhat trong `code/students/models.py` va `code/students/migrations/0003_...py`
- Cac view/template tuong ung voi UML nam trong:
  - `code/students/views.py`
  - `code/templates/students/*.html`
- Ban SQL duoc xuat tu `python manage.py sqlmigrate students 0003` de doi chieu schema CSDL.
