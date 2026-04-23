from .authz import get_user_role, get_user_student
from .models import UserProfile


def user_role_context(request):
    role = get_user_role(request.user)
    profile = getattr(request.user, "profile", None) if getattr(request, "user", None) else None
    student = get_user_student(request.user)
    role_label = profile.get_role_display() if profile else (role or "")

    return {
        "current_role": role,
        "current_role_label": role_label,
        "is_admin_role": role == UserProfile.Role.ADMIN,
        "is_student_role": role == UserProfile.Role.SINH_VIEN,
        "is_teacher_role": role == UserProfile.Role.GIANG_VIEN,
        "can_manage_students": role == UserProfile.Role.ADMIN,
        "can_manage_courses": role == UserProfile.Role.ADMIN,
        "can_manage_classes": role == UserProfile.Role.ADMIN,
        "can_register_courses": role in (UserProfile.Role.ADMIN, UserProfile.Role.SINH_VIEN),
        "can_view_my_classes": role in (UserProfile.Role.ADMIN, UserProfile.Role.GIANG_VIEN),
        "can_input_grade": role in (UserProfile.Role.ADMIN, UserProfile.Role.GIANG_VIEN),
        "can_take_attendance": role in (UserProfile.Role.ADMIN, UserProfile.Role.GIANG_VIEN),
        "current_student_ma": student.ma_sv if student else "",
    }
