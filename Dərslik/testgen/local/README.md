# Local run — copy-paste komandalar

Bütün komandalar `Dərslik/testgen/` papkasından işlədilir.

---

## 0. Əvvəlcədən (yalnız bir dəfə)

Docker Desktop işləyirsə keç 1-ci addıma. Əks halda Docker Desktop-u aç və WSL2 status yaşıl olana qədər gözlə.

`.env` faylı olmalıdır. Əgər yoxdursa:
```bash
cp .env.example .env
```
Sonra `.env`-i aç və `GEMINI_API_KEY` doldur.

---

## 1. İlk dəfə (və ya Dockerfile/package.json dəyişəndə)

```bash
docker compose build
```
Bu 3-5 dəqiqə çəkə bilər — image-lər qurulur, `npm ci` image-in içində işləyir, növbəti dəfələrdə lazım olmayacaq.

---

## 2. Gündəlik — siteyi qaldır

```bash
docker compose up -d
```
30-60 saniyə sonra:
- frontend:  http://localhost:3000
- backend:   http://localhost:8000/health
- qdrant:    http://localhost:6333/dashboard

---

## 3. Statusa bax

```bash
docker compose ps
```
Hamısı `healthy` və ya `running` olmalıdır.

---

## 4. Logları izlə

```bash
# bütün servislər
docker compose logs -f

# yalnız backend (pipeline logları burdadır)
docker compose logs -f backend

# yalnız frontend
docker compose logs -f frontend

# yalnız bizim testgen logları (retrieval, variant, validation)
docker compose logs backend | grep testgen
```

---

## 5. Diaqnostika — RAG dolumu yoxla

```bash
docker compose exec backend python scripts/qdrant_health.py
docker compose exec backend python scripts/qdrant_health.py --subject math --grade 11
```

---

## 6. Saytı dayandır

```bash
# saxla məlumatı (db + qdrant)
docker compose down

# HƏR ŞEYİ sil (db, qdrant, volumes — diqqət, data itir)
docker compose down -v
```

---

## 7. Kiçik müdaxilələr

```bash
# backend restart (kod dəyişikliyi üçün lazım deyil, reload işləyir)
docker compose restart backend

# frontend restart
docker compose restart frontend

# db shell
docker compose exec db psql -U testgen -d testgen

# backend shell
docker compose exec backend bash
```

---

## 8. Problem olsa — təmiz başlanğıc

```bash
docker compose down
docker compose build --no-cache
docker compose up -d
```

---

## 9. Production build (Digital Ocean üçün)

```bash
docker compose -f docker-compose.prod.yml up -d --build
```
