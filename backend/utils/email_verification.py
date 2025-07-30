import random
from backend.utils.email import send_email  

def generate_verification_code(length: int = 6) -> str:
    return ''.join(str(random.randint(0, 9)) for _ in range(length))

def send_verification_code(email: str, code: str):
    subject = "Подтверждение email"
    body = f"Ваш код подтверждения: {code}"
    send_email(to_email=email, subject=subject, body=body)