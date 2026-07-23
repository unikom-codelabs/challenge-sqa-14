import pytest

from main import (
    get_db_connection,
    hash_password,
    is_email_valid,
    is_password_valid,
    simpan_user_ke_db,
    verify_password,
)


@pytest.fixture(autouse=True)
def setup_mysql_db(request):
    """
    Fixture untuk Setup (membuat tabel users) dan Teardown (menghapus tabel users setelah tes).
    """
    db_conn = None
    try:
        db_conn = get_db_connection(connect_timeout=1)
        with db_conn:
            with db_conn.cursor() as cursor:
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
    except Exception as e:
        if "simpan_user" in request.node.name or "register" in request.node.name:
            pytest.skip(f"MySQL database tidak tersedia: {e}")

    yield

    if db_conn:
        try:
            conn = get_db_connection(connect_timeout=1)
            with conn:
                with conn.cursor() as cursor:
                    cursor.execute("DROP TABLE IF EXISTS users")
        except Exception:
            pass



@pytest.mark.parametrize(
    "email, expected, deskripsi_sqa",
    [
        # --- POSITIVE CASE ---
        ("mahasiswa@kampus.ac.id", True, "Lulus: Email kampus dengan sub-domain valid"),
        ("user.name@domain.com", True, "Lulus: Email standar dengan titik di local part"),
        # --- NEGATIVE CASE ---
        ("usertanpadomain", False, "Gagal: Tanpa karakter @ dan domain"),
        ("user@.com", False, "Gagal: Domain diawali dengan titik"),
        ("@domain.com", False, "Gagal: Local part kosong"),
        ("user@domain", False, "Gagal: Domain tanpa top level domain (TLD)"),
    ],
)
def test_email_validation(email, expected, deskripsi_sqa):
    result = is_email_valid(email)
    assert result == expected, f"Gagal pada skenario: {deskripsi_sqa}"


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


def test_password_hashing():
    raw_password = "ValidPass123"
    hashed = hash_password(raw_password)

    # Acceptance Criteria 1: Hasil hash tidak boleh sama dengan password asli
    assert hashed != raw_password, "Hash password tidak boleh sama dengan plain text"
    assert len(hashed) > 0, "Hash password tidak boleh kosong"


def test_password_verification():
    raw_password = "ValidPass123"
    wrong_password = "WrongPassword123"
    hashed = hash_password(raw_password)

    # Acceptance Criteria 2: verify_password True untuk password asli & hash-nya
    assert verify_password(raw_password, hashed) is True, "verifikasi password asli harus True"

    # Acceptance Criteria 3: verify_password False untuk password yang salah
    assert verify_password(wrong_password, hashed) is False, "verifikasi password salah harus False"


def test_simpan_user_ke_db():
    email = "user.test@kampus.ac.id"
    raw_pass = "ValidPass123"
    hashed = hash_password(raw_pass)

    success = simpan_user_ke_db(email, hashed)
    assert success is True, "Penyimpanan data ke MySQL harus mengembalikan True"

    # Verifikasi dengan SELECT dari database
    conn = get_db_connection()
    with conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            result = cursor.fetchone()

    assert result is not None, "Data user harus ditemukan di database"
    assert result["email"] == email, "Email tersimpan harus sesuai"
    assert result["password"] == hashed, "Password hash tersimpan harus sesuai"



