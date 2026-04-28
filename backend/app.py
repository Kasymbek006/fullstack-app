from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# -----------------------
# DATABASE URL
# -----------------------
DATABASE_URL = os.getenv("DATABASE_URL")


# -----------------------
# DB CONNECTION
# -----------------------
def get_db_connection():
    try:
        if not DATABASE_URL:
            print("No DATABASE_URL найден")
            return None

        return psycopg2.connect(DATABASE_URL)
    except Exception as e:
        print("Ошибка подключения к БД:", e)
        return None


# -----------------------
# ROUTES
# -----------------------

@app.route("/")
def home():
    return "Backend is working 🚀"


# GET ALL DATA
@app.route("/api/data", methods=["GET"])
def get_data():
    conn = get_db_connection()

    if conn is None:
        return jsonify([])

    try:
        cur = conn.cursor()
        cur.execute("SELECT id, name FROM data;")
        rows = cur.fetchall()

        result = [{"id": r[0], "name": r[1]} for r in rows]

        cur.close()
        conn.close()

        return jsonify(result)

    except Exception as e:
        print("Ошибка GET:", e)
        return jsonify([])


# ADD DATA
@app.route("/api/data", methods=["POST"])
def add_data():
    conn = get_db_connection()

    if conn is None:
        return jsonify({"error": "DB not available"}), 500

    try:
        data = request.get_json()
        name = data.get("name")

        cur = conn.cursor()
        cur.execute("INSERT INTO data (name) VALUES (%s)", (name,))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Added"}), 201

    except Exception as e:
        print("Ошибка POST:", e)
        return jsonify({"error": "Failed to insert"}), 500


# DELETE DATA
@app.route("/api/data/<int:id>", methods=["DELETE"])
def delete_data(id):
    conn = get_db_connection()

    if conn is None:
        return jsonify({"error": "DB not available"}), 500

    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM data WHERE id = %s", (id,))
        conn.commit()

        cur.close()
        conn.close()

        return jsonify({"message": "Deleted"})

    except Exception as e:
        print("Ошибка DELETE:", e)
        return jsonify({"error": "Failed to delete"}), 500


# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
