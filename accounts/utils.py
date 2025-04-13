# accounts/utils.py (또는 별도 sms.py)
import random

def generate_verification_code():
    return str(random.randint(100000, 999999))

def send_verification_code(phone_number):
    code = generate_verification_code()
    # 실제 문자 전송 API 호출 부분 필요 (ex. 쿨SMS, 카카오 알림톡, 솔루션톡)
    print(f"[디버그용] 인증번호 전송 → {phone_number} : {code}")
    return code
