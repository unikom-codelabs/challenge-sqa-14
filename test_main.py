from __future__ import annotations

import os
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

import main
from main import (
    app,
    hash_password,
    is_email_valid,
    is_password_valid,
    simpan_user_ke_db,
    verify_password,
)

client = TestClient(app)


@pytest.mark.parametrize(
    "password, expected",
    [
        ("ValidPass123", True),
        ("Pendek1", False),
        ("tanpakapital123", False),
        ("TanpaAngkaSamaSekali", False),
        (" 1A", False),
        ("", False),
    ],
)
def test_password_rules(password: str, expected: bool) -> None:
    assert is_password_valid(password) is expected


@pytest.mark.parametrize(
    "email",
    ["mahasiswa@kampus.ac.id", "user.name@domain.com"],
)
def test_email_positive_cases(email: str) -> None:
    assert is_email_valid(email) is True


@pytest.mark.parametrize(
    "email",
    ["usertanpadomain", "user@.com", "@domain.com", "user@domain"],
)
def test_email_negative_cases(email: str) -> None:
    assert is_email_valid(email) is False


def test_hash_password_is_not_plain_text() -> None:
    password = "Rahasia123"
    assert hash_password(password) != password


def test_verify_password_returns_true_for_matching_password() -> None:
    password = "Rahasia123"
    hashed = hash_password(password)
    assert verify_password(password, hashed) is True


def test_verify_password_returns_false_for_wrong_password() -> None:
    hashed = hash_password("Rahasia123")
    assert verify_password("PasswordSalah123", hashed) is False


def test_register_api_success_without_database(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, str] = {}

    def fake_save(email: str, hashed_password: str) -> bool:
        captured["email"] = email
        captured["hashed_password"] = hashed_password
        return True

    monkeypatch.setattr(main, "simpan_user_ke_db", fake_save)

    response = client.post(
        "/register",
        json={"email": "api.user@domain.com", "password": "Password123"},
    )

    assert response.status_code == 201
    assert response.json()["email"] == "api.user@domain.com"
    assert captured["email"] == "api.user@domain.com"
    assert captured["hashed_password"] != "Password123"


def test_register_api_duplicate_returns_400(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(main, "simpan_user_ke_db", lambda _email, _hash: False)

    response = client.post(
        "/register",
        json={"email": "duplicate@domain.com", "password": "Password123"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Email sudah terdaftar"


def test_register_api_invalid_email_returns_422() -> None:
    response = client.post(
        "/register",
        json={"email": "email-salah", "password": "Password123"},
    )
    assert response.status_code == 422


@pytest.fixture(scope="module")
def mysql_connection():
    """Setup/teardown integration test MySQL.

    Lokal tanpa MySQL akan skip. Di GitHub Actions, service MySQL membuat tes ini jalan.
    """
    try:
        import pymysql
    except ImportError:
        pytest.skip("pymysql belum terpasang")

    try:
        connection = pymysql.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", "root"),
            database=os.getenv("DB_NAME", "test_db"),
            charset="utf8mb4",
            autocommit=True,
        )
    except Exception as exc:
        pytest.skip(f"MySQL tidak tersedia: {exc}")

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS users")
        cursor.execute(
            """
            CREATE TABLE users (
                id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
                email VARCHAR(254) NOT NULL UNIQUE,
                hashed_password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """
        )
    connection.commit()

    yield connection

    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS users")
    connection.commit()
    connection.close()


def test_simpan_user_ke_mysql(mysql_connection) -> None:
    email = f"db-{uuid4().hex}@domain.com"
    hashed = hash_password("Password123")

    assert simpan_user_ke_db(email, hashed) is True

    mysql_connection.ping()
    with mysql_connection.cursor() as cursor:
        cursor.execute(
            "SELECT email, hashed_password FROM users WHERE email = %s", (email,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row[0] == email
    assert row[1] == hashed


def test_register_api_success_and_persists_to_mysql(mysql_connection) -> None:
    email = f"api-db-{uuid4().hex}@domain.com"

    response = client.post(
        "/register",
        json={"email": email, "password": "Password123"},
    )

    assert response.status_code == 201

    mysql_connection.ping()
    with mysql_connection.cursor() as cursor:
        cursor.execute(
            "SELECT email, hashed_password FROM users WHERE email = %s", (email,)
        )
        row = cursor.fetchone()

    assert row is not None
    assert row[0] == email
    assert row[1] != "Password123"
    assert verify_password("Password123", row[1]) is True
