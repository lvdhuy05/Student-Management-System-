from decimal import Decimal, ROUND_HALF_UP

from django.db import transaction

from .models import AcademicStanding, ClassificationRule, GPASemester, Grade, Student

DEFAULT_CLASSIFICATION_RULES = [
    (Decimal("3.60"), Decimal("4.00"), "Xuất sắc"),
    (Decimal("3.20"), Decimal("3.59"), "Giỏi"),
    (Decimal("2.50"), Decimal("3.19"), "Khá"),
    (Decimal("2.00"), Decimal("2.49"), "Trung bình"),
    (Decimal("0.00"), Decimal("1.99"), "Yếu"),
]


def ensure_default_classification_rules() -> None:
    if ClassificationRule.objects.filter(kich_hoat=True).exists():
        return
    for diem_tu, diem_den, nhan_xep_loai in DEFAULT_CLASSIFICATION_RULES:
        ClassificationRule.objects.create(
            diem_tu=diem_tu,
            diem_den=diem_den,
            nhan_xep_loai=nhan_xep_loai,
            kich_hoat=True,
        )


def get_classification_for_gpa(gpa: Decimal) -> str:
    rules = ClassificationRule.objects.filter(kich_hoat=True).order_by("-diem_tu")
    for rule in rules:
        if rule.diem_tu <= gpa <= rule.diem_den:
            return rule.nhan_xep_loai
    for diem_tu, diem_den, nhan_xep_loai in DEFAULT_CLASSIFICATION_RULES:
        if diem_tu <= gpa <= diem_den:
            return nhan_xep_loai
    return "Chưa xếp loại"


def _semester_sort_key(nam_hoc: str, hoc_ky: str) -> tuple[int, int]:
    try:
        year_start = int(str(nam_hoc).split("-")[0])
    except (ValueError, TypeError, IndexError):
        year_start = 0
    try:
        semester_number = int(hoc_ky)
    except (ValueError, TypeError):
        semester_number = 99
    return year_start, semester_number


@transaction.atomic
def recalculate_gpa_for_student(student: Student) -> dict[str, Decimal | str]:
    ensure_default_classification_rules()

    grades = (
        Grade.objects.filter(enrollment__student=student)
        .select_related("enrollment__course")
        .order_by("enrollment__course_id", "-lan_hoc", "-updated_at")
    )

    latest_grade_by_course: dict[int, Grade] = {}
    for grade in grades:
        course_id = grade.enrollment.course_id
        if course_id not in latest_grade_by_course:
            latest_grade_by_course[course_id] = grade

    effective_grades = list(latest_grade_by_course.values())

    total_credits = 0
    total_points = Decimal("0.00")
    per_semester: dict[tuple[str, str], dict[str, Decimal | int]] = {}

    for grade in effective_grades:
        credits = int(grade.enrollment.course.so_tin_chi)
        points = grade.diem_he_4 * Decimal(credits)
        total_credits += credits
        total_points += points

        sem_key = (grade.enrollment.nam_hoc, grade.enrollment.hoc_ky)
        if sem_key not in per_semester:
            per_semester[sem_key] = {"credits": 0, "points": Decimal("0.00")}
        per_semester[sem_key]["credits"] = int(per_semester[sem_key]["credits"]) + credits
        per_semester[sem_key]["points"] = Decimal(per_semester[sem_key]["points"]) + points

    if total_credits == 0:
        cumulative_gpa = Decimal("0.00")
    else:
        cumulative_gpa = (total_points / Decimal(total_credits)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    xep_loai = get_classification_for_gpa(cumulative_gpa)
    AcademicStanding.objects.update_or_create(
        student=student,
        defaults={"gpa_tich_luy": cumulative_gpa, "xep_loai": xep_loai},
    )

    running_credits = 0
    sorted_semesters = sorted(per_semester.keys(), key=lambda s: _semester_sort_key(s[0], s[1]))
    for nam_hoc, hoc_ky in sorted_semesters:
        semester_data = per_semester[(nam_hoc, hoc_ky)]
        sem_credits = int(semester_data["credits"])
        sem_points = Decimal(semester_data["points"])
        sem_gpa = Decimal("0.00")
        if sem_credits > 0:
            sem_gpa = (sem_points / Decimal(sem_credits)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        running_credits += sem_credits

        GPASemester.objects.update_or_create(
            student=student,
            hoc_ky=hoc_ky,
            nam_hoc=nam_hoc,
            defaults={"gpa_he_4": sem_gpa, "tong_tin_chi_tich_luy": running_credits},
        )

    return {"gpa": cumulative_gpa, "xep_loai": xep_loai}
