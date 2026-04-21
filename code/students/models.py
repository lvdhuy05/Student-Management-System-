from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


def score_10_to_4_and_letter(score_10: Decimal) -> tuple[Decimal, str]:
    mapping = [
        (Decimal("8.50"), Decimal("10.00"), Decimal("4.00"), "A"),
        (Decimal("8.00"), Decimal("8.49"), Decimal("3.50"), "B+"),
        (Decimal("7.00"), Decimal("7.99"), Decimal("3.00"), "B"),
        (Decimal("6.50"), Decimal("6.99"), Decimal("2.50"), "C+"),
        (Decimal("5.50"), Decimal("6.49"), Decimal("2.00"), "C"),
        (Decimal("5.00"), Decimal("5.49"), Decimal("1.50"), "D+"),
        (Decimal("4.00"), Decimal("4.99"), Decimal("1.00"), "D"),
        (Decimal("0.00"), Decimal("3.99"), Decimal("0.00"), "F"),
    ]
    for lower, upper, score_4, letter in mapping:
        if lower <= score_10 <= upper:
            return score_4, letter
    return Decimal("0.00"), "F"


class UserProfile(models.Model):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Quản trị viên"
        DAO_TAO = "DAO_TAO", "Đào tạo"
        GIANG_VIEN = "GIANG_VIEN", "Giảng viên"
        CO_VAN = "CO_VAN", "Cố vấn học tập"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Hoạt động"
        INACTIVE = "INACTIVE", "Không hoạt động"
        LOCKED = "LOCKED", "Bị khóa"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DAO_TAO)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Đang học"
        INACTIVE = "INACTIVE", "Tạm ngưng"
        SOFT_DELETED = "SOFT_DELETED", "Đã xóa mềm"

    ma_sv = models.CharField(max_length=20, unique=True)
    ho_ten = models.CharField(max_length=150)
    ngay_sinh = models.DateField()
    gioi_tinh = models.CharField(max_length=20, blank=True)
    email = models.EmailField(unique=True)
    so_dien_thoai = models.CharField(max_length=20, blank=True)
    khoa = models.CharField(max_length=120)
    nganh = models.CharField(max_length=120)
    lop = models.CharField(max_length=50)
    khoa_hoc = models.CharField(max_length=30)
    trang_thai = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["ma_sv"]

    def __str__(self) -> str:
        return f"{self.ma_sv} - {self.ho_ten}"

    def soft_delete(self) -> None:
        self.trang_thai = self.Status.SOFT_DELETED
        self.save(update_fields=["trang_thai", "updated_at"])


class Course(models.Model):
    ma_hp = models.CharField(max_length=20, unique=True)
    ten_hp = models.CharField(max_length=150)
    so_tin_chi = models.PositiveSmallIntegerField(default=3)

    class Meta:
        ordering = ["ma_hp"]

    def __str__(self) -> str:
        return f"{self.ma_hp} - {self.ten_hp}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        DANG_HOC = "DANG_HOC", "Đang học"
        HOAN_THANH = "HOAN_THANH", "Hoàn thành"
        HUY = "HUY", "Hủy"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="enrollments")
    hoc_ky = models.CharField(max_length=10)
    nam_hoc = models.CharField(max_length=20)
    trang_thai = models.CharField(max_length=20, choices=Status.choices, default=Status.DANG_HOC)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "course", "hoc_ky", "nam_hoc"],
                name="uniq_student_course_semester_year",
            )
        ]
        ordering = ["-nam_hoc", "-hoc_ky", "course__ma_hp"]

    def __str__(self) -> str:
        return f"{self.student.ma_sv} | {self.course.ma_hp} | HK{self.hoc_ky} {self.nam_hoc}"


class Grade(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="grades")
    diem_chuyen_can = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    diem_qua_trinh = models.DecimalField(max_digits=4, decimal_places=2)
    diem_thi = models.DecimalField(max_digits=4, decimal_places=2)
    diem_tong_ket_10 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    diem_he_4 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    diem_chu = models.CharField(max_length=2, blank=True)
    lan_hoc = models.PositiveIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["enrollment", "lan_hoc"], name="uniq_enrollment_attempt")]
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return f"{self.enrollment} - Lan {self.lan_hoc}: {self.diem_tong_ket_10}"

    def clean(self) -> None:
        for field_name in ("diem_chuyen_can", "diem_qua_trinh", "diem_thi"):
            value = getattr(self, field_name)
            if value is None:
                raise ValidationError({field_name: "Điểm bắt buộc nhập."})
            if value < Decimal("0.00") or value > Decimal("10.00"):
                raise ValidationError({field_name: "Điểm phải trong khoảng 0 -> 10."})

    def calculate(self) -> None:
        tong_ket = (
            (self.diem_chuyen_can * Decimal("0.1"))
            + (self.diem_qua_trinh * Decimal("0.3"))
            + (self.diem_thi * Decimal("0.6"))
        )
        self.diem_tong_ket_10 = tong_ket.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        self.diem_he_4, self.diem_chu = score_10_to_4_and_letter(self.diem_tong_ket_10)

    def save(self, *args, **kwargs):
        self.full_clean()
        self.calculate()
        super().save(*args, **kwargs)


class GPASemester(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="gpa_semesters")
    hoc_ky = models.CharField(max_length=10)
    nam_hoc = models.CharField(max_length=20)
    gpa_he_4 = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    tong_tin_chi_tich_luy = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["student", "hoc_ky", "nam_hoc"],
                name="uniq_student_semester_snapshot",
            )
        ]
        ordering = ["-nam_hoc", "-hoc_ky"]


class AcademicStanding(models.Model):
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name="academic_standing")
    gpa_tich_luy = models.DecimalField(max_digits=4, decimal_places=2, default=Decimal("0.00"))
    xep_loai = models.CharField(max_length=50, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.student.ma_sv}: {self.xep_loai} ({self.gpa_tich_luy})"


class ClassificationRule(models.Model):
    diem_tu = models.DecimalField(max_digits=4, decimal_places=2)
    diem_den = models.DecimalField(max_digits=4, decimal_places=2)
    nhan_xep_loai = models.CharField(max_length=50)
    kich_hoat = models.BooleanField(default=True)

    class Meta:
        ordering = ["-diem_tu"]

    def __str__(self) -> str:
        return f"{self.nhan_xep_loai}: {self.diem_tu} - {self.diem_den}"


class AuditLog(models.Model):
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    hanh_dong = models.CharField(max_length=120)
    doi_tuong = models.CharField(max_length=120)
    truoc_thay_doi = models.JSONField(null=True, blank=True)
    sau_thay_doi = models.JSONField(null=True, blank=True)
    tao_luc = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-tao_luc"]

    def __str__(self) -> str:
        return f"{self.hanh_dong} - {self.doi_tuong} - {self.tao_luc}"
