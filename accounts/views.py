# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from accounts.decorators import login_and_verified_required
from django.contrib.auth import get_user_model
from django.views.decorators.csrf import csrf_exempt

from .forms import SignupForm, VerificationForm, LoginForm, ProfileForm
from .models import PhoneVerification, LicenseVerification, Profile
from .utils import send_verification_code

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # ✅ 저장 미루기
            user.is_phone_verified = True   # ✅ 인증 통과 표시
            user.save()
            login(request, user)
            return redirect("accounts:verify")
        else: print("❌ 폼 유효성 검사 실패:", form.errors)
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

@csrf_exempt
def check_username_view(request):
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        if not username:
            return JsonResponse({"available": False, "message": "아이디를 입력해주세요."}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({"available": False, "message": "이미 사용 중인 아이디입니다."})
        return JsonResponse({"available": True, "message": "사용 가능한 아이디입니다!"})

    return JsonResponse({"error": "POST 요청이 필요합니다."}, status=400)

phone_validator = RegexValidator(
    regex=r'^01([0|1|6|7|8|9]?)-?([0-9]{3,4})-?([0-9]{4})$',
    message='유효한 전화번호 형식이 아닙니다.'
)
User = get_user_model()

@csrf_exempt
def send_code_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number")

        # ✅ 전화번호 형식 검증
        try:
            phone_validator(phone)
        except ValidationError as e:
            return JsonResponse({"error": str(e)}, status=400)

        # ✅ 전화번호 중복 체크 (이미 가입된 번호인지)
        if User.objects.filter(phone_number=phone).exists():
            return JsonResponse({"error": "이미 가입된 전화번호입니다."}, status=409)  # 409 Conflict

        # ✅ 인증코드 전송 및 저장
        code = send_verification_code(phone)
        PhoneVerification.objects.create(phone_number=phone, code=code)
        return JsonResponse({"message": "인증번호가 전송되었습니다."})

    return JsonResponse({"error": "POST 요청이 필요합니다."}, status=400)


@csrf_exempt
def verify_code_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number", "").strip()
        code = request.POST.get("code", "").strip()

        print(f"🔍 [검증 요청] phone={phone}, code={code}")

        try:
            verification = (
                PhoneVerification.objects
                .filter(phone_number=phone, code=code)
                .order_by('-created_at')
                .first()
            )

            if verification is None:
                print("❌ 인증 정보 없음 (번호 또는 코드 틀림)")
                return JsonResponse({
                    "result": False,
                    "error": "인증번호가 일치하지 않습니다."
                }, status=400)

            # 만료 체크
            if timezone.now() > verification.created_at + timedelta(minutes=1):
                print("⏰ 인증번호 만료")
                return JsonResponse({
                    "result": False,
                    "error": "인증번호가 만료되었습니다."
                }, status=400)

            print("✅ 인증 성공")
            return JsonResponse({"result": True})

        except Exception as e:
            print(f"🚨 예외 발생: {e}")
            return JsonResponse({
                "result": False,
                "error": "서버 오류가 발생했습니다."
            }, status=500)

    return JsonResponse({"error": "POST 요청 필요"}, status=400)

@login_required
def verify_view(request):
    user = request.user

    # 상태별 분기
    if user.verification_status == 'pending':
        submitted_at = None
        try:
            submitted_at = user.license.submitted_at
        except LicenseVerification.DoesNotExist:
            pass

        return render(request, 'accounts/verify_submitted.html', {
            'submitted_at': submitted_at
        })


    elif user.verification_status == 'approved':
        return redirect('main:index')  # 또는 마이페이지

    elif user.verification_status == 'rejected':
        return render(request, 'accounts/verify_rejected.html')  # ✅ 반려 안내 페이지

    # 미제출인 경우 (not_submitted)
    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save(user)
            return render(request, 'accounts/verify_submitted.html', {
                'submitted_at': user.license.submitted_at
            })
    else:
        form = VerificationForm()

    return render(request, 'accounts/verify.html', {'form': form})


def verified_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_verified:
            return redirect('accounts:verify')
        return view_func(request, *args, **kwargs)
    return _wrapped

def login_view(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                request,
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            if user is not None:
                login(request, user)
                return redirect("main:index")  # 로그인 후 메인페이지로 이동
            else:
                messages.error(request, "아이디 또는 비밀번호가 올바르지 않습니다.")
    else:
        form = LoginForm()

    return render(request, "accounts/login.html", {"form": form})

@login_and_verified_required
def dashboard_view(request):
    return render(request, "main/dashboard.html")

def logout_view(request):
    logout(request)
    return redirect("main:landing")

@login_required
def mypage_view(request):
    user = request.user

    if user.verification_status == 'pending':
        return render(request, "accounts/verify_submitted.html")

    return render(request, "accounts/mypage.html", {"user": user})

@login_required
def reset_verification(request):
    user = request.user
    user.verification_status = 'not_submitted'
    user.save()
    return redirect('accounts:verify')

@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('main:index')  # 저장 후 홈으로 이동
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'accounts/edit_profile.html', {'form': form})