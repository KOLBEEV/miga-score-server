from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

def init_db():
    with sqlite3.connect("scores.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            buyer TEXT,
            score INTEGER,
            money INTEGER,
            time TEXT
        )""")

@app.route("/submit", methods=["POST"])
def submit_score():
    data = request.json
    with sqlite3.connect("scores.db") as conn:
        conn.execute("""
        INSERT INTO scores (username, buyer, score, money, time)
        VALUES (?, ?, ?, ?, ?)""",
        (data["username"], data["buyer"], data["score"], data["money"], datetime.now().isoformat()))
    return {"status": "ok"}, 200

@app.route("/top", methods=["GET"])
def get_top():
    with sqlite3.connect("scores.db") as conn:
        result = conn.execute("""
        SELECT username, money FROM scores
        ORDER BY money DESC
        LIMIT 10
        """).fetchall()
    return jsonify(result)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)
