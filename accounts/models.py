from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta

# Create your models here.
class UserManager(BaseUserManager):
    def create_user(self, username, phone_number, password=None, **extra_fields):
        if not username:
            raise ValueError("아이디는 필수입니다.")
        if not phone_number:
            raise ValueError("전화번호는 필수입니다.")
        user = self.model(username=username, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(username, phone_number, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=30, unique=True)  # 로그인 ID
    phone_number = models.CharField(max_length=20, unique=True)  # 문자 인증용
    is_phone_verified = models.BooleanField(default=False)

    ROLE_CHOICES = [
        ("의사", "의사"), ("의대생", "의대생"),
        ("치과의사", "치과의사"), ("치대생", "치대생"),
        ("한의사", "한의사"), ("한의대생", "한의대생"),
        ("약사", "약사"), ("약대생", "약대생"),
        ("수의사", "수의사"), ("수의대생", "수의대생"),
        ("용병", "용병"),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    is_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'  # ✅ 로그인할 때 사용되는 ID
    REQUIRED_FIELDS = ['phone_number', 'role']

    objects = UserManager()

    def __str__(self):
        return self.username
    
class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

    def __str__(self):
        return f"{self.phone_number} - {self.code}"
    
class LicenseVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    document = models.FileField(upload_to="licenses/")
    status = models.CharField(choices=[('대기', '대기'), ('승인', '승인'), ('거절', '거절')], default='대기')
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)