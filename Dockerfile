# ---------- Tahap 1: dependensi dasar ----------
FROM python:3.10-slim AS base
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Tahap 2: unit test (dipakai stage Test di Jenkins) ----------
FROM base AS test
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt
COPY . .
RUN python -m pytest -q tests

# ---------- Tahap 3: image runtime ----------
FROM base AS runtime
COPY app.py ./
EXPOSE 5000
CMD ["python", "app.py"]
