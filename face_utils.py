import face_recognition
import json
import base64
import numpy as np
import cv2
import os
import mysql.connector
from database import get_db_connection


# ================= REGISTER USER =================
def register_user(name, email, image_data):

    try:
        if not os.path.exists("dataset"):
            os.makedirs("dataset")

        # Safe filename (remove spaces)
        safe_name = name.replace(" ", "_")

        # Decode base64 image
        header, encoded = image_data.split(",", 1)
        image_bytes = base64.b64decode(encoded)

        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        # Save image in dataset folder
        image_path = f"dataset/{safe_name}.jpg"
        cv2.imwrite(image_path, image)

        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        encodings = face_recognition.face_encodings(rgb_image)

        if len(encodings) == 0:
            print("❌ Face not detected during registration")
            return "no_face"

        encoding_str = json.dumps(encodings[0].tolist())

        conn = get_db_connection()
        cursor = conn.cursor()

        print("Saving into users table:", name, email)

        cursor.execute(
            "INSERT INTO users (name, email, face_encoding) VALUES (%s, %s, %s)",
            (name, email, encoding_str)
        )

        conn.commit()
        conn.close()

        print("✅ User saved successfully")
        return "success"

    except mysql.connector.Error as e:
        print("Database Error:", e)
        return "duplicate"


# ================= VERIFY + ATTENDANCE =================
def verify_user(image_data):

    header, encoded = image_data.split(",", 1)
    image_bytes = base64.b64decode(encoded)

    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    unknown_encodings = face_recognition.face_encodings(rgb_image)

    if len(unknown_encodings) == 0:
        return "no_face"

    unknown_encoding = unknown_encodings[0]

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, face_encoding FROM users")
    users = cursor.fetchall()

    for user in users:
        stored_name = user[0]
        stored_encoding = json.loads(user[1])

        matches = face_recognition.compare_faces(
            [stored_encoding], unknown_encoding
        )

        if matches[0]:
            # Insert attendance record
            cursor.execute(
                "INSERT INTO attendance (user_name) VALUES (%s)",
                (stored_name,)
            )
            conn.commit()
            conn.close()
            return stored_name

    conn.close()
    return "no_match"