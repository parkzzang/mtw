from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from datetime import datetime


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
    username = models.CharField(max_length=30, unique=True)
    phone_number = models.CharField(max_length=20, unique=True)
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

    verification_status = models.CharField(
        max_length=20,
        choices=[
            ('not_submitted', '미제출'),
            ('pending', '대기 중'),
            ('approved', '승인 완료'),
            ('rejected', '반려'),
        ],
        default='not_submitted',
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['phone_number', 'role']

    objects = UserManager()

    def __str__(self):
        return self.username

    @property
    def is_verified(self):
        return self.verification_status == 'approved'

class LicenseVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='license')
    document = models.FileField(upload_to="licenses/")
    submitted_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username} - 제출됨"

class PhoneVerification(models.Model):
    phone_number = models.CharField(max_length=20)
    code = models.CharField(max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=5)

class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    # 필수 정보
    photo = models.ImageField(upload_to='profile_photos/', null=True, blank=True)
    birth_year = models.PositiveIntegerField(null=True, blank=True)
    region = models.CharField(max_length=50, null=True, blank=True)

    # 선택 정보
    bio = models.TextField(blank=True)
    height = models.PositiveIntegerField(null=True, blank=True, help_text="cm")
    weight = models.PositiveIntegerField(null=True, blank=True, help_text="kg")
    is_smoker = models.BooleanField(null=True, blank=True)
    religion = models.CharField(max_length=20, blank=True)
    interests = models.CharField(max_length=100, blank=True)

    MBTI_CHOICES = [
        ('INTJ', 'INTJ'), ('INTP', 'INTP'), ('ENTJ', 'ENTJ'), ('ENTP', 'ENTP'),
        ('INFJ', 'INFJ'), ('INFP', 'INFP'), ('ENFJ', 'ENFJ'), ('ENFP', 'ENFP'),
        ('ISTJ', 'ISTJ'), ('ISFJ', 'ISFJ'), ('ESTJ', 'ESTJ'), ('ESFJ', 'ESFJ'),
        ('ISTP', 'ISTP'), ('ISFP', 'ISFP'), ('ESTP', 'ESTP'), ('ESFP', 'ESFP'),
        ('CHANGE', '자주 바뀜'), ('UNKNOWN', '알 수 없음'),
    ]
    mbti = models.CharField(max_length=10, choices=MBTI_CHOICES, blank=True)

    ideal_type = models.TextField(blank=True, verbose_name="원하는 매칭 조건")

    def __str__(self):
        return f"{self.user.username}의 프로필"

    @property
    def age(self):
        if self.birth_year:
            return datetime.now().year - self.birth_year + 1  # 한국식 나이 기준
        return None