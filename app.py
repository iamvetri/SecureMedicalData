from flask import Flask, render_template, request, redirect, url_for, session, send_file
import os
import cv2
import time
import json
from encryption import *
from cloud_upload import upload_to_drive
from roles_config import has_permission

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.secret_key = 'your_secret_key'
USER_FILE = "users.json"

def load_users():
    if not os.path.exists(USER_FILE):
        return {}
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_user(username, password, role):
    users = load_users()
    users[username] = {"password": password, "role": role}
    with open(USER_FILE, "w") as f:
        json.dump(users, f)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        role = request.form["role"]
        users = load_users()
        if username in users:
            return render_template("register.html", message="Username already exists")
        save_user(username, password, role)
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        user = users.get(username)

        if user and user["password"] == password:
            session["username"] = username
            session["role"] = user["role"]
            return redirect(url_for("index"))
        else:
            message = "Check username and password"
            return render_template("login.html", message=message)
    return render_template("login.html", message=message)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/", methods=["GET", "POST"])
def index():
    if 'username' not in session:
        return redirect(url_for("login"))
    if request.method == "POST":
        if not has_permission(session["role"], "can_encrypt"):
            return "Access denied: You are not allowed to upload."

        file = request.files["image"]
        path = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(path)

        img = process_image(path)
        binary = image_to_binary(img)
        dna = binary_to_dna(binary)

        pso = PSO()
        key = pso.optimize()

        start_enc = time.time()
        encrypted_dna = dna_encrypt(dna, key)
        enc_time = time.time() - start_enc

        out_path = os.path.join(UPLOAD_FOLDER, "encrypted_dna.txt")
        with open(out_path, "w") as f:
            f.write(encrypted_dna)

        drive_link = upload_to_drive(out_path)

        decrypted_dna = dna_decrypt(encrypted_dna, key)
        binary_decrypted = dna_to_binary(decrypted_dna)
        img_decrypted = binary_to_image(binary_decrypted)

        dec_start = time.time()
        cv2.imwrite(os.path.join(UPLOAD_FOLDER, "decrypted_image.png"), img_decrypted)
        dec_time = time.time() - dec_start

        return render_template("result.html", key=key, filename="encrypted_dna.txt", drive_link=drive_link,
                               enc_time=enc_time, dec_time=dec_time)
    return render_template("index.html", username=session.get("username"), role=session.get("role"))

@app.route("/decrypt", methods=["GET", "POST"])
def decrypt():
    if 'username' not in session:
        return redirect(url_for("login"))
    if not has_permission(session["role"], "can_decrypt"):
        return "Access denied: You are not allowed to decrypt."

    if request.method == "POST":
        encrypted_dna = request.form["encrypted_dna"]
        key_str = request.form["key"]
        try:
            key = eval(key_str)
        except:
            return "Invalid key format. Use [2,0,1,3] format."

        decrypted_dna = dna_decrypt(encrypted_dna, key)
        binary = dna_to_binary(decrypted_dna)
        img = binary_to_image(binary)
        output_path = os.path.join(UPLOAD_FOLDER, "decrypted_image.png")
        cv2.imwrite(output_path, img)
        return render_template("decryption_result.html", image_path="decrypted_image.png")
    return render_template("decryption_form.html")

@app.route("/download/<filename>")
def download(filename):
    return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)

@app.route("/uploads/<filename>")
def get_file(filename):
    return send_file(os.path.join("uploads", filename), as_attachment=True)

if __name__ == "__main__":
    app.run(debug=True)