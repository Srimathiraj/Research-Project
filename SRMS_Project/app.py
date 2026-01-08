from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "secretkey123"

# ---------------- DATABASE ----------------
def get_db():
    return sqlite3.connect("database.db")

def create_tables():
    db = get_db()

    db.execute("""
        CREATE TABLE IF NOT EXISTS faculty (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)

    db.execute("""
        CREATE TABLE IF NOT EXISTS supervisor (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            faculty_name TEXT,
            department TEXT,
            university TEXT,
            recognition_no TEXT UNIQUE,
            recognition_date TEXT,
            specialization TEXT
        )
    """)

    db.execute("""
        INSERT OR IGNORE INTO faculty (username, password)
        VALUES ('faculty1', 'faculty123')
    """)

    db.commit()

create_tables()

# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        db = get_db()
        user = db.execute(
            "SELECT * FROM faculty WHERE username=? AND password=?",
            (username, password)
        ).fetchone()

        if user:
            session["user"] = username
            return redirect("/")
        else:
            return render_template("login.html", error="Invalid Username or Password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")


# ---------------- DASHBOARD ----------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect("/login")

    db = get_db()
    data = db.execute("SELECT * FROM supervisor").fetchall()
    return render_template("index.html", data=data)


# ---------------- ADD SUPERVISOR ----------------
@app.route("/add", methods=["GET", "POST"])
def add():
    if "user" not in session:
        return redirect("/login")

    if request.method == "POST":
        try:
            db = get_db()
            db.execute("""
                INSERT INTO supervisor
                (faculty_name, department, university, recognition_no, recognition_date, specialization)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                request.form["faculty_name"],
                request.form["department"],
                request.form["university"],
                request.form["recognition_no"],
                request.form["recognition_date"],
                request.form["specialization"]
            ))
            db.commit()
            return redirect("/")
        except sqlite3.IntegrityError:
            return "Recognition Number already exists!"

    return render_template("add.html")


# ---------------- DELETE ----------------
@app.route("/delete/<int:id>")
def delete(id):
    if "user" not in session:
        return redirect("/login")

    db = get_db()
    db.execute("DELETE FROM supervisor WHERE id=?", (id,))
    db.commit()
    return redirect("/")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)
