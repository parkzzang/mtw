# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PhoneVerification, LicenseVerification
from django.contrib.auth import get_user_model

class SignupForm(UserCreationForm):
    username = forms.CharField()
    phone_number = forms.CharField()
    verification_code = forms.CharField()
    agree_terms = forms.BooleanField(label="이용약관 동의", required=True)
    agree_privacy = forms.BooleanField(label="개인정보처리방침 동의", required=True)

    class Meta:
        model = User
        fields = ("username", "phone_number", "verification_code", "password1", "password2")


    def clean(self):
        cleaned_data = super().clean()
        phone = cleaned_data.get("phone_number")
        code = cleaned_data.get("verification_code")

        if phone and code:
            try:
                pv = PhoneVerification.objects.filter(phone_number=phone, code=code).latest("created_at")
                if pv.is_expired():
                    raise forms.ValidationError("인증번호가 만료되었습니다.")
            except PhoneVerification.DoesNotExist:
                raise forms.ValidationError("인증번호가 일치하지 않습니다.")
        return cleaned_data


class VerificationForm(forms.ModelForm):
    class Meta:
        model = LicenseVerification
        fields = ['document']  # ✅ 실제 존재하는 필드만 사용
        labels = {
            'document': '면허증 또는 자격증 파일 업로드',
        }


class LoginForm(forms.Form):
    username = forms.CharField(label="아이디", max_length=150)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)