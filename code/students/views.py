import csv

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CourseForm, EnrollmentForm, GradeInputForm, StudentForm
from .authz import role_required
from .models import (
    AcademicStanding,
    AuditLog,
    Course,
    Enrollment,
    GPASemester,
    Grade,
    Student,
    UserProfile,
)
from .services import ensure_default_classification_rules, recalculate_gpa_for_student

READ_ROLES = (
    UserProfile.Role.ADMIN,
    UserProfile.Role.DAO_TAO,
    UserProfile.Role.GIANG_VIEN,
    UserProfile.Role.CO_VAN,
)
MANAGE_ROLES = (UserProfile.Role.ADMIN, UserProfile.Role.DAO_TAO)
GRADE_ROLES = (UserProfile.Role.ADMIN, UserProfile.Role.DAO_TAO, UserProfile.Role.GIANG_VIEN)


def _student_to_dict(student: Student) -> dict:
    return {
        "ma_sv": student.ma_sv,
        "ho_ten": student.ho_ten,
        "email": student.email,
        "khoa": student.khoa,
        "nganh": student.nganh,
        "lop": student.lop,
        "trang_thai": student.trang_thai,
    }


def _log_action(request, action: str, obj: str, before: dict | None = None, after: dict | None = None) -> None:
    AuditLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        hanh_dong=action,
        doi_tuong=obj,
        truoc_thay_doi=before,
        sau_thay_doi=after,
    )


@role_required(*READ_ROLES)
def dashboard(request):
    ensure_default_classification_rules()
    context = {
        "student_count": Student.objects.exclude(trang_thai=Student.Status.SOFT_DELETED).count(),
        "course_count": Course.objects.count(),
        "enrollment_count": Enrollment.objects.count(),
        "grade_count": Grade.objects.count(),
        "recent_logs": AuditLog.objects.select_related("actor")[:8],
    }
    return render(request, "students/dashboard.html", context)


@role_required(*READ_ROLES)
def student_list(request):
    students = Student.objects.all()

    keyword = request.GET.get("keyword", "").strip()
    khoa = request.GET.get("khoa", "").strip()
    nganh = request.GET.get("nganh", "").strip()
    lop = request.GET.get("lop", "").strip()
    trang_thai = request.GET.get("trang_thai", "").strip()

    if keyword:
        students = students.filter(Q(ma_sv__icontains=keyword) | Q(ho_ten__icontains=keyword))
    if khoa:
        students = students.filter(khoa__icontains=khoa)
    if nganh:
        students = students.filter(nganh__icontains=nganh)
    if lop:
        students = students.filter(lop__icontains=lop)
    if trang_thai:
        students = students.filter(trang_thai=trang_thai)
    else:
        students = students.exclude(trang_thai=Student.Status.SOFT_DELETED)

    paginator = Paginator(students.order_by("ma_sv"), 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "students/student_list.html",
        {
            "page_obj": page_obj,
            "filters": {
                "keyword": keyword,
                "khoa": khoa,
                "nganh": nganh,
                "lop": lop,
                "trang_thai": trang_thai,
            },
            "status_choices": Student.Status.choices,
        },
    )


@role_required(*MANAGE_ROLES)
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            _log_action(request, "TAO_SINH_VIEN", f"Student:{student.ma_sv}", after=_student_to_dict(student))
            messages.success(request, "Đã tạo sinh viên thành công.")
            return redirect("students:student_detail", ma_sv=student.ma_sv)
    else:
        form = StudentForm()
    return render(request, "students/student_form.html", {"form": form, "mode": "create"})


@role_required(*MANAGE_ROLES)
def student_update(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    before = _student_to_dict(student)
    if request.method == "POST":
        form = StudentForm(request.POST, instance=student)
        if form.is_valid():
            student = form.save()
            _log_action(
                request,
                "CAP_NHAT_SINH_VIEN",
                f"Student:{student.ma_sv}",
                before=before,
                after=_student_to_dict(student),
            )
            messages.success(request, "Đã cập nhật sinh viên.")
            return redirect("students:student_detail", ma_sv=student.ma_sv)
    else:
        form = StudentForm(instance=student)
    return render(request, "students/student_form.html", {"form": form, "mode": "update", "student": student})


@role_required(*MANAGE_ROLES)
def student_delete(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    if request.method == "POST":
        before = _student_to_dict(student)
        student.soft_delete()
        _log_action(request, "XOA_MEM_SINH_VIEN", f"Student:{student.ma_sv}", before=before, after=_student_to_dict(student))
        messages.warning(request, f"Đã xóa mềm sinh viên {student.ma_sv}.")
    return redirect("students:student_list")


@role_required(*READ_ROLES)
def student_detail(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky")
    )
    gpa_semesters = GPASemester.objects.filter(student=student).order_by("-nam_hoc", "-hoc_ky")
    standing = AcademicStanding.objects.filter(student=student).first()
    return render(
        request,
        "students/student_detail.html",
        {
            "student": student,
            "enrollments": enrollments,
            "gpa_semesters": gpa_semesters,
            "standing": standing,
        },
    )


@role_required(*MANAGE_ROLES)
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            _log_action(request, "TAO_HOC_PHAN", f"Course:{course.ma_hp}", after={"ma_hp": course.ma_hp, "ten_hp": course.ten_hp})
            messages.success(request, "Đã tạo học phần.")
            return redirect("students:dashboard")
    else:
        form = CourseForm()
    return render(request, "students/course_form.html", {"form": form})


@role_required(*MANAGE_ROLES)
def enrollment_create(request):
    if request.method == "POST":
        form = EnrollmentForm(request.POST)
        if form.is_valid():
            enrollment = form.save()
            _log_action(
                request,
                "TAO_DANG_KY_HOC_PHAN",
                f"Enrollment:{enrollment.id}",
                after={
                    "student": enrollment.student.ma_sv,
                    "course": enrollment.course.ma_hp,
                    "hoc_ky": enrollment.hoc_ky,
                    "nam_hoc": enrollment.nam_hoc,
                },
            )
            messages.success(request, "Đã tạo đăng ký học phần.")
            return redirect("students:student_detail", ma_sv=enrollment.student.ma_sv)
    else:
        form = EnrollmentForm()
    return render(request, "students/enrollment_form.html", {"form": form})


@role_required(*GRADE_ROLES)
def grade_input(request):
    if request.method == "POST":
        form = GradeInputForm(request.POST)
        if form.is_valid():
            grade = form.save()
            result = recalculate_gpa_for_student(grade.enrollment.student)
            _log_action(
                request,
                "NHAP_DIEM",
                f"Grade:{grade.id}",
                after={
                    "enrollment": grade.enrollment.id,
                    "diem_chuyen_can": str(grade.diem_chuyen_can),
                    "diem_qua_trinh": str(grade.diem_qua_trinh),
                    "diem_thi": str(grade.diem_thi),
                    "diem_tong_ket_10": str(grade.diem_tong_ket_10),
                    "diem_he_4": str(grade.diem_he_4),
                    "diem_chu": grade.diem_chu,
                    "gpa_tich_luy": str(result["gpa"]),
                    "xep_loai": result["xep_loai"],
                },
            )
            messages.success(
                request,
                f"Nhập điểm thành công. GPA hiện tại: {result['gpa']} ({result['xep_loai']}).",
            )
            return redirect("students:student_detail", ma_sv=grade.enrollment.student.ma_sv)
    else:
        selected_student_id = request.GET.get("student")
        form = GradeInputForm(initial={"student": selected_student_id} if selected_student_id else None)

    return render(request, "students/grade_form.html", {"form": form})


@role_required(*READ_ROLES)
def transcript_report(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
    )
    standing = AcademicStanding.objects.filter(student=student).first()
    return render(
        request,
        "students/transcript_report.html",
        {"student": student, "enrollments": enrollments, "standing": standing},
    )


@role_required(*READ_ROLES)
def transcript_csv(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="bang-diem-{student.ma_sv}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Mã SV", "Họ tên", student.ma_sv, student.ho_ten])
    writer.writerow([])
    writer.writerow(
        [
            "Học kỳ",
            "Năm học",
            "Ma HP",
            "Tên học phần",
            "Tín chỉ",
            "Diem chuyên cần",
            "Diem QT",
            "Điểm thi",
            "Diem TK (10)",
            "Điểm hệ 4",
            "Điểm chữ",
            "Lần học",
        ]
    )

    for enrollment in enrollments:
        latest_grade = enrollment.grades.order_by("-lan_hoc", "-updated_at").first()
        writer.writerow(
            [
                enrollment.hoc_ky,
                enrollment.nam_hoc,
                enrollment.course.ma_hp,
                enrollment.course.ten_hp,
                enrollment.course.so_tin_chi,
                latest_grade.diem_chuyen_can if latest_grade else "",
                latest_grade.diem_qua_trinh if latest_grade else "",
                latest_grade.diem_thi if latest_grade else "",
                latest_grade.diem_tong_ket_10 if latest_grade else "",
                latest_grade.diem_he_4 if latest_grade else "",
                latest_grade.diem_chu if latest_grade else "",
                latest_grade.lan_hoc if latest_grade else "",
            ]
        )

    return response
