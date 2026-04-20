# Plan trien khai he thong quan ly sinh vien

## 1. Muc tieu trien khai
Trong 8 tuan, xay dung va dua vao van hanh he thong quan ly sinh vien cho phong dao tao voi 5 nhom chuc nang cot loi:
- Quan ly ho so sinh vien
- Quan ly diem va tinh GPA
- Xep loai hoc luc
- Tim kiem sinh vien
- Xuat bao cao

## 2. Pham vi va nguyen tac
Pham vi:
- Web app noi bo cho dao tao + giang vien + co van.
- API backend + CSDL quan he + bao cao PDF/Excel.

Ngoai pham vi phase 1:
- App mobile.
- Tich hop thanh toan hoc phi.
- Tich hop LMS phuc tap.

Nguyen tac:
- Uu tien dung quy trinh dao tao truoc, toi uu UX sau.
- Moi sprint deu co dau ra chay duoc va co test.
- Moi thay doi rule diem/GPA phai cau hinh duoc.

## 3. De xuat cong nghe (co the dieu chinh)
- Frontend: React + TypeScript + Ant Design.
- Backend: NestJS (hoac Express) + TypeScript.
- Database: PostgreSQL.
- Report: ExcelJS + PDFKit.
- Auth: JWT + RBAC.
- DevOps: Docker Compose, GitHub Actions, deploy len VM noi bo.

## 4. Kien truc tong quan
- `frontend`: giao dien quan tri va tra cuu.
- `backend`: REST API, xu ly nghiep vu, auth, report.
- `database`: PostgreSQL.
- `storage`: luu file bao cao da xuat (neu can).
- `audit-log`: luu lich su cap nhat du lieu nhay cam.

## 5. Ke hoach theo giai doan

### Phase 0 - Khoi dong (Tuan 1)
Muc tieu:
- Chot yeu cau nghiep vu va tieu chi nghiem thu.
- Khoi tao repository code, convention, CI co ban.

Cong viec:
- Chot ERD ban dau.
- Chot API contract v1 cho 5 nhom chuc nang.
- Khoi tao skeleton frontend/backend/database.
- Tao seed data mau.

Dau ra:
- Tai lieu yeu cau chuc nang v1.
- Tai lieu API draft.
- Repo chay duoc local qua Docker Compose.

### Phase 1 - Quan ly sinh vien + Tim kiem (Tuan 2-3)
Muc tieu:
- Hoan thanh CRUD sinh vien va tim kiem/loc/phan trang.

Cong viec backend:
- Model + migration bang `students`.
- API CRUD + soft delete.
- API search (keyword + filter + paging + sort).

Cong viec frontend:
- Man hinh danh sach sinh vien.
- Form them/sua sinh vien.
- Bo loc tim kiem + bang ket qua phan trang.

Test:
- Unit test service CRUD/search.
- API integration test cho validation, duplicate.
- UAT voi phong dao tao tren du lieu mau.

Dau ra:
- Release `v0.1` quan ly ho so + tim kiem.

### Phase 2 - Nhap diem, tinh GPA, xep loai (Tuan 4-5)
Muc tieu:
- Hoan thanh quy trinh nhap diem, tinh GPA hoc ky/tich luy, xep loai hoc luc.

Cong viec backend:
- Model `courses`, `enrollments`, `grades`, `gpa_snapshots`.
- Service tinh diem tong ket, quy doi he 4, diem chu.
- Service tinh GPA theo tin chi.
- Service xep loai hoc luc theo nguong cau hinh.
- Audit log khi sua diem.

Cong viec frontend:
- Man hinh nhap diem theo lop hoc phan.
- Man hinh xem bang diem sinh vien.
- Hien thi GPA va hoc luc.

Test:
- Unit test cong thuc diem/GPA.
- Scenario test: hoc lai, nhap diem lai, doi nguong xep loai.
- UAT voi bo du lieu that (an danh) cua 1 khoa.

Dau ra:
- Release `v0.2` nghiep vu dao tao cot loi.

### Phase 3 - Bao cao + Hoan thien bao mat (Tuan 6-7)
Muc tieu:
- Xuat bao cao PDF/Excel va hoan thien quyen truy cap.

Cong viec backend:
- API bao cao bang diem ca nhan.
- API bao cao tong hop theo lop/khoa.
- API bao cao phan bo hoc luc + canh bao hoc vu.
- RBAC chi tiet theo vai tro.

Cong viec frontend:
- Man hinh tao bao cao theo bo loc.
- Tai file bao cao.
- Nhat ky xuat bao cao (lich su tai khoan).

Test:
- Performance test tao report lon.
- Security test (phan quyen API).
- UAT voi can bo dao tao.

Dau ra:
- Release `v1.0-rc` san sang pilot.

### Phase 4 - Pilot va Go-live (Tuan 8)
Muc tieu:
- Chay thu nghiem pilot, fix loi va dua vao su dung chinh thuc.

Cong viec:
- Import du lieu that (co kiem tra chat luong).
- Dao tao nguoi dung (dao tao, giang vien).
- Van hanh pilot 1-2 tuan voi 1 khoa.
- Fix loi P1/P2, dong goi release chinh thuc.

Dau ra:
- Go-live `v1.0`.
- Bien ban nghiem thu va checklist van hanh.

## 6. Backlog uu tien (MVP)
1. Auth + RBAC co ban.
2. CRUD sinh vien + validation.
3. Tim kiem/loc/phan trang.
4. Nhap diem hoc phan.
5. Tinh GPA + xep loai.
6. Xuat bang diem ca nhan.
7. Xuat bao cao tong hop.
8. Audit log + monitoring co ban.

## 7. Tieu chi hoan thanh (Definition of Done)
- Co unit test cho logic nghiep vu quan trong.
- API integration test pass.
- Co migration CSDL va rollback script.
- Tai lieu API cap nhat.
- Da review code va pass CI.
- Da test UAT theo checklist.

## 8. Rui ro va giai phap
- Rui ro du lieu dau vao khong sach:
  Giai phap: bo quy tac validation + script cleanup truoc import.
- Rui ro thay doi quy che tinh diem:
  Giai phap: dua cong thuc va nguong xep loai vao bang cau hinh.
- Rui ro cham tien do vi UAT:
  Giai phap: demo theo sprint, nghiem thu som theo module.

## 9. Cach to chuc trong repo
- Thu muc `prod`:
  Chua spec, user flow, test case UAT, ke hoach release.
- Thu muc `code`:
  Chua source code backend/frontend, migration, test, script deploy.

## 10. Moc kiem tra tien do
- Cuoi tuan 1: Chot spec + khoi tao codebase.
- Cuoi tuan 3: Demo CRUD + tim kiem.
- Cuoi tuan 5: Demo nhap diem + GPA + hoc luc.
- Cuoi tuan 7: Demo bao cao + phan quyen day du.
- Cuoi tuan 8: Go-live pilot/chinh thuc.
