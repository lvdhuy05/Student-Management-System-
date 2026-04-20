# 04 - Thiet ke UML

Tai lieu nay mo ta UML muc thiet ke co so cho pham vi MVP da thong nhat trong `03-yeu-cau-chuc-nang.md`.

## 1. Class Diagram

```mermaid
classDiagram
direction LR

class NguoiDung {
  +UUID id
  +string username
  +string passwordHash
  +VaiTro vaiTro
  +TrangThaiTaiKhoan trangThai
  +bool coQuyen(chucNang)
}

class SinhVien {
  +string maSv
  +string hoTen
  +date ngaySinh
  +string gioiTinh
  +string email
  +string soDienThoai
  +string khoa
  +string nganh
  +string lop
  +string khoaHoc
  +TrangThaiSinhVien trangThai
  +capNhatThongTin()
  +xoaMem()
}

class HocPhan {
  +string maHp
  +string tenHp
  +int soTinChi
}

class DangKyHocPhan {
  +UUID id
  +string hocKy
  +string namHoc
  +TrangThaiDangKy trangThai
}

class Diem {
  +UUID id
  +float diemQuaTrinh
  +float diemThi
  +float diemTongKet10
  +float diemHe4
  +string diemChu
  +int lanHoc
  +datetime capNhatLuc
  +tinhDiemTongKet()
  +quyDoiDiem()
}

class GPAHocKy {
  +UUID id
  +string hocKy
  +string namHoc
  +float gpaHe4
  +int tongTinChiTichLuy
  +datetime capNhatLuc
}

class HocLuc {
  +UUID id
  +float gpaTichLuy
  +string xepLoai
  +datetime capNhatLuc
}

class QuyTacXepLoai {
  +UUID id
  +float diemTu
  +float diemDen
  +string nhanXepLoai
  +bool kichHoat
}

class AuditLog {
  +UUID id
  +UUID actorId
  +string hanhDong
  +string doiTuong
  +string truocThayDoi
  +string sauThayDoi
  +datetime taoLuc
}

class StudentService {
  +taoSinhVien()
  +capNhatSinhVien()
  +xoaMemSinhVien()
  +timKiemSinhVien()
}

class GradeService {
  +nhapDiem()
  +capNhatDiem()
  +validateDiem()
}

class GPAService {
  +tinhGPAHocKy()
  +tinhGPATichLuy()
  +xepLoaiHocLuc()
}

class ReportService {
  +xuatBangDiemCaNhan()
  +xuatDanhSachSinhVien()
  +xuatBaoCaoHocLuc()
  +xuatDanhSachCanhBaoHocVu()
}

SinhVien "1" --> "0..*" DangKyHocPhan : dang ky
HocPhan "1" --> "0..*" DangKyHocPhan : duoc dang ky
DangKyHocPhan "1" --> "0..*" Diem : lan hoc
SinhVien "1" --> "0..*" GPAHocKy : tich luy
SinhVien "1" --> "0..*" HocLuc : lich su
QuyTacXepLoai "1" --> "0..*" HocLuc : ap dung
NguoiDung "1" --> "0..*" AuditLog : tao log

StudentService ..> SinhVien : CRUD/search
GradeService ..> Diem : tinh/luu
GradeService ..> DangKyHocPhan : kiem tra dang ky
GradeService ..> GPAService : trigger recalc
GPAService ..> GPAHocKy : cap nhat
GPAService ..> QuyTacXepLoai : doc nguong
ReportService ..> SinhVien : lay du lieu
ReportService ..> Diem : tong hop diem
ReportService ..> GPAHocKy : tong hop GPA
```

## 2. Activity Diagram (Luong nghiep vu tong the)

```mermaid
flowchart TD
    A([Bat dau]) --> B[Dang nhap he thong]
    B --> C{Xac thuc + RBAC hop le?}
    C -- Khong --> X[Tu choi truy cap] --> Z([Ket thuc])
    C -- Co --> D{Chon chuc nang}

    D -- CRUD sinh vien --> E[Nhap thong tin sinh vien]
    E --> E1{Du lieu hop le va khong trung?}
    E1 -- Khong --> E2[Tra loi validation error] --> D
    E1 -- Co --> E3[Luu thay doi sinh vien] --> D

    D -- Nhap diem/GPA --> F[Nhap diem qua trinh + diem thi]
    F --> F1{Diem 0..10 va co dang ky hoc phan?}
    F1 -- Khong --> F2[Tra loi loi nghiep vu] --> D
    F1 -- Co --> F3[Luu diem]
    F3 --> F4[Tinh diem tong ket he 10]
    F4 --> F5[Quy doi diem he 4 + diem chu]
    F5 --> F6[Tinh GPA hoc ky va tich luy]
    F6 --> F7[Xep loai hoc luc theo nguong cau hinh]
    F7 --> F8[Ghi audit log] --> D

    D -- Tim kiem sinh vien --> G[Nhap tu khoa + bo loc]
    G --> G1[Thuc hien tim kiem + phan trang]
    G1 --> G2[Hien thi ket qua] --> D

    D -- Xuat bao cao --> H[Chon loai bao cao + bo loc]
    H --> H1{Nguoi dung co quyen xuat?}
    H1 -- Khong --> H2[Tra loi 403 Forbidden] --> D
    H1 -- Co --> H3[Tong hop du lieu bao cao]
    H3 --> H4[Render file PDF/Excel]
    H4 --> H5[Ghi nhat ky xuat bao cao]
    H5 --> H6[Tra file ve nguoi dung] --> D

    D -- Dang xuat --> Z
```

## 3. Sequence Diagram (Nhap diem -> Tinh GPA -> Xep loai)

```mermaid
sequenceDiagram
    actor Cb as Can bo dao tao
    participant UI as Frontend Web
    participant GradeCtl as GradeController
    participant Auth as AuthService
    participant GradeSvc as GradeService
    participant EnrollRepo as EnrollmentRepository
    participant GradeRepo as GradeRepository
    participant GpaSvc as GPAService
    participant RuleRepo as RuleConfigRepository
    participant GpaRepo as GPASnapshotRepository
    participant Audit as AuditLogService
    participant DB as PostgreSQL

    Cb->>UI: Nhap diem (ma_sv, ma_hp, hoc_ky, nam_hoc, diem)
    UI->>GradeCtl: POST /api/grades
    GradeCtl->>Auth: Kiem tra JWT + RBAC
    Auth-->>GradeCtl: Hop le
    GradeCtl->>GradeSvc: nhapDiem(payload, actorId)
    GradeSvc->>EnrollRepo: findEnrollment(ma_sv, ma_hp, hoc_ky, nam_hoc)
    EnrollRepo->>DB: SELECT enrollment
    DB-->>EnrollRepo: enrollment/null
    EnrollRepo-->>GradeSvc: ket qua

    alt Khong ton tai dang ky hoc phan
        GradeSvc-->>GradeCtl: 404 EnrollmentNotFound
        GradeCtl-->>UI: Response loi
        UI-->>Cb: Hien thi thong bao loi
    else Ton tai dang ky hoc phan
        GradeSvc->>GradeSvc: Validate diem 0..10
        GradeSvc->>GradeRepo: UPSERT diem + lan_hoc
        GradeRepo->>DB: INSERT/UPDATE grades
        DB-->>GradeRepo: OK
        GradeRepo-->>GradeSvc: gradeSaved

        GradeSvc->>GpaSvc: recalculate(ma_sv)
        GpaSvc->>DB: SELECT diem moi nhat + tin chi
        DB-->>GpaSvc: dataset GPA
        GpaSvc->>RuleRepo: layNguongXepLoai()
        RuleRepo->>DB: SELECT quy_tac_xep_loai
        DB-->>RuleRepo: rules
        RuleRepo-->>GpaSvc: rules
        GpaSvc->>GpaRepo: UPSERT gpa_hoc_ky + hoc_luc
        GpaRepo->>DB: UPSERT snapshots
        DB-->>GpaRepo: OK
        GpaRepo-->>GpaSvc: OK
        GpaSvc-->>GradeSvc: gpa + xep_loai

        GradeSvc->>Audit: ghiLog(actorId, SUA_DIEM, payload)
        Audit->>DB: INSERT audit_log
        DB-->>Audit: OK

        GradeSvc-->>GradeCtl: 200 (diem, gpa, xep_loai)
        GradeCtl-->>UI: Response thanh cong
        UI-->>Cb: Hien thi ket qua cap nhat
    end
```

## 4. Ghi chu su dung
- Cac so do tren duoc viet bang Mermaid de render truc tiep trong Markdown preview.
- Neu can xuat file anh/PDF UML, co the copy block Mermaid sang cong cu render de xuat.

## 5. UML code (PlantUML)
- Class diagram: `prod/uml/class-diagram.puml`
- Activity diagram: `prod/uml/activity-diagram.puml`
- Sequence diagram: `prod/uml/sequence-diagram.puml`
