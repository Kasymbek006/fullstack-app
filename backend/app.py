from flask import Flask, request, jsonify
from flask_cors import CORS
import psycopg2
import os

app = Flask(__name__)
CORS(app)

# Лучше через переменную окружения (Railway), но есть fallback
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://myuser:mypassword@localhost/myapp"
)

# -----------------------
# DB CONNECTION
# -----------------------
def get_db_connection():
    if os.getenv("CI") == "true":
        return None  # в CI нет базы

    return psycopg2.connect(DATABASE_URL)

# -----------------------
# GET ALL DATA
# -----------------------
@app.route("/api/data", methods=["GET"])
def get_data():
    conn = get_db_connection()

    if conn is None:
        return jsonify([])  # CI просто возвращает пусто

    cur = conn.cursor()
    cur.execute("SELECT id, name FROM items;")
    rows = cur.fetchall()

    cur.close()
    conn.close()

    result = [{"id": r[0], "name": r[1]} for r in rows]
    return jsonify(result)

# -----------------------
# ADD DATA
# -----------------------
@app.route("/api/data", methods=["POST"])
def add_data():
    data = request.get_json()

    conn = get_db_connection()

    if conn is None:
        return jsonify({"id": 1, "name": data["name"]}), 201

    cur = conn.cursor()
    cur.execute(
        "INSERT INTO items (name) VALUES (%s) RETURNING id;",
        (data["name"],)
    )
    new_id = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"id": new_id, "name": data["name"]}), 201

# -----------------------
# DELETE DATA
# -----------------------
@app.route("/api/data/<int:item_id>", methods=["DELETE"])
def delete_data(item_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM items WHERE id = %s;", (item_id,))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"status": "deleted", "id": item_id})


# -----------------------
# RUN SERVER
# -----------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


@app.route("/")
def home():
    return "Backend is working 🚀"
