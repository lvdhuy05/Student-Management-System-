from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import (
    AcademicStanding,
    AuditLog,
    ClassificationRule,
    Course,
    Enrollment,
    GPASemester,
    Grade,
    Student,
    UserProfile,
)
from students.services import ensure_default_classification_rules, recalculate_gpa_for_student


class Command(BaseCommand):
    help = "Seed tai khoan phan quyen va du lieu demo cho he thong SMS."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Xoa du lieu nghiep vu cu truoc khi seed lai.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        reset = options["reset"]
        if reset:
            self._reset_business_data()

        ensure_default_classification_rules()
        accounts = self._seed_accounts()
        self._seed_business_data()

        self.stdout.write(self.style.SUCCESS("Seed du lieu demo thanh cong."))
        self.stdout.write(self.style.WARNING("Tai khoan demo:"))
        for account in accounts:
            self.stdout.write(
                f"- {account['username']} / {account['password']} ({account['role']})"
            )

    def _reset_business_data(self):
        Grade.objects.all().delete()
        Enrollment.objects.all().delete()
        GPASemester.objects.all().delete()
        AcademicStanding.objects.all().delete()
        ClassificationRule.objects.all().delete()
        AuditLog.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()

    def _seed_accounts(self):
        User = get_user_model()
        old_demo_usernames = ["admin_sms", "daotao01", "giangvien01", "covan01"]
        User.objects.filter(username__in=old_demo_usernames).delete()

        account_specs = [
            {
                "username": "admin",
                "password": "123456",
                "role": UserProfile.Role.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
            {
                "username": "daotao",
                "password": "123456",
                "role": UserProfile.Role.DAO_TAO,
                "is_staff": True,
                "is_superuser": False,
            },
            {
                "username": "giangvien",
                "password": "123456",
                "role": UserProfile.Role.GIANG_VIEN,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "covan",
                "password": "123456",
                "role": UserProfile.Role.CO_VAN,
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        for spec in account_specs:
            user, created = User.objects.get_or_create(
                username=spec["username"],
                defaults={
                    "is_staff": spec["is_staff"],
                    "is_superuser": spec["is_superuser"],
                    "is_active": True,
                },
            )
            if created:
                user.set_password(spec["password"])
            else:
                user.is_staff = spec["is_staff"]
                user.is_superuser = spec["is_superuser"]
                user.is_active = True
                user.set_password(spec["password"])
            user.save()

            UserProfile.objects.update_or_create(
                user=user,
                defaults={
                    "role": spec["role"],
                    "status": UserProfile.Status.ACTIVE,
                },
            )
        return account_specs

    def _seed_business_data(self):
        students_data = [
            {
                "ma_sv": "SV001",
                "ho_ten": "Nguyen Van Minh",
                "ngay_sinh": "2004-01-12",
                "gioi_tinh": "Nam",
                "email": "sv001@sms.edu.vn",
                "so_dien_thoai": "0901000001",
                "khoa": "CNTT",
                "nganh": "Khoa hoc may tinh",
                "lop": "K68A",
                "khoa_hoc": "2022-2026",
            },
            {
                "ma_sv": "SV002",
                "ho_ten": "Tran Thi Lan",
                "ngay_sinh": "2004-04-21",
                "gioi_tinh": "Nu",
                "email": "sv002@sms.edu.vn",
                "so_dien_thoai": "0901000002",
                "khoa": "CNTT",
                "nganh": "Ky thuat phan mem",
                "lop": "K68B",
                "khoa_hoc": "2022-2026",
            },
            {
                "ma_sv": "SV003",
                "ho_ten": "Le Quoc Bao",
                "ngay_sinh": "2003-09-15",
                "gioi_tinh": "Nam",
                "email": "sv003@sms.edu.vn",
                "so_dien_thoai": "0901000003",
                "khoa": "Kinh te",
                "nganh": "Quan tri kinh doanh",
                "lop": "K67QTKD",
                "khoa_hoc": "2021-2025",
            },
            {
                "ma_sv": "SV004",
                "ho_ten": "Pham Ngoc Anh",
                "ngay_sinh": "2004-11-30",
                "gioi_tinh": "Nu",
                "email": "sv004@sms.edu.vn",
                "so_dien_thoai": "0901000004",
                "khoa": "Ngoai ngu",
                "nganh": "Ngon ngu Anh",
                "lop": "K68NA",
                "khoa_hoc": "2022-2026",
            },
        ]

        courses_data = [
            {"ma_hp": "CS101", "ten_hp": "Nhập môn lập trình", "so_tin_chi": 3},
            {"ma_hp": "CS102", "ten_hp": "Cơ sở dữ liệu", "so_tin_chi": 3},
            {"ma_hp": "MATH101", "ten_hp": "Giải tích 1", "so_tin_chi": 4},
            {"ma_hp": "ENG101", "ten_hp": "Tiếng Anh học thuật", "so_tin_chi": 2},
        ]

        students = {}
        for item in students_data:
            student, _ = Student.objects.update_or_create(
                ma_sv=item["ma_sv"],
                defaults=item,
            )
            students[item["ma_sv"]] = student

        courses = {}
        for item in courses_data:
            course, _ = Course.objects.update_or_create(
                ma_hp=item["ma_hp"],
                defaults=item,
            )
            courses[item["ma_hp"]] = course

        enroll_specs = [
            ("SV001", "CS101", "1", "2025-2026"),
            ("SV001", "CS102", "1", "2025-2026"),
            ("SV001", "ENG101", "2", "2025-2026"),
            ("SV002", "CS101", "1", "2025-2026"),
            ("SV002", "MATH101", "1", "2025-2026"),
            ("SV003", "ENG101", "1", "2024-2025"),
            ("SV004", "CS101", "1", "2025-2026"),
            ("SV004", "ENG101", "1", "2025-2026"),
        ]

        enrollments = {}
        for ma_sv, ma_hp, hoc_ky, nam_hoc in enroll_specs:
            enrollment, _ = Enrollment.objects.update_or_create(
                student=students[ma_sv],
                course=courses[ma_hp],
                hoc_ky=hoc_ky,
                nam_hoc=nam_hoc,
                defaults={"trang_thai": Enrollment.Status.DANG_HOC},
            )
            enrollments[(ma_sv, ma_hp, hoc_ky, nam_hoc)] = enrollment

        grades_data = [
            ("SV001", "CS101", "1", "2025-2026", Decimal("9.0"), Decimal("8.0"), Decimal("7.0"), 1),
            ("SV001", "CS102", "1", "2025-2026", Decimal("10.0"), Decimal("9.0"), Decimal("8.5"), 1),
            ("SV001", "ENG101", "2", "2025-2026", Decimal("8.0"), Decimal("7.0"), Decimal("7.5"), 1),
            ("SV002", "CS101", "1", "2025-2026", Decimal("6.0"), Decimal("5.0"), Decimal("4.5"), 1),
            ("SV002", "CS101", "1", "2025-2026", Decimal("8.0"), Decimal("7.0"), Decimal("6.5"), 2),
            ("SV002", "MATH101", "1", "2025-2026", Decimal("7.0"), Decimal("6.0"), Decimal("5.0"), 1),
            ("SV003", "ENG101", "1", "2024-2025", Decimal("9.0"), Decimal("8.5"), Decimal("8.0"), 1),
            ("SV004", "CS101", "1", "2025-2026", Decimal("5.0"), Decimal("4.0"), Decimal("4.0"), 1),
            ("SV004", "ENG101", "1", "2025-2026", Decimal("7.0"), Decimal("6.5"), Decimal("7.0"), 1),
        ]

        for ma_sv, ma_hp, hoc_ky, nam_hoc, diem_cc, diem_qt, diem_thi, lan_hoc in grades_data:
            enrollment = enrollments[(ma_sv, ma_hp, hoc_ky, nam_hoc)]
            Grade.objects.update_or_create(
                enrollment=enrollment,
                lan_hoc=lan_hoc,
                defaults={
                    "diem_chuyen_can": diem_cc,
                    "diem_qua_trinh": diem_qt,
                    "diem_thi": diem_thi,
                },
            )

        for student in students.values():
            recalculate_gpa_for_student(student)
