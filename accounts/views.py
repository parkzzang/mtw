# accounts/views.py
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import SignupForm
from django.http import JsonResponse
from .models import PhoneVerification
from .utils import send_verification_code

from django.views.decorators.csrf import csrf_exempt

def signup_view(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # ✅ 저장 미루기
            user.is_phone_verified = True   # ✅ 인증 통과 표시
            user.save()
            login(request, user)
            return redirect("main:index")
    else:
        form = SignupForm()
    return render(request, "accounts/signup.html", {"form": form})

@csrf_exempt
def send_code_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number")
        code = send_verification_code(phone)

        PhoneVerification.objects.create(phone_number=phone, code=code)
        return JsonResponse({"message": "인증번호가 전송되었습니다."})
    return JsonResponse({"error": "POST 요청이 필요합니다."}, status=400)

@csrf_exempt
def verify_code_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number")
        code = request.POST.get("code")
        try:
            pv = PhoneVerification.objects.filter(phone_number=phone, code=code).latest("created_at")
            if pv.is_expired():
                return JsonResponse({"error": "인증번호가 만료되었습니다."}, status=400)
            return JsonResponse({"success": True})
        except PhoneVerification.DoesNotExist:
            return JsonResponse({"error": "인증번호가 일치하지 않습니다."}, status=400)
