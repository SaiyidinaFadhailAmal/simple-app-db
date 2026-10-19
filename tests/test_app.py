import app as app_module


class FakeCursor:
    def __init__(self, store):
        self.store = store
        self._rows = []

    def execute(self, sql, params=None):
        if sql.strip().upper().startswith("INSERT"):
            self.store.append({"id": len(self.store) + 1, "isi": params[0], "dibuat": "2026-10-18 10:00:00"})
        elif sql.strip().upper().startswith("SELECT ID"):
            self._rows = list(reversed(self.store))

    def fetchall(self):
        return self._rows

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


class FakeConn:
    def __init__(self, store):
        self.store = store

    def cursor(self):
        return FakeCursor(self.store)

    def commit(self):
        pass

    def close(self):
        pass


def make_client(monkeypatch):
    store = []
    monkeypatch.setattr(app_module, "get_connection", lambda: FakeConn(store))
    app_module.app.config["TESTING"] = True
    return app_module.app.test_client(), store


def test_health_ok(monkeypatch):
    client, _ = make_client(monkeypatch)
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json()["database"] == "connected"


def test_halaman_utama(monkeypatch):
    client, _ = make_client(monkeypatch)
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"Flask + Docker + Jenkins" in resp.data


def test_tambah_dan_baca_catatan(monkeypatch):
    client, store = make_client(monkeypatch)
    assert client.post("/api/notes", json={"isi": "pipeline pertama"}).status_code == 201
    data = client.get("/api/notes").get_json()
    assert data[0]["isi"] == "pipeline pertama"
    assert len(store) == 1


def test_catatan_kosong_ditolak(monkeypatch):
    client, _ = make_client(monkeypatch)
    assert client.post("/api/notes", json={"isi": "  "}).status_code == 400
