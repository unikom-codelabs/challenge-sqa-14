# Challenge SQA 14 — Solusi

Implementasi lengkap untuk:

1. Validasi password dan email.
2. Password hashing dan verification.
3. Penyimpanan user ke MySQL.
4. RESTful API FastAPI `POST /register`.
5. Unit test, integration test, API test, dan GitHub Actions CI.

## Setup

```bash
git clone https://github.com/unikom-codelabs/challenge-sqa-14.git
cd challenge-sqa-14
uv sync --dev
docker compose up -d
uv run pytest test_main.py -v --cov=main
```

Jalankan API:

```bash
uv run fastapi dev main.py
```

Swagger UI: `http://localhost:8000/docs`
