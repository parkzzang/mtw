# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm, VerificationForm
from django.http import JsonResponse
from .models import PhoneVerification
from .utils import send_verification_code
from django.utils import timezone
from datetime import timedelta
from django.core.validators import RegexValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required

from django.contrib.auth import get_user_model

from django.views.decorators.csrf import csrf_exempt

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
    if request.user.is_verified:
        return redirect('main:index')  # ✅ 자기 자신으로 리다이렉트 X

    if request.method == 'POST':
        form = VerificationForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return render(request, 'accounts/verify_submitted.html')  # 완료 메시지
        else:
            print("❌ 폼 오류 발생:", form.errors)  # ✅ 서버 콘솔에 출력
    else:
        form = VerificationForm(instance=request.user)

    return render(request, 'accounts/verify.html', {'form': form})


def verified_required(view_func):
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('accounts:login')
        if not request.user.is_verified:
            return redirect('accounts:verify')
        return view_func(request, *args, **kwargs)
    return _wrapped
