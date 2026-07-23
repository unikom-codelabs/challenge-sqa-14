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



