from flask import Flask, render_template, request
import sqlite3
import os

# Adjust template/static paths for Vercel
app = Flask(__name__, template_folder="../templates", static_folder="../static")

# Database setup (⚠️ Vercel serverless resets between runs, so use external DB in production)
db_path = os.path.join(os.path.dirname(__file__), "../database.db")

def init_db():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("DROP TABLE IF EXISTS jobs")
    c.execute("""CREATE TABLE jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    prediction TEXT,
                    keyword TEXT
                )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    keyword = None

    if request.method == "POST":
        job_desc = request.form.get("job_desc", "")

        # Simple keyword-based fake job detection
        suspicious_keywords = ["money", "$", "earn", "fast", "guaranteed", "investment"]
        for word in suspicious_keywords:
            if word in job_desc.lower():
                result = "Fake Job"
                keyword = word
                break

        if not result:
            result = "Real Job"

        # Save to DB
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        c.execute("INSERT INTO jobs (description, prediction, keyword) VALUES (?, ?, ?)",
                  (job_desc, result, keyword))
        conn.commit()
        conn.close()

    return render_template("index.html", result=result, keyword=keyword)

@app.route("/history")
def history():
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute("SELECT description, prediction, keyword FROM jobs ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()
    return render_template("history.html", jobs=rows)

# Vercel looks for 'app'
if __name__ == "__main__":
    app.run()
