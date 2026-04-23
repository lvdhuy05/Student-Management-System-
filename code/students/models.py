from decimal import Decimal, ROUND_HALF_UP

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q


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
        ADMIN = "ADMIN", "Quan tri vien"
        SINH_VIEN = "SINH_VIEN", "Sinh vien"
        GIANG_VIEN = "GIANG_VIEN", "Giang vien"

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Hoat dong"
        INACTIVE = "INACTIVE", "Khong hoat dong"
        LOCKED = "LOCKED", "Bi khoa"

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="profile")
    student = models.OneToOneField(
        "Student",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="account_profile",
    )
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SINH_VIEN)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    def __str__(self) -> str:
        return f"{self.user.username} ({self.role})"


class Student(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Dang hoc"
        INACTIVE = "INACTIVE", "Tam ngung"
        SOFT_DELETED = "SOFT_DELETED", "Da xoa mem"

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


class Classroom(models.Model):
    class Status(models.TextChoices):
        OPEN = "OPEN", "Dang mo"
        CLOSED = "CLOSED", "Da dong"

    ma_lop_hp = models.CharField(max_length=30, unique=True)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="classrooms")
    giang_vien = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="teaching_classes",
    )
    hoc_ky = models.CharField(max_length=10)
    nam_hoc = models.CharField(max_length=20)
    phong_hoc = models.CharField(max_length=50, blank=True)
    lich_hoc = models.CharField(max_length=120, blank=True)
    si_so_toi_da = models.PositiveSmallIntegerField(default=60)
    trang_thai = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-nam_hoc", "-hoc_ky", "ma_lop_hp"]

    def __str__(self) -> str:
        return f"{self.ma_lop_hp} - {self.course.ma_hp} - HK{self.hoc_ky} {self.nam_hoc}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        DANG_HOC = "DANG_HOC", "Dang hoc"
        HOAN_THANH = "HOAN_THANH", "Hoan thanh"
        HUY = "HUY", "Huy"

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="enrollments")
    classroom = models.ForeignKey(
        Classroom,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="enrollments",
    )
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
            ),
            models.UniqueConstraint(
                fields=["student", "classroom"],
                condition=Q(classroom__isnull=False),
                name="uniq_student_classroom",
            ),
        ]
        ordering = ["-nam_hoc", "-hoc_ky", "course__ma_hp"]

    def sync_from_classroom(self) -> None:
        if not self.classroom_id:
            return
        self.course = self.classroom.course
        self.hoc_ky = self.classroom.hoc_ky
        self.nam_hoc = self.classroom.nam_hoc

    def clean(self) -> None:
        if self.classroom and self.classroom.trang_thai == Classroom.Status.CLOSED and self.pk is None:
            raise ValidationError({"classroom": "Lop hoc phan da dong dang ky."})
        if self.student and self.student.trang_thai == Student.Status.SOFT_DELETED:
            raise ValidationError({"student": "Khong the dang ky cho sinh vien da xoa mem."})

    def save(self, *args, **kwargs):
        self.sync_from_classroom()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        class_code = self.classroom.ma_lop_hp if self.classroom_id else "N/A"
        return f"{self.student.ma_sv} | {self.course.ma_hp} | {class_code} | HK{self.hoc_ky} {self.nam_hoc}"


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
                raise ValidationError({field_name: "Diem bat buoc nhap."})
            if value < Decimal("0.00") or value > Decimal("10.00"):
                raise ValidationError({field_name: "Diem phai trong khoang 0 -> 10."})

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


class Attendance(models.Model):
    class Status(models.TextChoices):
        PRESENT = "PRESENT", "Co mat"
        ABSENT = "ABSENT", "Vang"
        LATE = "LATE", "Di muon"
        EXCUSED = "EXCUSED", "Co phep"

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name="attendances")
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name="attendances")
    ngay_hoc = models.DateField()
    trang_thai = models.CharField(max_length=20, choices=Status.choices, default=Status.PRESENT)
    ghi_chu = models.CharField(max_length=255, blank=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="attendance_updates",
    )
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["classroom", "enrollment", "ngay_hoc"],
                name="uniq_attendance_per_session",
            )
        ]
        ordering = ["-ngay_hoc", "enrollment__student__ma_sv"]

    def clean(self) -> None:
        if self.enrollment_id and self.classroom_id and self.enrollment.classroom_id != self.classroom_id:
            raise ValidationError({"enrollment": "Dang ky hoc phan khong thuoc lop hoc phan nay."})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.classroom.ma_lop_hp} | {self.enrollment.student.ma_sv} | {self.ngay_hoc} | {self.trang_thai}"


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
