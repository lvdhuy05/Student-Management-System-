# SMS - Student Management System

## Muc dich thu muc `code`
Thu muc `code` dung de trien khai source code cua he thong quan ly sinh vien theo spec tai thu muc `prod`.

## De xuat cau truc source
```text
code/
  backend/
    src/
    test/
    prisma-or-migrations/
  frontend/
    src/
    public/
  shared/
    types/
  infra/
    docker/
    scripts/
```

## Chuc nang MVP can co trong code
- Quan ly sinh vien: them, sua, xoa mem, xem chi tiet.
- Tim kiem sinh vien: keyword + bo loc + phan trang.
- Nhap diem hoc phan: diem qua trinh, diem thi, diem tong ket.
- Tinh GPA: hoc ky va tich luy.
- Xep loai hoc luc theo nguong cau hinh.
- Xuat bao cao PDF/Excel.

## Quy uoc ky thuat
- Viet TypeScript cho ca frontend va backend.
- Moi thay doi CSDL phai di kem migration.
- API tra loi co chuan loi thong nhat.
- Co test cho logic nghiep vu quan trong (GPA, xep loai).
- Khong hard-code nguong xep loai; dua vao cau hinh.

## Checklist khoi tao
1. Khoi tao backend framework va frontend framework.
2. Khoi tao PostgreSQL bang Docker Compose.
3. Tao migration ban dau cho cac bang cot loi.
4. Dung bo API CRUD sinh vien + search.
5. Dung module diem/GPA/xep loai.
6. Dung module report.
7. Thiet lap CI cho lint + test.

## Tieu chi san sang release v1.0
- Hoan thanh 100% chuc nang MVP.
- Pass test tu dong + UAT.
- Co script deploy va huong dan rollback.
