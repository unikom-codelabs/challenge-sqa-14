# Demo SQA: CI/CD Pipeline dengan Python dan uv

Project ini merangkum skenario demonstrasi **Continuous Integration (CI)** untuk kelas **Software Quality Assurance (SQA)**. Demo ini dirancang untuk menunjukkan transisi dari pengujian unit dasar hingga pengujian API menggunakan ekosistem Python modern.

---

## 🎯 Tujuan Pembelajaran

- **Memahami CI/CD Dasar**: Mengotomatiskan pengujian perangkat lunak menggunakan GitHub Actions setiap kali ada Pull Request.
- **Pengenalan uv**: Menggunakan uv (oleh Astral) sebagai package manager Python berkinerja tinggi untuk memangkas waktu setup environment di CI.
- **Penerapan Konsep SQA**:
  - Positive & Negative Testing
  - Data-Driven Testing (menggunakan `@pytest.mark.parametrize`)
  - Environment Parity (kesamaan lingkungan lokal dan CI menggunakan Docker)
  - Integration Testing & API Testing

---

## 🛠️ Tech Stack

- **Bahasa**: Python 3.12+
- **Package Manager**: uv
- **Testing Framework**: pytest, pytest-cov, httpx (untuk API test)
- **Web Framework**: FastAPI & Pydantic
- **Database**: MySQL (dengan pymysql)
- **Infrastruktur**: GitHub Actions & Docker Compose

---

## 📋 Prasyarat

Sebelum meng-_clone_ dan menjalankan project ini, pastikan perangkat Anda sudah memiliki:

- **Git** — untuk meng-_clone_ repository. [Download Git](https://git-scm.com/downloads)
- **Python 3.12+** — bahasa utama yang digunakan project ini. [Download Python](https://www.python.org/downloads/)
- **uv** — package manager Python yang dipakai untuk mengelola dependensi & virtual environment.
  ```bash
  # macOS / Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows (PowerShell)
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```
- **Docker & Docker Compose** — untuk menjalankan database MySQL secara lokal (dibutuhkan mulai Issue #3). [Download Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Editor/IDE** — disarankan menggunakan [Antigravity IDE](https://antigravity.google/) untuk pengembangan project ini.

Verifikasi instalasi dengan menjalankan:

```bash
git --version
python --version
uv --version
docker --version
docker compose version
```

---

## 📥 Langkah-Langkah Clone & Setup Project

1. **Clone repository**

   ```bash
   git clone https://github.com/unikom-codelabs/challenge-sqa-14.git
   cd challenge-sqa-14
   ```

2. **Pastikan versi Python sesuai**

   Project ini menggunakan file `.python-version` (Python 3.12). Jika menggunakan `uv`, versi Python yang sesuai akan otomatis diunduh/dipakai saat sinkronisasi dependensi.

3. **Buat dan aktifkan virtual environment**

   ```bash
   uv venv
   ```

   Aktifkan virtual environment yang baru dibuat:

   ```bash
   # macOS / Linux
   source .venv/bin/activate

   # Windows (PowerShell)
   .venv\Scripts\activate
   ```

4. **Sinkronisasi dependensi project**

   Perintah ini akan menginstal seluruh dependensi (termasuk dependensi development seperti `pytest`) berdasarkan `pyproject.toml` dan `uv.lock` ke dalam virtual environment yang sudah dibuat.

   ```bash
   uv sync --dev
   ```

5. **(Opsional) Jalankan database MySQL lokal**

   Dibutuhkan jika sedang mengerjakan/menguji fitur dari Issue #3 (Integrasi MySQL) dan seterusnya.

   ```bash
   docker-compose up -d
   ```

   `docker-compose.yml` juga sudah menyertakan **phpMyAdmin** sebagai antarmuka web untuk mengelola database MySQL secara visual. Setelah container berjalan, buka:

   ```
   http://localhost:8080
   ```

   Login menggunakan:
   - **Username**: `root`
   - **Password**: `root`

6. **Jalankan pengujian untuk memastikan setup berhasil**

   ```bash
   uv run pytest test_main.py -v --cov=main
   ```

   Jika seluruh test **PASSED**, setup project sudah berhasil dan siap untuk dikembangkan.

7. **(Opsional) Jalankan server FastAPI**

   Dibutuhkan jika sedang mengerjakan/menguji fitur dari Issue #4 (RESTful API) dan seterusnya.

   ```bash
   uv run fastapi dev main.py
   ```

   Dokumentasi API interaktif (Swagger UI) dapat diakses melalui:

   ```
   http://localhost:8000/docs
   ```

8. **Mulai mengembangkan fitur**

   Ikuti alur kerja standar project ini: **issue -> branch -> implementasi -> commit -> pull request -> ci -> merge**. Lihat detail masing-masing fitur di folder [`issues/`](./issues).

   ```bash
   git checkout -b feature/issue-<nomor>-<nama-fitur>
   ```

---

## 🚀 Alur Eskalasi Proyek (Berbasis Issue)

Proyek ini dibangun secara bertahap melalui Pull Request untuk mensimulasikan lingkungan kerja nyata.

### 1. Tahap Dasar (Base)

- **Fitur**: Fungsi validasi password sederhana (Minimal 8 karakter, 1 huruf kapital, 1 angka).
- **Fokus SQA**: Menulis Unit Test dasar untuk memisahkan aturan-aturan validasi menjadi skenario yang terisolasi.

### 2. Issue #1: Validasi Email

- **Fitur**: Menambahkan fungsi validasi format email menggunakan Regular Expression (Regex).
- **Fokus SQA**: Equivalence Partitioning untuk membedakan kelompok format email yang valid (domain benar) dan tidak valid (kurang karakter `@`, dsb).

### 3. Issue #2: Password Hashing

- **Fitur**: Mengamankan password menggunakan algoritma hashing sebelum disimpan.
- **Fokus SQA**: Memastikan fungsionalitas enkripsi berjalan (password asli ≠ hash) dan menguji fungsi verifikasi kecocokan password.

### 4. Issue #3: Integrasi MySQL

- **Fitur**: Menyimpan data kredensial pengguna ke dalam database MySQL.
- **Fokus SQA**:
  - **Integration Testing**: Menggunakan Fixture di pytest untuk Setup (membuat tabel) dan Teardown (menghapus tabel).
  - **Environment Parity**: Menggunakan `docker-compose.yml` di lokal dan Service Containers di GitHub Actions agar environment database selalu konsisten.

### 5. Issue #4: Migrasi ke RESTful API (FastAPI)

- **Fitur**: Mengekspos fungsi-fungsi sebelumnya menjadi endpoint `POST /register`.
- **Fokus SQA**:
  - **API Testing**: Mensimulasikan request HTTP menggunakan TestClient.
  - **Status Code Validation**:
    - 201 Created → sukses
    - 400 Bad Request → duplikasi data
    - 422 Unprocessable Entity → kegagalan validasi (Pydantic)

---

## ⚙️ Skrip Penting (Cheatsheet)

### Inisialisasi Proyek Lokal

```bash
uv init
uv add "fastapi[standard]" pymysql passlib
uv add --dev pytest pytest-cov httpx
```

### Menjalankan Database Lokal (MySQL + phpMyAdmin)

```bash
docker-compose up -d
```

- MySQL dapat diakses di `localhost:3306`
- phpMyAdmin dapat diakses melalui browser di `http://localhost:8080`

### Menjalankan Pengujian (Testing)

```bash
uv run pytest test_main.py -v --cov=main
```

### Menjalankan Server FastAPI

```bash
uv run fastapi dev main.py
```

Dokumentasi API (Swagger UI) dapat diakses di `http://localhost:8000/docs`.
