# Presensi Deepface 🎯

Sistem presensi berbasis pengenalan wajah menggunakan teknologi deep learning **DeepFace** dan **ArcFace**. Aplikasi web yang memungkinkan registrasi karyawan dan pencatatan absensi secara otomatis melalui pengenalan wajah.

![Badge Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Badge Flask](https://img.shields.io/badge/Flask-2.0+-green.svg)
![Badge Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple.svg)
![Badge License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ Fitur Utama

- 👤 **Admin Panel** - Registrasi wajah karyawan baru
- 📸 **Presensi via Kamera** - Capture wajah langsung dari webcam
- 📁 **Presensi via Upload** - Upload foto untuk presensi
- 🧠 **Deep Learning** - Ekstraksi embedding wajah menggunakan ArcFace
- 📊 **Matching Otomatis** - Pencocokan dengan cosine similarity
- 🎨 **UI Modern** - Bootstrap 5 dengan design responsif
- 💾 **Database MySQL** - Penyimpanan data terstruktur
- 🔍 **Real-time Detection** - Deteksi wajah dengan RetinaFace

## 🏗️ Arsitektur

```
presensi/
├── app.py                    # Backend Flask
├── templates/
│   ├── admin_register.html   # Admin panel UI
│   └── presensi.html         # User presensi UI
├── static/
│   └── uploads/              # Folder penyimpanan foto
├── requirements.txt          # Dependencies Python
└── README.md                 # Dokumentasi
```

## 🛠️ Tech Stack

| Komponen | Teknologi |
|----------|-----------|
| **Backend** | Flask (Python) |
| **Database** | MySQL |
| **AI/ML** | DeepFace, ArcFace |
| **Face Detection** | RetinaFace |
| **Frontend** | HTML5, Bootstrap 5, JavaScript Vanilla |
| **Image Processing** | OpenCV, NumPy |

## 📋 Requirements

- Python 3.8+
- MySQL Server
- pip

## 🚀 Instalasi

### 1. Clone Repository
```bash
git clone https://github.com/penggunainternet/Presensi-Deepface.git
cd Presensi-Deepface
```

### 2. Setup Virtual Environment
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Setup Database

**Create Database:**
```sql
CREATE DATABASE presensi;
USE presensi;

-- Users table
CREATE TABLE users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  photo VARCHAR(255),
  embedding LONGTEXT NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Attendance table
CREATE TABLE absensi (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (user_id) REFERENCES users(id)
);
```

### 5. Konfigurasi Database (app.py)
Edit bagian database connection di `app.py`:
```python
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",  # Ganti dengan password MySQL Anda
        database="presensi"
    )
```

### 6. Jalankan Aplikasi
```bash
python app.py
```

Aplikasi akan berjalan di: **http://localhost:5000**

## 📖 Cara Penggunaan

### Admin Panel
1. Akses: http://localhost:5000/admin
2. Masukkan nama karyawan
3. Upload foto wajah karyawan
4. Klik "Daftarkan Karyawan"
5. Embedding wajah tersimpan di database

### Presensi User
1. Akses: http://localhost:5000/presensi-user
2. **Pilih Metode:**
   - **Kamera**: Klik "Ambil Foto & Presensi" - posisikan wajah ke kamera
   - **Upload**: Pilih file foto dan klik "Upload Foto & Presensi"
3. Sistem akan mencocokkan wajah dengan database
4. Jika cocok (similarity > 0.40), presensi tercatat otomatis

## 🔧 API Endpoints

| Method | Endpoint | Deskripsi |
|--------|----------|-----------|
| GET | `/admin` | Admin panel registration |
| POST | `/admin/register` | Register wajah karyawan baru |
| GET | `/presensi-user` | Halaman presensi user |
| POST | `/presensi-kamera` | Presensi via kamera (base64) |
| POST | `/presensi-upload` | Presensi via upload foto |

## 📊 Database Schema

### Users Table
```sql
users {
  id: INT (Primary Key)
  name: VARCHAR(100)
  photo: VARCHAR(255) - nama file foto
  embedding: LONGTEXT - base64 encoded embedding vector
  created_at: TIMESTAMP
}
```

### Attendance Table
```sql
absensi {
  id: INT (Primary Key)
  user_id: INT (Foreign Key)
  waktu: TIMESTAMP
}
```

## 🎯 Alur Kerja Sistem

### Registrasi Karyawan
```
Upload Foto 
  ↓
Ekstraksi Embedding (ArcFace)
  ↓
Encode base64
  ↓
Simpan ke Database
```

### Presensi
```
Capture/Upload Foto
  ↓
Ekstraksi Embedding
  ↓
Hitung Cosine Similarity dengan semua user
  ↓
Ambil user dengan score tertinggi
  ↓
Jika score > 0.40: Catat Absensi ✓
Jika score < 0.40: Tolak (Wajah tidak dikenali) ✗
```

## ⚙️ Konfigurasi

### Threshold Similarity
Edit di `app.py` baris threshold:
```python
if best_score < 0.40:  # Ubah threshold sesuai kebutuhan
    return jsonify({"status": False, "message": "Wajah tidak dikenali!"})
```

### Model AI
Menggunakan ArcFace untuk embedding:
```python
rep = DeepFace.represent(img_path, model_name="ArcFace")
```

## 🐛 Troubleshooting

| Problem | Solusi |
|---------|--------|
| `ModuleNotFoundError: No module named 'deepface'` | Run: `pip install deepface` |
| Database connection error | Cek konfigurasi MySQL & credentials |
| Camera tidak bisa diakses | Izinkan browser akses kamera |
| Wajah tidak terdeteksi | Pastikan pencahayaan cukup & wajah jelas |
| Foto tidak cocok setelah registrasi | Ubah threshold similarity (lebih rendah) |

## 📦 Dependencies

```txt
Flask==2.3.0
DeepFace==0.0.67
mysql-connector-python==8.0.33
opencv-python==4.7.0.72
numpy==1.24.3
Pillow==10.0.0
tensorflow==2.13.0
```

## 🔐 Security Note

⚠️ **Production Deployment:**
- Ubah `debug=True` ke `debug=False`
- Gunakan WSGI server (Gunicorn, uWSGI)
- Enkripsi database password
- Setup HTTPS
- Validate & sanitize input

## 📝 License

MIT License - Bebas digunakan untuk keperluan apapun

## 👨‍💻 Author

**Presensi Deepface Development Team**

## 📞 Support

Untuk pertanyaan atau issue, silahkan buat issue di repository ini.

---

**Made with ❤️ using DeepFace & Flask**
