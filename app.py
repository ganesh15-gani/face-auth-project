from flask import Flask, render_template, request, redirect, session, url_for, send_from_directory
from face_utils import register_user, verify_user
from database import get_db_connection
import os

app = Flask(__name__)
app.secret_key = "ganesh_super_secret_key"


# ================= USER ROUTES =================

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        image_data = request.form["image_data"]

        result = register_user(name, email, image_data)

        if result == "success":
            return redirect(url_for("index"))
        elif result == "duplicate":
            return "Email already registered"
        elif result == "no_face":
            return "No face detected"

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        image_data = request.form["image_data"]
        result = verify_user(image_data)

        if result == "no_match":
            return "Face not recognized"
        elif result == "no_face":
            return "No face detected"
        else:
            session["user"] = result
            return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))

    username = session["user"]
    safe_name = username.replace(" ", "_")

    return render_template(
        "dashboard.html",
        username=username,
        filename=safe_name + ".jpg"
    )


@app.route("/dataset/<filename>")
def serve_image(filename):
    return send_from_directory("dataset", filename)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ================= ADMIN =================

@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()

        if username == "admin" and password == "admin123":
            session["admin"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            return "Invalid Admin Credentials"

    return render_template("admin_login.html")


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM users")
    total_users = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "admin_dashboard.html",
        users=users,
        total_users=total_users
    )


@app.route("/admin/attendance")
def view_attendance():
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT user_name, login_time FROM attendance ORDER BY login_time DESC"
    )
    records = cursor.fetchall()

    conn.close()

    return render_template("attendance.html", records=records)


@app.route("/delete_user/<int:user_id>")
def delete_user(user_id):
    if "admin" not in session:
        return redirect(url_for("admin_login"))

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM users WHERE id=%s", (user_id,))
    user = cursor.fetchone()

    if user:
        username = user[0]
        safe_name = username.replace(" ", "_")

        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()

        image_path = f"dataset/{safe_name}.jpg"
        if os.path.exists(image_path):
            os.remove(image_path)

    conn.close()
    return redirect(url_for("admin_dashboard"))


# ================= RENDER DEPLOY FIX =================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)