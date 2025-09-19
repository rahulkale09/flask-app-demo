from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime



app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)

#login manager setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

#user model
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)


#Database model
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect("/")
        else:
            return "Invalid credentials"
    return render_template("login.html")
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/login')

@app.route("/", methods=['GET'])
@login_required
def home():
    notes = Note.query.all()
    return render_template('home.html', notes=notes)

@app.route("/about")
@login_required
def about():
    return render_template("about.html")

@app.route("/add-note", methods=['POST'])
@login_required
def add_note():
    content = request.form['content']
    if content:
        new_note = Note(content=content)
        db.session.add(new_note)
        db.session.commit()
    return redirect("/")

@app.route("/delete-note/<int:id>")
@login_required
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        if not User.query.filter_by(username="admin").first():
            new_user = User(username = "admin", password = "password")
            db.session.add(new_user)
            db.session.commit()
    app.run(debug=True)

