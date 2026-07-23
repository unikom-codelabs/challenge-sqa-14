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


import bcrypt


def hash_password(password: str) -> str:
    """
    Mengenkripsi kata sandi menggunakan algoritma bcrypt.
    """
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Memverifikasi kecocokan kata sandi asli dengan hash kata sandi.
    """
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


import os
import pymysql


def get_db_connection():
    """
    Membuat koneksi ke database MySQL menggunakan Environment Variables.
    """
    host = os.getenv("DB_HOST", "127.0.0.1")
    port = int(os.getenv("DB_PORT", "3306"))
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "root")
    database = os.getenv("DB_NAME", "test_db")

    return pymysql.connect(
        host=host,
        port=port,
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True,
    )


def simpan_user_ke_db(email: str, hashed_password: str) -> bool:
    """
    Menyimpan email dan hashed_password ke dalam database MySQL.
    """
    try:
        connection = get_db_connection()
        with connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    CREATE TABLE IF NOT EXISTS users (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        email VARCHAR(255) NOT NULL UNIQUE,
                        password VARCHAR(255) NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )
                sql = "INSERT INTO users (email, password) VALUES (%s, %s)"
                cursor.execute(sql, (email, hashed_password))
        return True
    except Exception as e:
        print(f"Error simpan_user_ke_db: {e}")
        return False



