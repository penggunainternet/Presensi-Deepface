from flask import Flask, request, render_template, jsonify
from deepface import DeepFace
import mysql.connector
import numpy as np
import pickle
import base64
import os
import cv2
from datetime import datetime
from config import MODEL_CACHE_DIR

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

# Set home dir untuk model cache
os.environ['DEEPFACE_HOME'] = MODEL_CACHE_DIR


# ========================
#  DATABASE CONNECT
# ========================
def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="presensi"
    )

# ========================
#  HALAMAN ADMIN REGISTER
# ========================
@app.route("/admin")
def admin_page():
    return render_template("admin_register.html")


@app.route("/admin/register", methods=["POST"])
def admin_register():

    name = request.form["name"]
    photo = request.files["photo"]

    filename = name.replace(" ", "_") + ".jpg"
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    photo.save(path)

    # Ekstraksi embedding
    try:
        rep = DeepFace.represent(path, model_name="ArcFace")[0]["embedding"]
    except Exception as e:
        return f"Error deteksi wajah! <br>Detail: {e}"

    # Simpan embedding sebagai BLOB base64
    emb_blob = base64.b64encode(pickle.dumps(rep)).decode('utf-8')

    db = get_db()
    cursor = db.cursor()
    sql = "INSERT INTO users (name, photo, embedding) VALUES (%s, %s, %s)"
    cursor.execute(sql, (name, filename, emb_blob))
    db.commit()

    return f"""
    <!DOCTYPE html>
    <html lang="id">
    <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>Registrasi Berhasil</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.0/font/bootstrap-icons.css" />
        <style>
            body {{
                background: #F0F4F8;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                padding: 20px;
                font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            }}
            .success-container {{
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.15);
                padding: 40px;
                max-width: 500px;
                text-align: center;
            }}
            .success-icon {{
                font-size: 60px;
                color: #28a745;
                margin-bottom: 20px;
            }}
            .success-title {{
                color: #0066CC;
                font-weight: 700;
                font-size: 28px;
                margin-bottom: 15px;
            }}
            .photo-preview {{
                margin: 30px 0;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }}
            .photo-preview img {{
                width: 100%;
                max-width: 300px;
                display: block;
                margin: 0 auto;
            }}
            .user-info {{
                background: #F8F9FA;
                padding: 20px;
                border-radius: 10px;
                margin: 20px 0;
                border-left: 4px solid #0066CC;
            }}
            .user-info label {{
                font-weight: 600;
                color: #666;
                font-size: 12px;
                text-transform: uppercase;
                display: block;
                margin-bottom: 5px;
            }}
            .user-info p {{
                font-size: 18px;
                color: #333;
                margin: 0;
            }}
            .button-group {{
                margin-top: 30px;
                display: flex;
                gap: 10px;
                justify-content: center;
            }}
            .btn-back {{
                background: #0066CC;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}
            .btn-back:hover {{
                background: #0052A3;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 102, 204, 0.3);
                color: white;
            }}
            .btn-next {{
                background: #00AA66;
                color: white;
                border: none;
                padding: 12px 30px;
                border-radius: 8px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
                text-decoration: none;
                display: inline-block;
            }}
            .btn-next:hover {{
                background: #008A52;
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0, 170, 102, 0.3);
                color: white;
            }}
            .success-message {{
                color: #28a745;
                font-weight: 600;
                font-size: 14px;
                margin-bottom: 10px;
            }}
        </style>
    </head>
    <body>
        <div class="success-container">
            <div class="success-icon">
                <i class="bi bi-check-circle-fill"></i>
            </div>
            
            <div class="success-message">
                <i class="bi bi-check-lg"></i> Registrasi Berhasil!
            </div>
            
            <h1 class="success-title">Karyawan Terdaftar</h1>
            
            <div class="user-info">
                <label>Nama Karyawan</label>
                <p>{name}</p>
            </div>
            
            <div class="photo-preview">
                <img src="/static/uploads/{filename}" alt="Foto {name}">
            </div>
            
            <p style="color: #666; font-size: 14px; margin: 20px 0;">
                <i class="bi bi-info-circle"></i>
                Wajah karyawan telah berhasil didaftarkan dan disimpan ke database.
            </p>
            
            <div class="button-group">
                <a href="/admin" class="btn-back">
                    <i class="bi bi-arrow-left"></i> Daftar Lagi
                </a>
                <a href="/presensi-user" class="btn-next">
                    <i class="bi bi-arrow-right"></i> Presensi
                </a>
            </div>
        </div>
        
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """


# ========================
#  HALAMAN PRESENSI (USER)
# ========================
@app.route("/presensi-user")
def presensi_user():
    return render_template("presensi.html")  # ada ambil kamera + upload foto


# ========================
#  FUNGSI PEMBANDING ARC FACE
# ========================
def cosine_similarity(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# ========================
#  PRESENSI VIA KAMERA (BASE64)
# ========================
@app.route("/presensi-kamera", methods=["POST"])
def presensi_kamera():

    try:
        image_data = request.form["image_data"]
        image_data = image_data.split(",")[1]
        img_bytes = base64.b64decode(image_data)

        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        rep = DeepFace.represent(
            img_path=img,
            model_name="ArcFace",
            detector_backend="retinaface",
            enforce_detection=False
        )

        if len(rep) == 0:
            return jsonify({"status": False, "message": "Wajah tidak terdeteksi!"})

        user_embed = np.array(rep[0]["embedding"])

        # ambil user DB
        db = get_db()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()

        best_user = None
        best_score = -1

        for row in rows:
            emb_db = pickle.loads(base64.b64decode(row["embedding"]))
            emb_db = np.array(emb_db)

            sim = cosine_similarity(user_embed, emb_db)

            if sim > best_score:
                best_score = sim
                best_user = row

        if best_score < 0.40:
            return jsonify({"status": False, "message": "Wajah tidak dikenali!"})

        # catat absensi
        cursor.execute("INSERT INTO absensi (user_id, waktu) VALUES (%s, NOW())",
                       (best_user["id"],))
        db.commit()

        return jsonify({
            "status": True,
            "message": f"Presensi Berhasil: {best_user['name']}",
            "score": float(best_score)
        })

    except Exception as e:
        return jsonify({"status": False, "message": f"Error: {str(e)}"})


if __name__ == "__main__":
    app.run(debug=True)
