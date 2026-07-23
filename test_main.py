import pytest

from main import is_email_valid, is_password_valid


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

