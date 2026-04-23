from django.urls import path

from . import views

app_name = "students"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("students/", views.student_list, name="student_list"),
    path("students/create/", views.student_create, name="student_create"),
    path("students/<str:ma_sv>/", views.student_detail, name="student_detail"),
    path("students/<str:ma_sv>/edit/", views.student_update, name="student_update"),
    path("students/<str:ma_sv>/delete/", views.student_delete, name="student_delete"),

    path("courses/create/", views.course_create, name="course_create"),

    path("classes/", views.classroom_list, name="classroom_list"),
    path("classes/create/", views.classroom_create, name="classroom_create"),
    path("classes/my/", views.my_classes, name="my_classes"),
    path("classes/<int:class_id>/", views.classroom_detail, name="classroom_detail"),
    path("classes/<int:class_id>/attendance/", views.attendance_take, name="attendance_take"),

    path("enrollments/create/", views.enrollment_create, name="enrollment_create"),
    path("my/enrollments/", views.my_enrollments, name="my_enrollments"),

    path("grades/input/", views.grade_input, name="grade_input"),

    path("reports/my-transcript/", views.my_transcript_redirect, name="my_transcript"),
    path("reports/transcript/<str:ma_sv>/", views.transcript_report, name="transcript_report"),
    path("reports/transcript/<str:ma_sv>/csv/", views.transcript_csv, name="transcript_csv"),
]
