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


import re


def is_email_valid(email: str) -> bool:
    """
    Memvalidasi format email berdasarkan kriteria SQA:
    - Memiliki karakter @ dan domain yang valid
    """
    if not isinstance(email, str) or not email.strip():
        return False

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9-]+(\.[a-zA-Z0-9-]+)*\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email.strip()))

