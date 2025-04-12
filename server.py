from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Инициализация БД
def init_db():
    with sqlite3.connect("scores.db") as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            buyer TEXT,
            score INTEGER,
            money INTEGER,
            time TEXT
        )
        """)

# Отправка результата игрока
@app.route("/submit", methods=["POST"])
def submit_score():
    data = request.json
    now = datetime.now().isoformat()

    with sqlite3.connect("scores.db") as conn:
        cur = conn.cursor()

        # Проверка: игрок уже есть?
        cur.execute("SELECT score, money FROM scores WHERE username = ?", (data["username"],))
        existing = cur.fetchone()

        if existing:
            old_score, old_money = existing
            new_score = max(old_score, data["score"])
            new_money = old_money + data["money"]

            cur.execute("""
                UPDATE scores
                SET buyer = ?, score = ?, money = ?, time = ?
                WHERE username = ?
            """, (data["buyer"], new_score, new_money, now, data["username"]))

        else:
            cur.execute("""
                INSERT INTO scores (username, buyer, score, money, time)
                VALUES (?, ?, ?, ?, ?)
            """, (data["username"], data["buyer"], data["score"], data["money"], now))

    return {"status": "ok"}, 200

# Получить топ-10 по деньгам
@app.route("/top", methods=["GET"])
def get_top():
    with sqlite3.connect("scores.db") as conn:
        result = conn.execute("""
            SELECT username, money
            FROM scores
            ORDER BY money DESC
            LIMIT 10
        """).fetchall()
    return jsonify(result)

# Главная страница с таблицей
@app.route("/")
def index():
    with sqlite3.connect("scores.db") as conn:
        result = conn.execute("""
            SELECT username, money, score
            FROM scores
            ORDER BY money DESC
        """).fetchall()

    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Miga: Таблица рекордов</title>
        <style>
            body {
                font-family: sans-serif;
                background: #f3f3f3;
                text-align: center;
                padding: 40px;
            }
            h1 {
                color: #333;
                margin-bottom: 10px;
            }
            h2 {
                color: #666;
                margin-bottom: 30px;
            }
            table {
                margin: 0 auto;
                border-collapse: collapse;
                width: 70%;
                background: white;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }
            th, td {
                padding: 12px;
                border: 1px solid #ccc;
            }
            th {
                background-color: #ddd;
            }
            tr:nth-child(even) {
                background-color: #f9f9f9;
            }
        </style>
    </head>
    <body>
        <h1>Miga: Рыбный Бизнес</h1>
        <h2>Таблица рекордов</h2>
        <table>
            <tr><th>№</th><th>Игрок</th><th>Всего заработано (₽)</th><th>Макс. рыбы</th></tr>
    """

    for i, (username, money, score) in enumerate(result, 1):
        html += f"<tr><td>{i}</td><td>{username}</td><td>{money}</td><td>{score}</td></tr>"

    html += """
        </table>
    </body>
    </html>
    """
    return html

# Запуск сервера
if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=8000)
