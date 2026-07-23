import pytest

from main import is_email_valid, is_password_valid


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

