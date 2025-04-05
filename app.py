from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import os
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'clave_secreta_segura'

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Flask-Login setup
login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

# User class
class User(UserMixin):
    def __init__(self, id):
        self.id = id

# Hardcoded user
USERS = {
    "admin": {"password": "psicologia123"}
}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

# Database setup
DB_FILE = 'blog.db'

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS posts (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            title TEXT NOT NULL,
                            content TEXT NOT NULL,
                            image TEXT,
                            video TEXT
                        )''')

init_db()

# Routes
@app.route('/')
def index():
    with sqlite3.connect(DB_FILE) as conn:
        posts = conn.execute('SELECT * FROM posts ORDER BY id DESC').fetchall()
    return render_template('index.html', posts=posts)

@app.route('/post/<int:post_id>')
def post(post_id):
    with sqlite3.connect(DB_FILE) as conn:
        post = conn.execute('SELECT * FROM posts WHERE id=?', (post_id,)).fetchone()
    return render_template('post.html', post=post)

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        video = request.form['video']

        image_file = request.files['image']
        image_filename = ''

        if image_file and image_file.filename:
            image_filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], image_filename))

        with sqlite3.connect(DB_FILE) as conn:
            conn.execute('INSERT INTO posts (title, content, image, video) VALUES (?, ?, ?, ?)',
                         (title, content, image_filename, video))
        return redirect(url_for('index'))

    return render_template('upload.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in USERS and USERS[username]['password'] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for('index'))
        else:
            error = 'Credenciales inválidas'
    return render_template('login.html', error=error)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
    app.run(debug=True)
