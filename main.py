import os
import re
from passlib.context import CryptContext
import pymysql
import pymysql.cursors

pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


def get_db_connection(connect_timeout: int = 2):
    """
    Membuat koneksi ke MySQL menggunakan Environment Variables.
    """
    return pymysql.connect(
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", "root"),
        database=os.getenv("DB_NAME", "test_db"),
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
        connect_timeout=connect_timeout,
    )



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


def simpan_user_ke_db(email: str, hashed_password: str) -> bool:
    """
    Menyimpan data user (email dan hashed_password) ke dalam database MySQL.
    Mengembalikan True jika berhasil, False jika gagal.
    """
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
                cursor.execute(sql, (email, hashed_password))
        return True
    except Exception as e:
        print(f"Error simpan_user_ke_db: {e}")
        return False



