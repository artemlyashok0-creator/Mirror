import sqlite3
from flask import Flask, jsonify, request, send_from_directory

app = Flask(__name__, static_folder=".")


def get_db():
  conn = sqlite3.connect("mirror.db")
  conn.row_factory = sqlite3.Row
  return conn


def init_db():
  with get_db() as db:
    db.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender TEXT,
                text TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
    db.commit()


init_db()


@app.route("/")
def index():
  return send_from_directory(".", "index.html")


@app.route("/messages", methods=["GET"])
def get_messages():
  with get_db() as db:
    cursor = db.execute(
        "SELECT sender, text, timestamp FROM messages ORDER BY id ASC"
    )
    messages = [dict(row) for row in cursor.fetchall()]
  return jsonify(messages)


@app.route("/messages", methods=["POST"])
def post_message():
  data = request.json
  sender = data.get("sender", "Anonym")
  text = data.get("text", "")

  if not text.strip():
    return jsonify({"error": "Empty message"}), 400

  with get_db() as db:
    db.execute(
        "INSERT INTO messages (sender, text) VALUES (?, ?)", (sender, text)
    )
    db.commit()

  return jsonify({"status": "success"})


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=5000, debug=True)
