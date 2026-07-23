import re
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def is_email_valid(email: str) -> bool:
    """
    Memvalidasi format email menggunakan Regular Expression.
    Format harus memiliki karakter local part, '@', domain, dan TLD valid.
    """
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_password_valid(password: str) -> bool:
    """
    Memvalidasi kata sandi berdasarkan 3 aturan dasar SQA:
    1. Minimal 8 karakter
    2. Mengandung minimal 1 huruf kapital
    3. Mengandung minimal 1 angka
    """
    if len(password.strip()) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True


def hash_password(password: str) -> str:
    """
    Mengenkripsi/hashing kata sandi menggunakan passlib.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi kata sandi plain text dengan hash kata sandi.
    """
    return pwd_context.verify(plain_password, hashed_password)


