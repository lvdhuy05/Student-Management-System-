# 04 - Thiet ke UML

Tai lieu nay tong hop thiet ke UML cho he thong quan ly sinh vien.
Nguon chinh duoc luu duoi dang PlantUML trong thu muc `prod/uml`.

## 1. Danh sach file UML
- Class diagram: `prod/uml/class-diagram.puml`
- Activity diagram: `prod/uml/activity-diagram.puml`
- Sequence diagram: `prod/uml/sequence-diagram.puml`

## 2. Class Diagram (PlantUML)
```plantuml
@startuml
title SMS - Class Diagram

skinparam classAttributeIconSize 0
hide circle

enum VaiTro {
  ADMIN
  DAO_TAO
  GIANG_VIEN
  CO_VAN
}

enum TrangThaiTaiKhoan {
  ACTIVE
  INACTIVE
  LOCKED
}

enum TrangThaiSinhVien {
  ACTIVE
  INACTIVE
  SOFT_DELETED
}

enum TrangThaiDangKy {
  DANG_HOC
  HOAN_THANH
  HUY
}

class NguoiDung {
  +id: UUID
  +username: string
  +passwordHash: string
  +vaiTro: VaiTro
  +trangThai: TrangThaiTaiKhoan
  +coQuyen(chucNang: string): bool
}

class SinhVien {
  +maSv: string
  +hoTen: string
  +ngaySinh: date
  +gioiTinh: string
  +email: string
  +soDienThoai: string
  +khoa: string
  +nganh: string
  +lop: string
  +khoaHoc: string
  +trangThai: TrangThaiSinhVien
  +capNhatThongTin(): void
  +xoaMem(): void
}

class HocPhan {
  +maHp: string
  +tenHp: string
  +soTinChi: int
}

class DangKyHocPhan {
  +id: UUID
  +hocKy: string
  +namHoc: string
  +trangThai: TrangThaiDangKy
}

class Diem {
  +id: UUID
  +diemQuaTrinh: float
  +diemThi: float
  +diemTongKet10: float
  +diemHe4: float
  +diemChu: string
  +lanHoc: int
  +capNhatLuc: datetime
  +tinhDiemTongKet(): float
  +quyDoiDiem(): void
}

class GPAHocKy {
  +id: UUID
  +hocKy: string
  +namHoc: string
  +gpaHe4: float
  +tongTinChiTichLuy: int
  +capNhatLuc: datetime
}

class HocLuc {
  +id: UUID
  +gpaTichLuy: float
  +xepLoai: string
  +capNhatLuc: datetime
}

class QuyTacXepLoai {
  +id: UUID
  +diemTu: float
  +diemDen: float
  +nhanXepLoai: string
  +kichHoat: bool
}

class AuditLog {
  +id: UUID
  +actorId: UUID
  +hanhDong: string
  +doiTuong: string
  +truocThayDoi: text
  +sauThayDoi: text
  +taoLuc: datetime
}

class StudentService {
  +taoSinhVien(): SinhVien
  +capNhatSinhVien(maSv: string): SinhVien
  +xoaMemSinhVien(maSv: string): void
  +timKiemSinhVien(filter: map): list
}

class GradeService {
  +nhapDiem(payload: map): Diem
  +capNhatDiem(id: UUID, payload: map): Diem
  +validateDiem(payload: map): bool
}

class GPAService {
  +tinhGPAHocKy(maSv: string, hocKy: string, namHoc: string): GPAHocKy
  +tinhGPATichLuy(maSv: string): float
  +xepLoaiHocLuc(maSv: string): HocLuc
}

class ReportService {
  +xuatBangDiemCaNhan(maSv: string): File
  +xuatDanhSachSinhVien(filter: map): File
  +xuatBaoCaoHocLuc(filter: map): File
  +xuatDanhSachCanhBaoHocVu(filter: map): File
}

SinhVien "1" -- "0..*" DangKyHocPhan : dang ky
HocPhan "1" -- "0..*" DangKyHocPhan : duoc dang ky
DangKyHocPhan "1" -- "0..*" Diem : lan hoc
SinhVien "1" -- "0..*" GPAHocKy : tich luy
SinhVien "1" -- "0..*" HocLuc : lich su
QuyTacXepLoai "1" -- "0..*" HocLuc : ap dung
NguoiDung "1" -- "0..*" AuditLog : tao log

StudentService ..> SinhVien : CRUD/search
GradeService ..> Diem : tinh/luu
GradeService ..> DangKyHocPhan : kiem tra dang ky
GradeService ..> GPAService : trigger recalc
GPAService ..> GPAHocKy : cap nhat
GPAService ..> QuyTacXepLoai : doc nguong
ReportService ..> SinhVien : lay du lieu
ReportService ..> Diem : tong hop diem
ReportService ..> GPAHocKy : tong hop GPA

@enduml
```

## 3. Activity Diagram (PlantUML)
```plantuml
@startuml
title SMS - Activity Diagram (Luong nghiep vu tong the)

start

:Dang nhap he thong;
if (Xac thuc + RBAC hop le?) then (Co)
  :Chon chuc nang;
else (Khong)
  :Tu choi truy cap;
  stop
endif

repeat
  if (CRUD sinh vien?) then (Co)
    :Nhap thong tin sinh vien;
    if (Du lieu hop le va khong trung?) then (Co)
      :Luu thay doi sinh vien;
    else (Khong)
      :Tra loi validation error;
    endif

  elseif (Nhap diem/GPA?) then (Co)
    :Nhap diem qua trinh + diem thi;
    if (Diem 0..10 va co dang ky hoc phan?) then (Co)
      :Luu diem;
      :Tinh diem tong ket he 10;
      :Quy doi diem he 4 + diem chu;
      :Tinh GPA hoc ky va tich luy;
      :Xep loai hoc luc theo nguong cau hinh;
      :Ghi audit log;
    else (Khong)
      :Tra loi loi nghiep vu;
    endif

  elseif (Tim kiem sinh vien?) then (Co)
    :Nhap tu khoa + bo loc;
    :Thuc hien tim kiem + phan trang;
    :Hien thi ket qua;

  elseif (Xuat bao cao?) then (Co)
    :Chon loai bao cao + bo loc;
    if (Nguoi dung co quyen xuat?) then (Co)
      :Tong hop du lieu bao cao;
      :Render file PDF/Excel;
      :Ghi nhat ky xuat bao cao;
      :Tra file ve nguoi dung;
    else (Khong)
      :Tra loi 403 Forbidden;
    endif
  endif

repeat while (Tiep tuc thao tac?) is (Co)

stop
@enduml
```

## 4. Sequence Diagram (PlantUML)
```plantuml
@startuml
title SMS - Sequence Diagram (Nhap diem -> Tinh GPA -> Xep loai)

actor "Can bo dao tao" as Cb
participant "Frontend Web" as UI
participant "GradeController" as GradeCtl
participant "AuthService" as Auth
participant "GradeService" as GradeSvc
participant "EnrollmentRepository" as EnrollRepo
participant "GradeRepository" as GradeRepo
participant "GPAService" as GpaSvc
participant "RuleConfigRepository" as RuleRepo
participant "GPASnapshotRepository" as GpaRepo
participant "AuditLogService" as Audit
database "PostgreSQL" as DB

Cb -> UI: Nhap diem(ma_sv, ma_hp, hoc_ky, nam_hoc, diem)
UI -> GradeCtl: POST /api/grades
GradeCtl -> Auth: Kiem tra JWT + RBAC
Auth --> GradeCtl: Hop le
GradeCtl -> GradeSvc: nhapDiem(payload, actorId)
GradeSvc -> EnrollRepo: findEnrollment(ma_sv, ma_hp, hoc_ky, nam_hoc)
EnrollRepo -> DB: SELECT enrollment
DB --> EnrollRepo: enrollment/null
EnrollRepo --> GradeSvc: ket qua

alt Khong ton tai dang ky hoc phan
  GradeSvc --> GradeCtl: 404 EnrollmentNotFound
  GradeCtl --> UI: Response loi
  UI --> Cb: Hien thi thong bao loi
else Ton tai dang ky hoc phan
  GradeSvc -> GradeSvc: Validate diem 0..10
  GradeSvc -> GradeRepo: UPSERT diem + lan_hoc
  GradeRepo -> DB: INSERT/UPDATE grades
  DB --> GradeRepo: OK
  GradeRepo --> GradeSvc: gradeSaved

  GradeSvc -> GpaSvc: recalculate(ma_sv)
  GpaSvc -> DB: SELECT diem moi nhat + tin chi
  DB --> GpaSvc: dataset GPA
  GpaSvc -> RuleRepo: layNguongXepLoai()
  RuleRepo -> DB: SELECT quy_tac_xep_loai
  DB --> RuleRepo: rules
  RuleRepo --> GpaSvc: rules
  GpaSvc -> GpaRepo: UPSERT gpa_hoc_ky + hoc_luc
  GpaRepo -> DB: UPSERT snapshots
  DB --> GpaRepo: OK
  GpaRepo --> GpaSvc: OK
  GpaSvc --> GradeSvc: gpa + xep_loai

  GradeSvc -> Audit: ghiLog(actorId, SUA_DIEM, payload)
  Audit -> DB: INSERT audit_log
  DB --> Audit: OK

  GradeSvc --> GradeCtl: 200 (diem, gpa, xep_loai)
  GradeCtl --> UI: Response thanh cong
  UI --> Cb: Hien thi ket qua cap nhat
end

@enduml
```
