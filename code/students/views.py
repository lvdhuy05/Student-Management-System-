import csv
from datetime import date, timedelta

from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone

from .authz import get_user_role, get_user_student, role_required
from .forms import (
    ClassroomForm,
    CourseForm,
    EnrollmentForm,
    GradeInputForm,
    StudentEnrollmentForm,
    StudentForm,
)
from .models import (
    AcademicStanding,
    Attendance,
    AuditLog,
    Classroom,
    Course,
    Enrollment,
    GPASemester,
    Grade,
    Student,
    UserProfile,
)
from .services import ensure_default_classification_rules, recalculate_gpa_for_student

ALL_ROLES = (UserProfile.Role.ADMIN, UserProfile.Role.SINH_VIEN, UserProfile.Role.GIANG_VIEN)
ADMIN_ROLES = (UserProfile.Role.ADMIN,)
STUDENT_ROLES = (UserProfile.Role.SINH_VIEN,)
TEACHER_ROLES = (UserProfile.Role.GIANG_VIEN,)
GRADE_ROLES = (UserProfile.Role.ADMIN, UserProfile.Role.GIANG_VIEN)
CLASSROOM_ROLES = (UserProfile.Role.ADMIN, UserProfile.Role.GIANG_VIEN)
STUDENT_ACCESS_ROLES = (UserProfile.Role.ADMIN, UserProfile.Role.SINH_VIEN)


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


def _grade_to_dict(grade: Grade) -> dict:
    return {
        "id": grade.id,
        "enrollment": grade.enrollment_id,
        "lan_hoc": grade.lan_hoc,
        "diem_chuyen_can": str(grade.diem_chuyen_can),
        "diem_qua_trinh": str(grade.diem_qua_trinh),
        "diem_thi": str(grade.diem_thi),
        "diem_tong_ket_10": str(grade.diem_tong_ket_10),
        "diem_he_4": str(grade.diem_he_4),
        "diem_chu": grade.diem_chu,
    }


def _log_action(request, action: str, obj: str, before: dict | None = None, after: dict | None = None) -> None:
    AuditLog.objects.create(
        actor=request.user if request.user.is_authenticated else None,
        hanh_dong=action,
        doi_tuong=obj,
        truoc_thay_doi=before,
        sau_thay_doi=after,
    )


def _can_access_classroom(user, classroom: Classroom) -> bool:
    role = get_user_role(user)
    if role == UserProfile.Role.ADMIN:
        return True
    if role == UserProfile.Role.GIANG_VIEN and classroom.giang_vien_id == user.id:
        return True
    return False


def _safe_next_url(raw_url: str | None) -> str:
    if raw_url and raw_url.startswith("/"):
        return raw_url
    return ""


def _calc_month_growth(queryset, field_name: str = "created_at") -> float:
    now = timezone.now()
    this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    prev_month_start = (this_month_start - timedelta(days=1)).replace(day=1)

    this_month_count = queryset.filter(**{f"{field_name}__gte": this_month_start}).count()
    prev_month_count = queryset.filter(
        **{
            f"{field_name}__gte": prev_month_start,
            f"{field_name}__lt": this_month_start,
        }
    ).count()

    if prev_month_count == 0:
        return 100.0 if this_month_count > 0 else 0.0
    return round(((this_month_count - prev_month_count) / prev_month_count) * 100, 1)


def _attach_progress(classrooms):
    result = []
    for classroom in classrooms:
        student_count = getattr(classroom, "student_count", 0) or 0
        graded_count = getattr(classroom, "graded_count", 0) or 0
        classroom.progress_percent = int((graded_count / student_count) * 100) if student_count else 0
        result.append(classroom)
    return result


@role_required(*ALL_ROLES)
def dashboard(request):
    ensure_default_classification_rules()
    role = get_user_role(request.user)

    if role == UserProfile.Role.ADMIN:
        active_students = Student.objects.exclude(trang_thai=Student.Status.SOFT_DELETED)
        standing_qs = AcademicStanding.objects.exclude(student__trang_thai=Student.Status.SOFT_DELETED)
        standing_count = standing_qs.count()
        graduated_count = standing_qs.filter(gpa_tich_luy__gte=2).count()
        graduation_rate = round((graduated_count / standing_count) * 100, 1) if standing_count else 0.0

        student_growth = _calc_month_growth(active_students)
        classroom_growth = _calc_month_growth(Classroom.objects.all())

        department_stats = list(
            active_students.values("khoa")
            .annotate(total=Count("id"))
            .order_by("-total", "khoa")[:8]
        )
        new_students = active_students.order_by("-created_at")[:6]

        context = {
            "dashboard_mode": "admin",
            "student_count": active_students.count(),
            "course_count": Course.objects.count(),
            "classroom_count": Classroom.objects.count(),
            "faculty_count": active_students.values("khoa").distinct().count(),
            "graduation_rate": graduation_rate,
            "student_growth": student_growth,
            "classroom_growth": classroom_growth,
            "department_stats": department_stats,
            "new_students": new_students,
            "recent_logs": AuditLog.objects.select_related("actor")[:8],
        }
        return render(request, "students/dashboard.html", context)

    if role == UserProfile.Role.SINH_VIEN:
        student = get_user_student(request.user)
        if not student:
            messages.error(request, "Tai khoan sinh vien chua duoc lien ket ho so sinh vien.")
            return render(request, "students/dashboard.html", {"dashboard_mode": "student_missing"})

        enrollments = (
            Enrollment.objects.filter(student=student)
            .select_related("course", "classroom")
            .prefetch_related("grades")
            .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
        )
        standing = AcademicStanding.objects.filter(student=student).first()

        context = {
            "dashboard_mode": "student",
            "student": student,
            "standing": standing,
            "enrollment_count": enrollments.count(),
            "available_classroom_count": Classroom.objects.filter(trang_thai=Classroom.Status.OPEN)
            .exclude(enrollments__student=student)
            .count(),
            "recent_enrollments": enrollments[:6],
        }
        return render(request, "students/dashboard.html", context)

    classrooms = (
        Classroom.objects.filter(giang_vien=request.user)
        .select_related("course")
        .annotate(
            student_count=Count("enrollments", distinct=True),
            graded_count=Count("enrollments", filter=Q(enrollments__grades__isnull=False), distinct=True),
        )
        .order_by("-nam_hoc", "-hoc_ky", "ma_lop_hp")
    )
    classroom_preview = _attach_progress(list(classrooms[:6]))
    context = {
        "dashboard_mode": "teacher",
        "classroom_count": classrooms.count(),
        "student_count": Enrollment.objects.filter(classroom__giang_vien=request.user).values("student_id").distinct().count(),
        "grade_count": Grade.objects.filter(enrollment__classroom__giang_vien=request.user).count(),
        "attendance_days": Attendance.objects.filter(classroom__giang_vien=request.user)
        .values("ngay_hoc")
        .distinct()
        .count(),
        "my_classes": classroom_preview,
    }
    return render(request, "students/dashboard.html", context)


@role_required(*ADMIN_ROLES)
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


@role_required(*ADMIN_ROLES)
def student_create(request):
    if request.method == "POST":
        form = StudentForm(request.POST)
        if form.is_valid():
            student = form.save()
            _log_action(request, "TAO_SINH_VIEN", f"Student:{student.ma_sv}", after=_student_to_dict(student))
            messages.success(request, "Da tao sinh vien thanh cong.")
            return redirect("students:student_detail", ma_sv=student.ma_sv)
    else:
        form = StudentForm()
    return render(request, "students/student_form.html", {"form": form, "mode": "create"})


@role_required(*ADMIN_ROLES)
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
            messages.success(request, "Da cap nhat sinh vien.")
            return redirect("students:student_detail", ma_sv=student.ma_sv)
    else:
        form = StudentForm(instance=student)

    return render(request, "students/student_form.html", {"form": form, "mode": "update", "student": student})


@role_required(*ADMIN_ROLES)
def student_delete(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    if request.method == "POST":
        before = _student_to_dict(student)
        student.soft_delete()
        _log_action(request, "XOA_MEM_SINH_VIEN", f"Student:{student.ma_sv}", before=before, after=_student_to_dict(student))
        messages.warning(request, f"Da xoa mem sinh vien {student.ma_sv}.")
    return redirect("students:student_list")


@role_required(*STUDENT_ACCESS_ROLES)
def student_detail(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    role = get_user_role(request.user)

    if role == UserProfile.Role.SINH_VIEN:
        current_student = get_user_student(request.user)
        if not current_student or current_student.id != student.id:
            messages.error(request, "Ban chi duoc xem thong tin cua chinh minh.")
            return redirect("students:dashboard")

    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course", "classroom")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
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


@role_required(*ADMIN_ROLES)
def course_create(request):
    if request.method == "POST":
        form = CourseForm(request.POST)
        if form.is_valid():
            course = form.save()
            _log_action(request, "TAO_HOC_PHAN", f"Course:{course.ma_hp}", after={"ma_hp": course.ma_hp, "ten_hp": course.ten_hp})
            messages.success(request, "Da tao hoc phan.")
            return redirect("students:dashboard")
    else:
        form = CourseForm()

    return render(request, "students/course_form.html", {"form": form})


@role_required(*ADMIN_ROLES)
def classroom_list(request):
    classrooms = (
        Classroom.objects.select_related("course", "giang_vien")
        .annotate(student_count=Count("enrollments", distinct=True))
        .order_by("-nam_hoc", "-hoc_ky", "ma_lop_hp")
    )
    return render(request, "students/classroom_list.html", {"classrooms": classrooms})


@role_required(*ADMIN_ROLES)
def classroom_create(request):
    if request.method == "POST":
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom = form.save()
            _log_action(
                request,
                "TAO_LOP_HOC_PHAN",
                f"Classroom:{classroom.ma_lop_hp}",
                after={
                    "ma_lop_hp": classroom.ma_lop_hp,
                    "course": classroom.course.ma_hp,
                    "giang_vien": classroom.giang_vien.username if classroom.giang_vien else "",
                    "hoc_ky": classroom.hoc_ky,
                    "nam_hoc": classroom.nam_hoc,
                },
            )
            messages.success(request, "Da tao lop hoc phan.")
            return redirect("students:classroom_list")
    else:
        form = ClassroomForm()

    return render(request, "students/classroom_form.html", {"form": form})


@role_required(*TEACHER_ROLES)
def my_classes(request):
    classrooms = (
        Classroom.objects.filter(giang_vien=request.user)
        .select_related("course")
        .annotate(
            student_count=Count("enrollments", distinct=True),
            graded_count=Count("enrollments", filter=Q(enrollments__grades__isnull=False), distinct=True),
        )
        .order_by("-nam_hoc", "-hoc_ky", "ma_lop_hp")
    )
    return render(request, "students/my_classes.html", {"classrooms": _attach_progress(list(classrooms))})


@role_required(*CLASSROOM_ROLES)
def classroom_detail(request, class_id: int):
    classroom = get_object_or_404(Classroom.objects.select_related("course", "giang_vien"), id=class_id)
    if not _can_access_classroom(request.user, classroom):
        messages.error(request, "Ban khong co quyen truy cap lop hoc phan nay.")
        return redirect("students:dashboard")

    enrollments = (
        Enrollment.objects.filter(classroom=classroom)
        .select_related("student", "course")
        .prefetch_related("grades")
        .order_by("student__ma_sv")
    )

    selected_date_raw = request.GET.get("ngay_hoc") or date.today().isoformat()
    try:
        selected_date = date.fromisoformat(selected_date_raw)
    except ValueError:
        selected_date = date.today()
        selected_date_raw = selected_date.isoformat()

    attendance_qs = Attendance.objects.filter(classroom=classroom, ngay_hoc=selected_date, enrollment__in=enrollments)
    attendance_map = {item.enrollment_id: item for item in attendance_qs}

    roster = []
    for enrollment in enrollments:
        grades = list(enrollment.grades.all())
        latest_grade = grades[0] if grades else None
        roster.append(
            {
                "enrollment": enrollment,
                "latest_grade": latest_grade,
                "attendance": attendance_map.get(enrollment.id),
            }
        )

    attendance_dates = (
        Attendance.objects.filter(classroom=classroom)
        .values_list("ngay_hoc", flat=True)
        .distinct()
        .order_by("-ngay_hoc")[:10]
    )

    return render(
        request,
        "students/classroom_detail.html",
        {
            "classroom": classroom,
            "enrollments": enrollments,
            "roster": roster,
            "selected_date": selected_date_raw,
            "attendance_dates": attendance_dates,
            "attendance_status_choices": Attendance.Status.choices,
        },
    )


@role_required(*CLASSROOM_ROLES)
def attendance_take(request, class_id: int):
    classroom = get_object_or_404(Classroom.objects.select_related("course", "giang_vien"), id=class_id)
    if not _can_access_classroom(request.user, classroom):
        messages.error(request, "Ban khong co quyen diem danh lop hoc phan nay.")
        return redirect("students:dashboard")

    if request.method != "POST":
        return redirect("students:classroom_detail", class_id=classroom.id)

    ngay_hoc_raw = request.POST.get("ngay_hoc", "").strip()
    try:
        ngay_hoc = date.fromisoformat(ngay_hoc_raw)
    except ValueError:
        ngay_hoc = date.today()

    allowed_statuses = {choice[0] for choice in Attendance.Status.choices}
    enrollments = Enrollment.objects.filter(classroom=classroom).select_related("student")

    for enrollment in enrollments:
        status = request.POST.get(f"status_{enrollment.id}", Attendance.Status.PRESENT)
        if status not in allowed_statuses:
            status = Attendance.Status.PRESENT
        ghi_chu = request.POST.get(f"note_{enrollment.id}", "").strip()

        Attendance.objects.update_or_create(
            classroom=classroom,
            enrollment=enrollment,
            ngay_hoc=ngay_hoc,
            defaults={
                "trang_thai": status,
                "ghi_chu": ghi_chu,
                "updated_by": request.user,
            },
        )

    _log_action(
        request,
        "DIEM_DANH_LOP",
        f"Classroom:{classroom.ma_lop_hp}",
        after={"ngay_hoc": ngay_hoc.isoformat(), "so_sinh_vien": enrollments.count()},
    )
    messages.success(request, "Da luu diem danh cho lop hoc phan.")

    detail_url = reverse("students:classroom_detail", kwargs={"class_id": classroom.id})
    return redirect(f"{detail_url}?ngay_hoc={ngay_hoc.isoformat()}")


@role_required(*ADMIN_ROLES)
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
                    "classroom": enrollment.classroom.ma_lop_hp if enrollment.classroom else "",
                    "course": enrollment.course.ma_hp,
                    "hoc_ky": enrollment.hoc_ky,
                    "nam_hoc": enrollment.nam_hoc,
                },
            )
            messages.success(request, "Da tao dang ky hoc phan.")
            return redirect("students:student_detail", ma_sv=enrollment.student.ma_sv)
    else:
        form = EnrollmentForm()

    return render(request, "students/enrollment_form.html", {"form": form})


@role_required(*STUDENT_ROLES)
def my_enrollments(request):
    student = get_user_student(request.user)
    if not student:
        messages.error(request, "Tai khoan sinh vien chua duoc lien ket ho so sinh vien.")
        return redirect("students:dashboard")

    keyword = request.GET.get("q", "").strip()
    available_classrooms = (
        Classroom.objects.filter(trang_thai=Classroom.Status.OPEN)
        .exclude(enrollments__student=student)
        .select_related("course", "giang_vien")
        .annotate(student_count=Count("enrollments", distinct=True))
        .order_by("-nam_hoc", "-hoc_ky", "ma_lop_hp")
    )
    if keyword:
        available_classrooms = available_classrooms.filter(
            Q(ma_lop_hp__icontains=keyword)
            | Q(course__ma_hp__icontains=keyword)
            | Q(course__ten_hp__icontains=keyword)
            | Q(giang_vien__username__icontains=keyword)
        )

    if request.method == "POST":
        form = StudentEnrollmentForm({"classroom": request.POST.get("classroom")}, student=student)
        if form.is_valid():
            enrollment = form.save()
            _log_action(
                request,
                "SINH_VIEN_DANG_KY_HOC_PHAN",
                f"Enrollment:{enrollment.id}",
                after={
                    "student": student.ma_sv,
                    "classroom": enrollment.classroom.ma_lop_hp if enrollment.classroom else "",
                    "course": enrollment.course.ma_hp,
                    "hoc_ky": enrollment.hoc_ky,
                    "nam_hoc": enrollment.nam_hoc,
                },
            )
            messages.success(request, "Dang ky hoc phan thanh cong.")
            return redirect("students:my_enrollments")
    else:
        form = StudentEnrollmentForm(student=student)

    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course", "classroom", "classroom__giang_vien")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
    )

    return render(
        request,
        "students/my_enrollments.html",
        {
            "student": student,
            "form": form,
            "available_classrooms": available_classrooms,
            "keyword": keyword,
            "enrollments": enrollments,
        },
    )


@role_required(*GRADE_ROLES)
def grade_input(request):
    next_url = _safe_next_url(request.POST.get("next") or request.GET.get("next"))

    if request.method == "POST":
        enrollment_id = request.POST.get("enrollment")
        lan_hoc = request.POST.get("lan_hoc")
        existing_grade = None
        if enrollment_id and lan_hoc:
            existing_grade = Grade.objects.filter(enrollment_id=enrollment_id, lan_hoc=lan_hoc).first()

        before = _grade_to_dict(existing_grade) if existing_grade else None
        form = GradeInputForm(request.POST, user=request.user, instance=existing_grade)
        if form.is_valid():
            grade = form.save()
            action = "CAP_NHAT_DIEM" if existing_grade else "NHAP_DIEM"

            result = recalculate_gpa_for_student(grade.enrollment.student)
            _log_action(
                request,
                action,
                f"Grade:{grade.id}",
                before=before,
                after={
                    **_grade_to_dict(grade),
                    "gpa_tich_luy": str(result["gpa"]),
                    "xep_loai": result["xep_loai"],
                },
            )

            messages.success(
                request,
                f"Luu diem thanh cong. GPA hien tai: {result['gpa']} ({result['xep_loai']}).",
            )

            role = get_user_role(request.user)
            if role == UserProfile.Role.GIANG_VIEN and grade.enrollment.classroom_id:
                return redirect("students:classroom_detail", class_id=grade.enrollment.classroom_id)

            if next_url:
                return redirect(next_url)
            return redirect("students:student_detail", ma_sv=grade.enrollment.student.ma_sv)
    else:
        initial = {}
        selected_student_id = request.GET.get("student")
        selected_enrollment_id = request.GET.get("enrollment")
        selected_attempt = request.GET.get("lan_hoc")

        if selected_student_id:
            initial["student"] = selected_student_id

        if selected_enrollment_id:
            enrollment = Enrollment.objects.select_related("student", "classroom").filter(id=selected_enrollment_id).first()
            if enrollment:
                initial["enrollment"] = enrollment.id
                initial["student"] = enrollment.student_id
                latest_grade = enrollment.grades.order_by("-lan_hoc", "-updated_at").first()
                if latest_grade:
                    initial.setdefault("diem_chuyen_can", latest_grade.diem_chuyen_can)
                    initial.setdefault("diem_qua_trinh", latest_grade.diem_qua_trinh)
                    initial.setdefault("diem_thi", latest_grade.diem_thi)
                    initial.setdefault("lan_hoc", latest_grade.lan_hoc)

        if selected_attempt:
            initial["lan_hoc"] = selected_attempt

        form = GradeInputForm(initial=initial or None, user=request.user)

    return render(request, "students/grade_form.html", {"form": form, "next_url": next_url})


@role_required(*STUDENT_ROLES)
def my_transcript_redirect(request):
    student = get_user_student(request.user)
    if not student:
        messages.error(request, "Tai khoan sinh vien chua duoc lien ket ho so sinh vien.")
        return redirect("students:dashboard")
    return redirect("students:transcript_report", ma_sv=student.ma_sv)


@role_required(*STUDENT_ACCESS_ROLES)
def transcript_report(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    role = get_user_role(request.user)

    if role == UserProfile.Role.SINH_VIEN:
        current_student = get_user_student(request.user)
        if not current_student or current_student.id != student.id:
            messages.error(request, "Ban chi duoc xem bang diem cua chinh minh.")
            return redirect("students:dashboard")

    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course", "classroom", "classroom__giang_vien")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
    )
    standing = AcademicStanding.objects.filter(student=student).first()

    return render(
        request,
        "students/transcript_report.html",
        {"student": student, "enrollments": enrollments, "standing": standing},
    )


@role_required(*STUDENT_ACCESS_ROLES)
def transcript_csv(request, ma_sv: str):
    student = get_object_or_404(Student, ma_sv=ma_sv)
    role = get_user_role(request.user)

    if role == UserProfile.Role.SINH_VIEN:
        current_student = get_user_student(request.user)
        if not current_student or current_student.id != student.id:
            messages.error(request, "Ban chi duoc xuat bang diem cua chinh minh.")
            return redirect("students:dashboard")

    enrollments = (
        Enrollment.objects.filter(student=student)
        .select_related("course", "classroom", "classroom__giang_vien")
        .prefetch_related("grades")
        .order_by("-nam_hoc", "-hoc_ky", "course__ma_hp")
    )

    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = f'attachment; filename="bang-diem-{student.ma_sv}.csv"'

    writer = csv.writer(response)
    writer.writerow(["Ma SV", "Ho ten", student.ma_sv, student.ho_ten])
    writer.writerow([])
    writer.writerow(
        [
            "Hoc ky",
            "Nam hoc",
            "Ma lop HP",
            "Ma HP",
            "Ten hoc phan",
            "Tin chi",
            "Diem chuyen can",
            "Diem QT",
            "Diem thi",
            "Diem TK (10)",
            "Diem he 4",
            "Diem chu",
            "Lan hoc",
        ]
    )

    for enrollment in enrollments:
        latest_grade = enrollment.grades.order_by("-lan_hoc", "-updated_at").first()
        writer.writerow(
            [
                enrollment.hoc_ky,
                enrollment.nam_hoc,
                enrollment.classroom.ma_lop_hp if enrollment.classroom else "",
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
