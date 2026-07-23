"""SQA challenge: validation, password hashing, MySQL, and FastAPI."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
import re
import secrets
from typing import Any

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, field_validator

# Regex sederhana tetapi cukup ketat untuk acceptance criteria challenge.
EMAIL_PATTERN = re.compile(
    r"^(?=.{1,254}$)[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)


def is_password_valid(password: str) -> bool:
    """Valid jika panjang >= 8, memiliki huruf kapital, dan angka."""
    if not isinstance(password, str) or len(password.strip()) < 8:
        return False
    if not any(char.isupper() for char in password):
        return False
    if not any(char.isdigit() for char in password):
        return False
    return True


def is_email_valid(email: str) -> bool:
    """Memvalidasi email menggunakan regular expression."""
    if not isinstance(email, str):
        return False
    normalized_email = email.strip()
    if normalized_email != email:
        return False
    return EMAIL_PATTERN.fullmatch(normalized_email) is not None


# Challenge menyarankan passlib. Fallback PBKDF2 hanya dipakai bila passlib
# belum terpasang, sehingga modul tetap bisa diuji sebelum `uv sync --dev`.
try:
    from passlib.context import CryptContext
except ImportError:  # pragma: no cover - fallback khusus environment minimal
    CryptContext = None  # type: ignore[assignment]

_PASSWORD_CONTEXT = (
    CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
    if CryptContext is not None
    else None
)


def _fallback_hash_password(password: str) -> str:
    iterations = 600_000
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)
    return "pbkdf2_sha256${}${}${}".format(
        iterations,
        base64.urlsafe_b64encode(salt).decode(),
        base64.urlsafe_b64encode(digest).decode(),
    )


def _fallback_verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        algorithm, iteration_text, salt_text, digest_text = hashed_password.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.urlsafe_b64decode(salt_text.encode())
        expected = base64.urlsafe_b64decode(digest_text.encode())
        actual = hashlib.pbkdf2_hmac(
            "sha256", plain_password.encode(), salt, int(iteration_text)
        )
        return hmac.compare_digest(actual, expected)
    except (TypeError, ValueError):
        return False


def hash_password(password: str) -> str:
    """Menghasilkan hash satu arah untuk password."""
    if not isinstance(password, str) or not password:
        raise ValueError("Password tidak boleh kosong")
    if _PASSWORD_CONTEXT is not None:
        return _PASSWORD_CONTEXT.hash(password)
    return _fallback_hash_password(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Memverifikasi password plain text terhadap hash."""
    if not isinstance(plain_password, str) or not isinstance(hashed_password, str):
        return False
    if _PASSWORD_CONTEXT is not None:
        try:
            return _PASSWORD_CONTEXT.verify(plain_password, hashed_password)
        except (TypeError, ValueError):
            return False
    return _fallback_verify_password(plain_password, hashed_password)


CREATE_USERS_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS users (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(254) NOT NULL UNIQUE,
    hashed_password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
"""


def get_db_config() -> dict[str, Any]:
    """Mengambil konfigurasi MySQL dari environment variables."""
    return {
        "host": os.getenv("DB_HOST", "127.0.0.1"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "database": os.getenv("DB_NAME", "test_db"),
        "charset": "utf8mb4",
        "autocommit": False,
    }


def get_db_connection():
    """Membuat koneksi baru ke MySQL."""
    try:
        import pymysql
    except ImportError as exc:  # pragma: no cover - dependency setup error
        raise RuntimeError("pymysql belum terpasang. Jalankan `uv sync --dev`.") from exc
    return pymysql.connect(**get_db_config())


def create_users_table() -> None:
    """Membuat tabel users bila belum tersedia."""
    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE_SQL)
        connection.commit()
    finally:
        connection.close()


def simpan_user_ke_db(email: str, hashed_password: str) -> bool:
    """Menyimpan user. Mengembalikan False bila email sudah terdaftar."""
    if not is_email_valid(email):
        raise ValueError("Format email tidak valid")
    if not isinstance(hashed_password, str) or not hashed_password:
        raise ValueError("Hash password tidak valid")

    try:
        import pymysql
    except ImportError as exc:  # pragma: no cover - dependency setup error
        raise RuntimeError("pymysql belum terpasang. Jalankan `uv sync --dev`.") from exc

    connection = get_db_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(CREATE_USERS_TABLE_SQL)
            cursor.execute(
                "INSERT INTO users (email, hashed_password) VALUES (%s, %s)",
                (email, hashed_password),
            )
        connection.commit()
        return True
    except pymysql.err.IntegrityError:
        connection.rollback()
        return False
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


class RegisterRequest(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not is_email_valid(value):
            raise ValueError("Format email tidak valid")
        return value

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if not is_password_valid(value):
            raise ValueError(
                "Password minimal 8 karakter dan harus memiliki huruf kapital serta angka"
            )
        return value


class RegisterResponse(BaseModel):
    message: str
    email: str


app = FastAPI(title="SQA Registration API", version="1.0.0")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: RegisterRequest) -> RegisterResponse:
    hashed_password = hash_password(payload.password)
    try:
        saved = simpan_user_ke_db(payload.email, hashed_password)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database tidak tersedia",
        ) from exc

    if not saved:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email sudah terdaftar",
        )

    return RegisterResponse(
        message="User berhasil didaftarkan",
        email=payload.email,
    )
