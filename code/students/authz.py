from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse

from .models import UserProfile


def get_user_role(user) -> str | None:
    if not user or not user.is_authenticated:
        return None
    if user.is_superuser:
        return UserProfile.Role.ADMIN

    profile = getattr(user, "profile", None)
    if profile is None:
        profile = UserProfile.objects.create(user=user, role=UserProfile.Role.DAO_TAO)

    if profile.status != UserProfile.Status.ACTIVE:
        return None
    return profile.role


def role_required(*allowed_roles: str):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect(f"{reverse('login')}?next={request.path}")

            role = get_user_role(request.user)
            if role is None:
                messages.error(request, "Tài khoản của bạn đã bị khóa hoặc chưa kích hoạt.")
                return redirect("login")

            if allowed_roles and role not in allowed_roles:
                messages.error(request, "Bạn không có quyền truy cập chức năng này.")
                return redirect("students:dashboard")
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator
