"""
Intentionally vulnerable practice app for a beginner SQL injection challenge.
The flag is injected via the FLAG environment variable at container start —
never hardcoded into the image.
"""
import os
import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
FLAG = os.environ.get("FLAG", "CTF{missing_flag_env_var}")

import tempfile
DB_PATH = os.path.join(tempfile.gettempdir(), "users.db")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("CREATE TABLE IF NOT EXISTS users (username TEXT, password TEXT)")
    conn.execute("DELETE FROM users")
    conn.execute("INSERT INTO users VALUES ('admin', 'S3cur3P@ss!')")
    conn.commit()
    conn.close()

PAGE = """
<h2>Staff Login</h2>
<form method="post">
  Username: <input name="username"><br>
  Password: <input name="password" type="password"><br>
  <input type="submit" value="Login">
</form>
{% if message %}<p>{{ message }}</p>{% endif %}
"""

@app.route("/", methods=["GET", "POST"])
def login():
    message = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Intentionally vulnerable: string-built query, no parameterization.
        # This is the bug the player is meant to find and exploit.
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"

        conn = sqlite3.connect(DB_PATH)
        try:
            cursor = conn.execute(query)
            row = cursor.fetchone()
        except sqlite3.Error as e:
            row = None
            message = f"DB error: {e}"
        conn.close()

        if row:
            message = f"Welcome, {row[0]}! Flag: {FLAG}"
        elif not message:
            message = "Invalid credentials."

    return render_template_string(PAGE, message=message)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
