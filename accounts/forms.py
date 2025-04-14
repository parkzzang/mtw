# accounts/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from datetime import datetime

from .models import User, PhoneVerification, LicenseVerification, Profile

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


class VerificationForm(forms.Form):
    document = forms.FileField(label="면허증 또는 자격증 업로드")

    def save(self, user):
        from .models import LicenseVerification

        # 기존 인증기록이 있으면 갱신
        obj, _ = LicenseVerification.objects.get_or_create(user=user)
        obj.document = self.cleaned_data['document']
        obj.save()

        user.verification_status = 'pending'
        user.save()


class LoginForm(forms.Form):
    username = forms.CharField(label="아이디", max_length=150)
    password = forms.CharField(label="비밀번호", widget=forms.PasswordInput)



class ProfileForm(forms.ModelForm):
    BIRTH_YEAR_CHOICES = [(y, str(y)) for y in range(2006, 1974, -1)]
    birth_year = forms.ChoiceField(choices=BIRTH_YEAR_CHOICES, label="출생 연도")

    class Meta:
        model = Profile
        fields = [
            'photo', 'birth_year', 'region',
            'bio', 'height', 'weight',
            'is_smoker', 'religion',
            'interests', 'mbti', 'ideal_type',
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3}),
            'ideal_type': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        required_fields = ['photo', 'birth_year', 'region']
        for field in required_fields:
            self.fields[field].required = True

        for field in self.fields:
            widget = self.fields[field].widget
            if not isinstance(widget, forms.Textarea):
                widget.attrs.update({'class': 'form-control'})