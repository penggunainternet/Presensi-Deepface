# 🚀 Railway Deployment Guide - Sistem Presensi Wajah

## Prerequisites

- GitHub Account (push code ke GitHub dulu)
- Railway Account (https://railway.app)
- MySQL Database (PlanetScale atau railway MySQL add-on)

---

## Step 1: Push Code ke GitHub

```bash
# Jika belum ada git
git init
git add .
git commit -m "Initial commit - presensi wajah app"
git branch -M main

# Add remote (ganti USERNAME dengan GitHub username Anda)
git remote add origin https://github.com/USERNAME/presensi.git
git push -u origin main
```

---

## Step 2: Setup di Railway

### 2.1 Login ke Railway

1. Buka https://railway.app
2. Klik "Login"
3. Pilih "GitHub" login
4. Authorize Railway

### 2.2 Create New Project

1. Klik "Create New Project"
2. Pilih "Deploy from GitHub repo"
3. Pilih repository `presensi`
4. Railway akan auto-detect Flask app

### 2.3 Add MySQL Database

1. Di Railway Dashboard, klik "Add Service"
2. Pilih "Database" → "MySQL"
3. Railway akan auto-create MySQL instance

### 2.4 Configure Environment Variables

1. Di project settings, buka "Variables"
2. Add variables berdasarkan `.env.example`:

```
DB_HOST=mysql.railway.internal
DB_USER=[dari MySQL service credentials]
DB_PASSWORD=[dari MySQL service credentials]
DB_NAME=presensi
DB_PORT=3306
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000
```

Cara dapat credentials MySQL dari Railway:

- Klik MySQL service di dashboard
- Buka tab "Connect"
- Copy nilai Host, Username, Password

### 2.5 Create Database & Tables

Di Railway MySQL console, jalankan SQL init:

```sql
CREATE DATABASE IF NOT EXISTS presensi;
USE presensi;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    photo VARCHAR(255),
    embedding LONGTEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE absensi (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE INDEX idx_user_id ON absensi(user_id);
```

---

## Step 3: Deploy

1. Railway otomatis deploy saat push ke main branch
2. Tunggu deployment selesai (~2-3 menit)
3. Cek status di Railway Dashboard

---

## Step 4: Verify Deployment

1. Buka URL yang diberikan Railway (misal: `presensi-production.up.railway.app`)
2. Test: `/` → lihat halaman presensi
3. Test: `/admin` → halaman registrasi admin

---

## Troubleshooting

### Build Failed: "ModuleNotFoundError"

- Pastikan `requirements.txt` lengkap
- Railway harus install semua dependencies

### Runtime Error: "DB Connection Failed"

- Cek environment variables DB_HOST, DB_USER, DB_PASSWORD
- Pastikan MySQL service sudah running di Railway
- Cek koneksi ke database

### TensorFlow Too Large

- Railway free tier mungkin slow download TF (2GB)
- Solusi: Gunakan lighter model atau upgrade plan

---

## Production Tips

### 1. Security

```env
FLASK_ENV=production
FLASK_DEBUG=0
```

Jangan set ini ke debug/development!

### 2. Model Optimization

Gunakan `arcface_fp16.tflite` saja (lebih ringan):

- File size: ~50 MB
- Memory: ~200 MB saat runtime
- Speed: ~80-100ms per embedding

### 3. Monitoring

- Railway Dashboard → view logs
- Cek "Deployments" tab untuk history
- Monitor CPU/Memory usage

### 4. Backup Database

Railway MySQL free tier limited. Backup regular:

```bash
mysqldump -h [HOST] -u [USER] -p[PASSWORD] presensi > backup.sql
```

---

## Cost Estimate

- **Free Tier**: $0/bulan (30 hari trial + $5 credit)
- **Setelah free**: ~$5-10/bulan (tergantung usage)
- **Paid Plan**: Mulai $5/bulan per service

---

## Next Steps

1. Connect code ke GitHub
2. Setup Railway account & MySQL
3. Configure env variables
4. Deploy!
5. Test app di production URL

**Questions?** Check Railway docs: https://docs.railway.app
