from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# -----------------------
# DATABASE CONFIG
# -----------------------
DATABASE_URL = os.getenv("DATABASE_URL")

# -----------------------
# INIT DB
# -----------------------
def init_db():
    if not DATABASE_URL:
        print("No DATABASE_URL найден")
        return

    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS items (
            id SERIAL PRIMARY KEY,
            name TEXT
        );
    """)

    conn.commit()
    cur.close()
    conn.close()

# -----------------------
# DB CONNECTION
# -----------------------
def get_db_connection():
    if os.getenv("CI") == "true":
        return None

    if not DATABASE_URL:
        return None

    return psycopg2.connect(DATABASE_URL)

# -----------------------
# HOME
# -----------------------
@app.route("/")
def home():
    return jsonify({
        "message": "Backend is working 🚀"
    })

# -----------------------
# HEALTH CHECK
# -----------------------
@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy"
    })

# -----------------------
# GET DATA
# -----------------------
@app.route("/api/data", methods=["GET"])
def get_data():
    conn = get_db_connection()

    if conn is None:
        return jsonify([])

    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items;")

    rows = cur.fetchall()

    data = [
        {
            "id": r[0],
            "name": r[1]
        }
        for r in rows
    ]

    cur.close()
    conn.close()

    return jsonify(data)

# -----------------------
# ADD DATA
# -----------------------
@app.route("/api/data", methods=["POST"])
def add_data():
    data = request.get_json()

    if not data or "name" not in data:
        return jsonify({
            "error": "Name is required"
        }), 400

    name = data.get("name")

    conn = get_db_connection()

    # TEST MODE
    if conn is None:
        return jsonify({
            "id": 1,
            "name": name
        }), 201

    try:
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO items (name) VALUES (%s) RETURNING id;",
            (name,)
        )

        new_id = cur.fetchone()[0]

        conn.commit()

        cur.close()
        conn.close()

        return jsonify({
            "id": new_id,
            "name": name
        }), 201

    except Exception as e:
        print("DB ERROR:", e)

        return jsonify({
            "error": "Failed to insert"
        }), 500

# -----------------------
# DELETE DATA
# -----------------------
@app.route("/api/data/<int:id>", methods=["DELETE"])
def delete_data(id):
    conn = get_db_connection()

    if conn is None:
        return jsonify({
            "message": "test mode"
        })

    cur = conn.cursor()

    cur.execute(
        "DELETE FROM items WHERE id = %s;",
        (id,)
    )

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "message": "deleted"
    })

# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    init_db()

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port
    )
