# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, PhoneVerification

class SignupForm(UserCreationForm):
    phone_number = forms.CharField(label="전화번호")
    role = forms.ChoiceField(label="직군", choices=User.ROLE_CHOICES)
    verification_code = forms.CharField(label="인증번호")  # ✅ 추가

    class Meta:
        model = User
        fields = ("username", "phone_number", "role", "verification_code", "password1", "password2")

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
