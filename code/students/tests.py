from decimal import Decimal

from django.test import TestCase

from .models import AcademicStanding, Course, Enrollment, Grade, Student
from .services import recalculate_gpa_for_student


class GradeCalculationTests(TestCase):
    def setUp(self):
        self.student = Student.objects.create(
            ma_sv="SV001",
            ho_ten="Nguyen Van A",
            ngay_sinh="2005-01-01",
            gioi_tinh="Nam",
            email="sva@example.com",
            so_dien_thoai="0912345678",
            khoa="CNTT",
            nganh="Khoa hoc may tinh",
            lop="K68A",
            khoa_hoc="2023-2027",
        )
        self.course = Course.objects.create(ma_hp="CS101", ten_hp="Nhap mon lap trinh", so_tin_chi=3)
        self.enrollment = Enrollment.objects.create(student=self.student, course=self.course, hoc_ky="1", nam_hoc="2025-2026")

    def test_grade_auto_calculated_on_save(self):
        grade = Grade.objects.create(
            enrollment=self.enrollment,
            diem_chuyen_can=Decimal("10.00"),
            diem_qua_trinh=Decimal("8.00"),
            diem_thi=Decimal("6.00"),
            lan_hoc=1,
        )
        self.assertEqual(grade.diem_tong_ket_10, Decimal("7.00"))
        self.assertEqual(grade.diem_he_4, Decimal("3.00"))
        self.assertEqual(grade.diem_chu, "B")

    def test_recalculate_uses_latest_attempt_and_updates_standing(self):
        Grade.objects.create(
            enrollment=self.enrollment,
            diem_chuyen_can=Decimal("5.00"),
            diem_qua_trinh=Decimal("5.00"),
            diem_thi=Decimal("5.00"),
            lan_hoc=1,
        )
        Grade.objects.create(
            enrollment=self.enrollment,
            diem_chuyen_can=Decimal("9.00"),
            diem_qua_trinh=Decimal("9.00"),
            diem_thi=Decimal("9.00"),
            lan_hoc=2,
        )

        result = recalculate_gpa_for_student(self.student)
        standing = AcademicStanding.objects.get(student=self.student)

        self.assertEqual(result["gpa"], Decimal("4.00"))
        self.assertEqual(standing.gpa_tich_luy, Decimal("4.00"))
        self.assertEqual(standing.xep_loai, "Xuất sắc")
