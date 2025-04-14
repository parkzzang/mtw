from django.shortcuts import redirect, render
from functools import wraps

def login_and_verified_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if not user.is_authenticated:
            return redirect('accounts:login')

        if user.verification_status == 'not_submitted':
            return redirect('accounts:verify')  # 인증 제출하러 감

        elif user.verification_status == 'pending':
            return render(request, 'accounts/verify_submitted.html')  # ✅ 안내 템플릿

        elif user.verification_status == 'rejected':
            return redirect('accounts:verify')  # 반려 → 재제출 유도

        # approved는 통과
        return view_func(request, *args, **kwargs)
    return _wrapped_view
