from django.contrib import admin

from .models import (
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


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("ma_sv", "ho_ten", "email", "khoa", "nganh", "lop", "trang_thai")
    search_fields = ("ma_sv", "ho_ten", "email")
    list_filter = ("khoa", "nganh", "lop", "trang_thai")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("ma_hp", "ten_hp", "so_tin_chi")
    search_fields = ("ma_hp", "ten_hp")


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ("student", "course", "hoc_ky", "nam_hoc", "trang_thai")
    search_fields = ("student__ma_sv", "student__ho_ten", "course__ma_hp", "course__ten_hp")
    list_filter = ("hoc_ky", "nam_hoc", "trang_thai")


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        "enrollment",
        "diem_chuyen_can",
        "diem_qua_trinh",
        "diem_thi",
        "diem_tong_ket_10",
        "diem_he_4",
        "diem_chu",
        "lan_hoc",
        "updated_at",
    )
    list_filter = ("diem_chu", "lan_hoc")


admin.site.register(GPASemester)
admin.site.register(AcademicStanding)
admin.site.register(ClassificationRule)
admin.site.register(AuditLog)
admin.site.register(UserProfile)
