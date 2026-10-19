import os
import time

import pymysql
from flask import Flask, jsonify, redirect, render_template_string, request, url_for

app = Flask(__name__)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.getenv("DB_USER", "appuser"),
    "password": os.getenv("DB_PASSWORD", "apppass"),
    "database": os.getenv("DB_NAME", "catatan_db"),
    "cursorclass": pymysql.cursors.DictCursor,
    "connect_timeout": 5,
}

PAGE = """
<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <title>Catatan Praktikum - Flask + Docker + Jenkins</title>
  <style>
    body { font-family: Arial, sans-serif; max-width: 640px; margin: 40px auto; padding: 0 16px; color: #1f2937; }
    h1 { color: #1f3864; margin-bottom: 4px; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 12px; font-size: 13px; }
    .ok { background: #dcfce7; color: #166534; }
    .fail { background: #fee2e2; color: #991b1b; }
    form { display: flex; gap: 8px; margin: 20px 0; }
    input[type=text] { flex: 1; padding: 8px; border: 1px solid #cbd5e1; border-radius: 6px; }
    button { padding: 8px 16px; background: #2e75b6; color: #fff; border: 0; border-radius: 6px; cursor: pointer; }
    li { padding: 6px 0; border-bottom: 1px solid #e5e7eb; }
    small { color: #6b7280; }
  </style>
</head>
<body>
     <h1>Halo dari Flask + Docker + Jenkins! (build otomatis)</h1>
  <p>Status database:
    <span class="badge {{ 'ok' if db_ok else 'fail' }}">{{ 'terhubung' if db_ok else 'tidak terhubung' }}</span>
  </p>
  <form method="post" action="{{ url_for('tambah') }}">
    <input type="text" name="isi" placeholder="Tulis catatan baru" required maxlength="255">
    <button type="submit">Simpan</button>
  </form>
  <ul>
    {% for n in notes %}
      <li>{{ n.isi }} <small>({{ n.dibuat }})</small></li>
    {% else %}
      <li><small>Belum ada catatan.</small></li>
    {% endfor %}
  </ul>
</body>
</html>
"""


def get_connection():
    return pymysql.connect(**DB_CONFIG)


def init_db(retries=10, delay=3):
    """Buat tabel jika belum ada. Dicoba berulang karena MySQL butuh waktu untuk siap."""
    for attempt in range(1, retries + 1):
        try:
            conn = get_connection()
            try:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS notes (
                            id INT AUTO_INCREMENT PRIMARY KEY,
                            isi VARCHAR(255) NOT NULL,
                            dibuat TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                        """
                    )
                conn.commit()
            finally:
                conn.close()
            return True
        except pymysql.MySQLError as exc:
            print(f"[init_db] percobaan {attempt}/{retries} gagal: {exc}", flush=True)
            time.sleep(delay)
    return False


def fetch_notes():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, isi, dibuat FROM notes ORDER BY id DESC LIMIT 50")
            return cur.fetchall()
    finally:
        conn.close()


def insert_note(isi):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("INSERT INTO notes (isi) VALUES (%s)", (isi,))
        conn.commit()
    finally:
        conn.close()


@app.route("/")
def index():
    try:
        notes, db_ok = fetch_notes(), True
    except pymysql.MySQLError:
        notes, db_ok = [], False
    return render_template_string(PAGE, notes=notes, db_ok=db_ok)


@app.route("/tambah", methods=["POST"])
def tambah():
    isi = request.form.get("isi", "").strip()
    if isi:
        insert_note(isi[:255])
    return redirect(url_for("index"))


@app.route("/api/notes", methods=["GET", "POST"])
def api_notes():
    if request.method == "POST":
        isi = (request.get_json(silent=True) or {}).get("isi", "").strip()
        if not isi:
            return jsonify(error="field 'isi' wajib diisi"), 400
        insert_note(isi[:255])
        return jsonify(status="created"), 201
    return jsonify([{**n, "dibuat": str(n["dibuat"])} for n in fetch_notes()])


@app.route("/health")
def health():
    try:
        conn = get_connection()
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
        finally:
            conn.close()
        return jsonify(status="ok", database="connected"), 200
    except pymysql.MySQLError as exc:
        return jsonify(status="error", database=str(exc)), 503


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
