from .authz import get_user_role
from .models import UserProfile


def user_role_context(request):
    role = get_user_role(request.user)
    return {
        "current_role": role,
        "can_manage_students": role in (UserProfile.Role.ADMIN, UserProfile.Role.DAO_TAO),
        "can_input_grade": role in (UserProfile.Role.ADMIN, UserProfile.Role.DAO_TAO, UserProfile.Role.GIANG_VIEN),
        "can_view_reports": role
        in (
            UserProfile.Role.ADMIN,
            UserProfile.Role.DAO_TAO,
            UserProfile.Role.GIANG_VIEN,
            UserProfile.Role.CO_VAN,
        ),
    }
