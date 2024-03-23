from flask import Flask, render_template, redirect, url_for, session, flash, request
from flask_sqlalchemy import SQLAlchemy 
from datetime import timedelta, datetime

app = Flask(__name__)
app.secret_key = "hello"
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///Base.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.permanent_session_lifetime = timedelta(minutes=5)

db = SQLAlchemy(app)

class Info(db.Model):
    id = db.Column("id", db.Integer, primary_key = True)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    
    def __init__(self, username, email):
        self.username = username
        self.email = email
        
class Task(db.Model):
    id1 = db.Column("id1", db.Integer, primary_key = True)
    taskname = db.Column(db.String(100), nullable=False)
    created_at = db. Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    def __init__(self, taskname, created_at):
        self.taskname = taskname

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        session.permanent = True
        username = request.form["name"]
        email = request.form["email"]
        session["username"] = username
        session["email"] = email
        
        flash(f"Hello {username}, you are connected !")
        return redirect(url_for("user"))
    else:
        if "username" in session:
            flash("Already connected.")
            return redirect(url_for("user"))
    return render_template("login.html")

@app.route("/user")
def user():
    if "username" in session:
        return render_template("user.html")
    return redirect(url_for("login"))

@app.route("/tache", methods = ["GET", "POST"])
def tache():
    if request.method == "POST":
        taskname = request.form["tache"]
        created_at = datetime.utcnow()
        new = Task(taskname=taskname, created_at=created_at)
        try:
            db.session.add(new)
            db.session.commit()
            return redirect(url_for("tache"))
        except Exception:
            return "Une erreur s'est produite"
    tasks = Task.query.order_by(Task.created_at)
    return render_template("tache.html", tasks=tasks)

@app.route("/update/<int:id1>/", methods = ["GET", "POST"])
def update(id1):
    tasks = Task.query.get_or_404(id1)
    if request.method == "POST":
        tasks.taskname = request.form["tache"]
        try:
            db.session.commit()
            return redirect(url_for("tache"))
        except Exception:
            return "Une erreur s'est produite"
    return render_template("update.html", tasks = tasks)

@app.route("/delete/<int:id1>/")
def delete(id1):
    tasks = Task.query.get_or_404(id1)
    try:
        db.session.delete(tasks)
        db.session.commit()
        return redirect(url_for("tache"))
    except Exception:
        return "Une erreur s'est produite"
    return redirect(url_for("tache"))

@app.route("/logout")
def logout():
    if "username" in session:
        username = session["username"]
        email = session["email"]
        flash("You have been logged out.", "info")
        session.pop("username", None)
        session.pop("email", None)
        return redirect_with_delay("login", delay_seconds=3)  # Redirect with delay
    return render_template("login.html")

def redirect_with_delay(endpoint, delay_seconds):
    return f"""
        <script>
            setTimeout(function() {{
                window.location.href = "{url_for(endpoint)}";
            }}, {delay_seconds * 1000});
        </script>
        Redirecting...
    """

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug = True)