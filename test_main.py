import pytest

from main import (
    get_db_connection,
    hash_password,
    is_email_valid,
    is_password_valid,
    simpan_user_ke_db,
    verify_password,
)


@pytest.mark.parametrize(
    "password, expected, deskripsi_sqa",
    [
        # --- POSITIVE TESTING ---
        (
            "ValidPass123",
            True,
            "Lulus: Memenuhi semua syarat (>=8, ada kapital, ada angka)",
        ),
        # --- NEGATIVE TESTING ---
        ("Pendek1", False, "Gagal: Hanya 7 karakter (Batas bawah Aturan 1)"),
        ("tanpakapital123", False, "Gagal: Tidak ada huruf besar (Aturan 2)"),
        ("TanpaAngkaSamaSekali", False, "Gagal: Tidak ada angka (Aturan 3)"),
        ("      1A", False, "Gagal: Kombinasi spasi dengan panjang kurang dari 8"),
        ("", False, "Gagal: Input kosong (Edge case ekstrim)"),
    ],
)
def test_password_rules(password, expected, deskripsi_sqa):
    result = is_password_valid(password)

    assert result == expected, f"Gagal pada skenario: {deskripsi_sqa}"


@pytest.mark.parametrize(
    "email, expected, deskripsi_sqa",
    [
        # --- POSITIVE TESTING ---
        ("mahasiswa@kampus.ac.id", True, "Lulus: Format email valid dengan TLD ac.id"),
        ("user.name@domain.com", True, "Lulus: Format email valid dengan nama titik"),
        # --- NEGATIVE TESTING ---
        ("usertanpadomain", False, "Gagal: Tidak memiliki karakter @ dan domain"),
        ("user@.com", False, "Gagal: Domain langsung diawali titik"),
        ("@domain.com", False, "Gagal: Karakter lokal di depan @ kosong"),
        ("user@domain", False, "Gagal: Tidak memiliki TLD (misal: .com, .id)"),
    ],
)
def test_email_rules(email, expected, deskripsi_sqa):
    result = is_email_valid(email)

    assert result == expected, f"Gagal pada skenario: {deskripsi_sqa}"


def test_password_hashing():
    plain_password = "ValidPass123"
    hashed = hash_password(plain_password)

    # 1. Hasil hash tidak sama dengan password asli
    assert (
        hashed != plain_password
    ), "Hash password tidak boleh sama dengan password asli"

    # 2. verify_password mengembalikan True untuk password asli yang benar
    assert (
        verify_password(plain_password, hashed) is True
    ), "Password asli harus cocok dengan hash-nya"

    # 3. verify_password mengembalikan False untuk password yang salah
    assert (
        verify_password("PasswordSalah123", hashed) is False
    ), "Password salah tidak boleh cocok dengan hash"


@pytest.fixture(scope="function")
def db_setup_teardown():
    """
    Fixture Pytest untuk Setup dan Teardown database integration testing.
    Setup: Memastikan koneksi dan membuat tabel users.
    Teardown: Menghapus tabel users setelah tes selesai.
    """
    connection = get_db_connection()
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
        cursor.execute("TRUNCATE TABLE users")

    yield connection

    # Teardown
    with connection.cursor() as cursor:
        cursor.execute("DROP TABLE IF EXISTS users")
    connection.close()


def test_simpan_user_ke_db(db_setup_teardown):
    connection = db_setup_teardown
    test_email = "testuser@domain.com"
    test_hash = hash_password("ValidPass123")

    # 1. Simpan user ke DB
    result = simpan_user_ke_db(test_email, test_hash)
    assert result is True, "Pengembalian fungsi simpan_user_ke_db harus True"

    # 2. Verifikasi dengan query SELECT
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (test_email,))
        row = cursor.fetchone()

    assert row is not None, "Data user harus ditemukan di database"
    assert row["email"] == test_email, f"Email di DB harus {test_email}"
    assert row["password"] == test_hash, "Hash password di DB harus sesuai"


from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_api_register_success(db_setup_teardown):
    connection = db_setup_teardown
    payload = {"email": "user.api@domain.com", "password": "ValidPass123"}

    # 1. Mengirim POST request ke /register
    response = client.post("/register", json=payload)

    # 2. Verifikasi HTTP Status Code 201 Created
    assert (
        response.status_code == 201
    ), f"Expected 201 Created, got {response.status_code}"
    assert response.json()["message"] == "User berhasil terdaftar"
    assert response.json()["email"] == payload["email"]

    # 3. Verifikasi data di database
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE email = %s", (payload["email"],))
        row = cursor.fetchone()

    assert row is not None, "Data user dari API harus tersimpan di database"
    assert row["email"] == payload["email"]


def test_api_register_invalid_email_format():
    payload = {"email": "usertanpadomain", "password": "ValidPass123"}

    # Mengirim payload dengan format email yang salah
    response = client.post("/register", json=payload)

    # Verifikasi HTTP Status Code 422 Unprocessable Entity
    assert (
        response.status_code == 422
    ), f"Expected 422 Unprocessable Entity, got {response.status_code}"


def test_api_register_duplicate_email(db_setup_teardown):
    payload = {"email": "duplicate@domain.com", "password": "ValidPass123"}

    # Pendaftaran pertama (harus 201)
    response1 = client.post("/register", json=payload)
    assert response1.status_code == 201

    # Pendaftaran kedua dengan email sama (harus 400 Bad Request)
    response2 = client.post("/register", json=payload)
    assert (
        response2.status_code == 400
    ), f"Expected 400 Bad Request, got {response2.status_code}"




