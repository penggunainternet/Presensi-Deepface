from flask import Flask, request, render_template, jsonify
from deepface import DeepFace
import mysql.connector
import numpy as np
import pickle
import base64
import os
import cv2
from datetime import datetime

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"


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
        <h3>Registrasi Berhasil!</h3>
        <p>Nama: {name}</p>
        <img src='/static/uploads/{filename}' width='200'>
        <br><br>
        <a href='/admin'>Kembali</a>
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


# ========================
#  PRESENSI VIA UPLOAD FOTO
# ========================
@app.route("/presensi-upload", methods=["POST"])
def presensi_upload():

    if "foto" not in request.files:
        return jsonify({"status": False, "message": "Foto tidak ditemukan!"})

    file = request.files["foto"]
    temp_path = "temp_user.jpg"
    file.save(temp_path)

    try:
        rep = DeepFace.represent(temp_path, model_name="ArcFace")[0]["embedding"]
        user_embed = np.array(rep)

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
