import mysql.connector

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",   # XAMPP default empty
        database="face_auth_system"
    )