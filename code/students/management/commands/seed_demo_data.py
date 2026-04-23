from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from students.models import (
    AcademicStanding,
    Attendance,
    AuditLog,
    ClassificationRule,
    Classroom,
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
        if options["reset"]:
            self._reset_business_data()

        ensure_default_classification_rules()
        accounts = self._seed_accounts_and_students()
        self._seed_business_data()

        self.stdout.write(self.style.SUCCESS("Seed du lieu demo thanh cong."))
        self.stdout.write(self.style.WARNING("Tai khoan demo:"))
        for account in accounts:
            self.stdout.write(f"- {account['username']} / {account['password']} ({account['role']})")

    def _reset_business_data(self):
        Attendance.objects.all().delete()
        Grade.objects.all().delete()
        Enrollment.objects.all().delete()
        Classroom.objects.all().delete()
        GPASemester.objects.all().delete()
        AcademicStanding.objects.all().delete()
        ClassificationRule.objects.all().delete()
        AuditLog.objects.all().delete()
        Course.objects.all().delete()
        Student.objects.all().delete()

    def _upsert_user(self, *, username: str, password: str, role: str, is_staff: bool, is_superuser: bool, student=None):
        User = get_user_model()
        user, _ = User.objects.get_or_create(username=username)
        user.is_staff = is_staff
        user.is_superuser = is_superuser
        user.is_active = True
        user.set_password(password)
        user.save()

        UserProfile.objects.update_or_create(
            user=user,
            defaults={
                "role": role,
                "status": UserProfile.Status.ACTIVE,
                "student": student,
            },
        )
        return user

    def _seed_accounts_and_students(self):
        User = get_user_model()
        old_demo_usernames = ["admin_sms", "daotao", "daotao01", "covan", "covan01", "giangvien01"]
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
                "username": "giangvien",
                "password": "123456",
                "role": UserProfile.Role.GIANG_VIEN,
                "is_staff": False,
                "is_superuser": False,
            },
            {
                "username": "giangvien2",
                "password": "123456",
                "role": UserProfile.Role.GIANG_VIEN,
                "is_staff": False,
                "is_superuser": False,
            },
        ]

        for spec in account_specs:
            self._upsert_user(
                username=spec["username"],
                password=spec["password"],
                role=spec["role"],
                is_staff=spec["is_staff"],
                is_superuser=spec["is_superuser"],
            )

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

        for item in students_data:
            student, _ = Student.objects.update_or_create(ma_sv=item["ma_sv"], defaults=item)
            username = item["ma_sv"].lower()
            self._upsert_user(
                username=username,
                password="123456",
                role=UserProfile.Role.SINH_VIEN,
                is_staff=False,
                is_superuser=False,
                student=student,
            )
            account_specs.append(
                {
                    "username": username,
                    "password": "123456",
                    "role": UserProfile.Role.SINH_VIEN,
                }
            )

        return account_specs

    def _seed_business_data(self):
        User = get_user_model()
        students = {student.ma_sv: student for student in Student.objects.all()}

        courses_data = [
            {"ma_hp": "CS101", "ten_hp": "Nhap mon lap trinh", "so_tin_chi": 3},
            {"ma_hp": "CS102", "ten_hp": "Co so du lieu", "so_tin_chi": 3},
            {"ma_hp": "MATH101", "ten_hp": "Giai tich 1", "so_tin_chi": 4},
            {"ma_hp": "ENG101", "ten_hp": "Tieng Anh hoc thuat", "so_tin_chi": 2},
        ]
        courses = {}
        for item in courses_data:
            course, _ = Course.objects.update_or_create(ma_hp=item["ma_hp"], defaults=item)
            courses[item["ma_hp"]] = course

        gv1 = User.objects.get(username="giangvien")
        gv2 = User.objects.get(username="giangvien2")

        classroom_specs = [
            {
                "ma_lop_hp": "LHP-CS101-01",
                "course": courses["CS101"],
                "giang_vien": gv1,
                "hoc_ky": "1",
                "nam_hoc": "2025-2026",
                "phong_hoc": "A301",
                "lich_hoc": "Thu 2-4, tiet 1-3",
                "si_so_toi_da": 60,
                "trang_thai": Classroom.Status.OPEN,
            },
            {
                "ma_lop_hp": "LHP-CS102-01",
                "course": courses["CS102"],
                "giang_vien": gv1,
                "hoc_ky": "1",
                "nam_hoc": "2025-2026",
                "phong_hoc": "A402",
                "lich_hoc": "Thu 3-5, tiet 4-6",
                "si_so_toi_da": 60,
                "trang_thai": Classroom.Status.OPEN,
            },
            {
                "ma_lop_hp": "LHP-MATH101-01",
                "course": courses["MATH101"],
                "giang_vien": gv2,
                "hoc_ky": "1",
                "nam_hoc": "2025-2026",
                "phong_hoc": "B201",
                "lich_hoc": "Thu 2-6, tiet 7-9",
                "si_so_toi_da": 80,
                "trang_thai": Classroom.Status.OPEN,
            },
            {
                "ma_lop_hp": "LHP-ENG101-01",
                "course": courses["ENG101"],
                "giang_vien": gv2,
                "hoc_ky": "2",
                "nam_hoc": "2025-2026",
                "phong_hoc": "C105",
                "lich_hoc": "Thu 5, tiet 1-3",
                "si_so_toi_da": 80,
                "trang_thai": Classroom.Status.OPEN,
            },
        ]

        classrooms = {}
        for spec in classroom_specs:
            classroom, _ = Classroom.objects.update_or_create(
                ma_lop_hp=spec["ma_lop_hp"],
                defaults=spec,
            )
            classrooms[classroom.ma_lop_hp] = classroom

        enrollment_specs = [
            ("SV001", "LHP-CS101-01"),
            ("SV001", "LHP-CS102-01"),
            ("SV001", "LHP-ENG101-01"),
            ("SV002", "LHP-CS101-01"),
            ("SV002", "LHP-MATH101-01"),
            ("SV003", "LHP-ENG101-01"),
            ("SV004", "LHP-CS101-01"),
            ("SV004", "LHP-ENG101-01"),
        ]

        enrollments = {}
        for ma_sv, ma_lop_hp in enrollment_specs:
            student = students[ma_sv]
            classroom = classrooms[ma_lop_hp]
            enrollment, _ = Enrollment.objects.update_or_create(
                student=student,
                course=classroom.course,
                hoc_ky=classroom.hoc_ky,
                nam_hoc=classroom.nam_hoc,
                defaults={
                    "classroom": classroom,
                    "trang_thai": Enrollment.Status.DANG_HOC,
                },
            )
            enrollments[(ma_sv, ma_lop_hp)] = enrollment

        grades_data = [
            ("SV001", "LHP-CS101-01", Decimal("9.0"), Decimal("8.0"), Decimal("7.0"), 1),
            ("SV001", "LHP-CS102-01", Decimal("10.0"), Decimal("9.0"), Decimal("8.5"), 1),
            ("SV001", "LHP-ENG101-01", Decimal("8.0"), Decimal("7.0"), Decimal("7.5"), 1),
            ("SV002", "LHP-CS101-01", Decimal("6.0"), Decimal("5.0"), Decimal("4.5"), 1),
            ("SV002", "LHP-CS101-01", Decimal("8.0"), Decimal("7.0"), Decimal("6.5"), 2),
            ("SV002", "LHP-MATH101-01", Decimal("7.0"), Decimal("6.0"), Decimal("5.0"), 1),
            ("SV003", "LHP-ENG101-01", Decimal("9.0"), Decimal("8.5"), Decimal("8.0"), 1),
            ("SV004", "LHP-CS101-01", Decimal("5.0"), Decimal("4.0"), Decimal("4.0"), 1),
            ("SV004", "LHP-ENG101-01", Decimal("7.0"), Decimal("6.5"), Decimal("7.0"), 1),
        ]

        for ma_sv, ma_lop_hp, diem_cc, diem_qt, diem_thi, lan_hoc in grades_data:
            enrollment = enrollments[(ma_sv, ma_lop_hp)]
            Grade.objects.update_or_create(
                enrollment=enrollment,
                lan_hoc=lan_hoc,
                defaults={
                    "diem_chuyen_can": diem_cc,
                    "diem_qua_trinh": diem_qt,
                    "diem_thi": diem_thi,
                },
            )

        attendance_day = date(2026, 4, 20)
        for enrollment in enrollments.values():
            Attendance.objects.update_or_create(
                classroom=enrollment.classroom,
                enrollment=enrollment,
                ngay_hoc=attendance_day,
                defaults={
                    "trang_thai": Attendance.Status.PRESENT,
                    "ghi_chu": "",
                    "updated_by": enrollment.classroom.giang_vien,
                },
            )

        for student in students.values():
            recalculate_gpa_for_student(student)
