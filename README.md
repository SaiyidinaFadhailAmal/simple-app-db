# simple-app-db

Aplikasi catatan sederhana (Flask + MySQL) untuk praktikum Komputasi Awan: integrasi Jenkins dengan GitHub, database, dan stage Docker.

## Struktur

| Berkas | Fungsi |
|---|---|
| `app.py` | Aplikasi Flask, terhubung ke MySQL lewat PyMySQL |
| `tests/test_app.py` | Unit test (database di-mock) |
| `Dockerfile` | Multi-stage: `base`, `test` (menjalankan pytest), `runtime` |
| `docker-compose.yml` | Layanan `app` dan `db` (MySQL 8.0 + healthcheck + volume) |
| `db/init.sql` | Skema dan data awal tabel `notes` |
| `Jenkinsfile` | Pipeline untuk agent Windows (`bat`) |
| `Jenkinsfile.linux` | Pipeline untuk agent Linux (`sh`) |

## Menjalankan lokal

```bash
docker compose up -d --build
# buka http://localhost:5000  dan  http://localhost:5000/health
docker compose down        # tambahkan -v untuk menghapus data MySQL
```

## Alur pipeline

Checkout -> Unit Test -> Build Docker Image -> Push Docker Image -> Deploy (App + MySQL) -> Smoke Test

## Catatan penting

- Ganti `dockerhubuser` pada `IMAGE_NAME` di Jenkinsfile dengan username Docker Hub.
- Buat credential Jenkins bertipe *Username with password* dengan ID `dockerhub-credentials` (password = Docker Hub access token).
- Jenkins harus bisa menjalankan perintah `docker` dan `docker compose` di mesin yang sama dengan Docker Engine. Pada Windows, jalankan service Jenkins dengan akun yang menjalankan Docker Desktop.
- Jika Jenkins berjalan di dalam container (`jenkins/jenkins:lts`), image tersebut belum memiliki Docker CLI, dan `localhost:5000` mengarah ke container Jenkins, bukan ke host. Gunakan Jenkins langsung di host (Windows service) atau pasang Docker CLI dan ubah alamat smoke test.
- Jangan commit file `.env`; gunakan `.env.example` sebagai acuan.
