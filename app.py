from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# --------------------------
# Config
# --------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///rehab.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

# --------------------------
# Login manager setup
# --------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# --------------------------
# MODELS
# --------------------------
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password, method="pbkdf2:sha256")

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class RehabLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    exercise = db.Column(db.String(100), nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    sets = db.Column(db.Integer, nullable=True)
    pain_level = db.Column(db.Integer, nullable=True)  # scale 1–10
    notes = db.Column(db.String(200))
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))

# --------------------------
# User loader
# --------------------------
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --------------------------
# ROUTES
# --------------------------
@app.route("/")
def index():
    return render_template("index.html")  # Public landing page


@app.route("/dashboard")
@login_required
def home():
    logs = RehabLog.query.filter_by(user_id=current_user.id).all()
    return render_template('home.html', logs=logs)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        if User.query.filter_by(username=username).first():
            return "User already exists"

        new_user = User(username=username)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        # Automatically log in after registration
        login_user(new_user)
        return redirect('/dashboard')

    return render_template("register.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            login_user(user)
            return redirect("/dashboard")
        else:
            return "Invalid credentials"

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.route("/add-log", methods=['POST'])
@login_required
def add_log():
    exercise = request.form.get('exercise')
    reps = request.form.get('reps')
    sets = request.form.get('sets')
    pain_level = request.form.get('pain_level')
    notes = request.form.get('notes')

    if exercise:
        new_log = RehabLog(
            user_id=current_user.id,
            exercise=exercise,
            reps=int(reps) if reps else None,
            sets=int(sets) if sets else None,
            pain_level=int(pain_level) if pain_level else None,
            notes=notes
        )
        db.session.add(new_log)
        db.session.commit()

    return redirect("/dashboard")


@app.route("/delete-log/<int:id>")
@login_required
def delete_log(id):
    log = RehabLog.query.get_or_404(id)
    if log.user_id == current_user.id:  # prevent deleting others' logs
        db.session.delete(log)
        db.session.commit()
    return redirect("/dashboard")


@app.route("/about")
def about():
    return render_template("about.html")


# --------------------------
# MAIN
# --------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(host="0.0.0.0", port=5000, debug=True)
