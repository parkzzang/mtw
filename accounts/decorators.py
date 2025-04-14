# accounts/decorators.py
# 반복되는 접근 제어 로직을 @login_and_verified_required로 정리

from django.shortcuts import redirect, render
from functools import wraps

def login_and_verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('accounts:login')

        if user.verification_status == 'not_submitted':
            return redirect('accounts:verify')  # 인증 제출 폼

        elif user.verification_status == 'pending':
            return redirect('accounts:verify')  # ✅ 이걸로 URL까지 이동

        elif user.verification_status == 'rejected':
            return redirect('accounts:verify')  # 또는 별도 rejected URL

        return view_func(request, *args, **kwargs)
    return _wrapped_view

def profile_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user

        if not user.is_authenticated:
            return redirect('accounts:login')

        if user.verification_status != 'approved':
            return redirect('accounts:verify')  # 인증 미완료 유저는 인증부터

        # 프로필이 없거나 필수 항목(사진, 나이, 지역)이 빠졌다면 edit_profile로
        profile = getattr(user, 'profile', None)
        if not profile or not profile.photo or not profile.age or not profile.region:
            return redirect('accounts:edit_profile')

        return view_func(request, *args, **kwargs)
    return _wrapped_view