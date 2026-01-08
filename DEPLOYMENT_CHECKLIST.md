# ✅ Railway Deployment Checklist

## Project Ready ✓

- [x] Procfile dibuat (Gunicorn config)
- [x] requirements.txt updated (python-dotenv, gunicorn)
- [x] .env.example template created
- [x] app.py support environment variables
- [x] Code pushed ke GitHub

---

## Sebelum Deploy, Lakukan:

### 1. Buat Railway Account

- [ ] Buka https://railway.app
- [ ] Login dengan GitHub
- [ ] Authorize Railway

### 2. Create Project

- [ ] Klik "New Project"
- [ ] Pilih "Deploy from GitHub repo"
- [ ] Pilih repo "Presensi-Deepface"

### 3. Add MySQL Service

- [ ] Klik "Add Service"
- [ ] Pilih "Database" → "MySQL"
- [ ] Tunggu MySQL instance ready

### 4. Set Environment Variables

- [ ] Klik project → Variables
- [ ] Copy credentials dari MySQL service
- [ ] Add variables (lihat .env.example):
  - [ ] DB_HOST = mysql.railway.internal
  - [ ] DB_USER = [dari MySQL]
  - [ ] DB_PASSWORD = [dari MySQL]
  - [ ] DB_NAME = presensi
  - [ ] DB_PORT = 3306
  - [ ] FLASK_ENV = production
  - [ ] FLASK_DEBUG = 0
  - [ ] PORT = 5000

### 5. Initialize Database

- [ ] Buka MySQL service di Railway
- [ ] Klik "Connect" → gunakan credentials
- [ ] Copy-paste SQL dari RAILWAY_DEPLOYMENT.md
- [ ] Jalankan semua queries

### 6. Deploy & Monitor

- [ ] Railway akan auto-deploy (liat Deployments tab)
- [ ] Tunggu status "Success"
- [ ] Buka URL yang diberikan Railway
- [ ] Test: `/` (presensi page)
- [ ] Test: `/admin` (registration page)

---

## File Structure Sekarang:

```
presensi/
├── Procfile ✓ (Railway start command)
├── .env.example ✓ (env template)
├── requirements.txt ✓ (dengan gunicorn, python-dotenv)
├── app.py ✓ (updated untuk env variables)
├── RAILWAY_DEPLOYMENT.md ✓ (panduan lengkap)
├── config.py
├── models/
│   ├── arcface_fp16.tflite
│   └── arcface_fp16_v2.tflite
├── templates/
│   ├── presensi.html (hanya 2 opsi model)
│   └── admin_register.html (hanya 2 opsi model)
└── static/
    └── uploads/
```

---

## Expected URL

`https://presensi-production.up.railway.app`
(atau nama lain sesuai pilihan Railway)

---

## Troubleshooting Quick Tips

**Q: Build gagal, Module not found?**
A: Pastikan requirements.txt lengkap semua dependencies

**Q: Database connection error?**
A: Cek env variables DB_HOST, DB_USER, DB_PASSWORD di Railway

**Q: App crash saat startup?**
A: Check Railway logs → cari error message

**Q: Deployment terlalu lama?**
A: TensorFlow perlu download (~2GB), tunggu saja

---

## Support

Dokumentasi lengkap: RAILWAY_DEPLOYMENT.md (di repo)

Good luck! 🚀
