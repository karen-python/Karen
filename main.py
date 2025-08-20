from flask import Flask, render_template, g, request, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)

DATABASE = "sqlite.db"
app.config['SECRET_KEY'] = 'KKA_135_246'

login_manager = LoginManager(app)
login_manager.login_view = 'login'

connection = sqlite3.connect("sqlite.db", check_same_thread=False)


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    cursor = db.cursor()
    user = cursor.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    if user is not None:
        return User(user[0], user[1], user[2])
    return None


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
    return g.db


@app.teardown_appcontext
def close_connection(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()


@app.route("/")
def hello():
    return "Введи в адресной строке название страницы"


@app.route("/blog/")
def blog():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('''SELECT post.id, post.title, post.content, post.author_id, user.username, 
                COUNT(like.id) AS likes  FROM post
    JOIN user ON post.author_id = user.id
    LEFT JOIN like ON post.id = like.post_id
    GROUP BY post.id, post.title,post.author_id, post.content, user.username''')

    cursor.execute('SELECT * FROM post JOIN user ON post.author_id = user.id')
    result = cursor.fetchall()

    posts = []
    for post in reversed(result):
        posts.append({
            'id': post[0],
            'title': post[1],
            'content': post[2],
            'author_id': post[3],
            'username': post[4],
            'likes': post[5]
        })

        if current_user.is_authenticated:
            cursor.execute('SELECT post_id FROM like WHERE user_id = ?', (current_user.id,))
            likes_result = cursor.fetchall()
            liked_posts = []
            for like in likes_result:
                liked_posts.append(like[0])
            posts[-1]['liked_posts'] = liked_posts
    context = {'posts': posts}
    return render_template('blog.html', **context)


@app.route("/add/", methods=["GET", "POST"])
@login_required
def add_post():
    if request.method == "POST":
        title = request.form["title"]
        content = request.form["content"]
        db = get_db()
        cursor = db.cursor()
        cursor.execute(
            'INSERT INTO post (title, content, author_id) VALUES (?, ?, ?)',
            (title, content, current_user.id)
        )
        db.commit()
        return redirect(url_for("blog"))
    return render_template("add_posts.html")


@app.route("/register/", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        db = get_db()
        cursor = db.cursor()
        try:
            cursor.execute('INSERT INTO user (username, password_hash, email) VALUES(?, ?, ?)',
                           (username, generate_password_hash(password), email))
            db.commit()
            print("Регистрация пользователя прошла успешно")
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            print("Username already exists!")
    return render_template('register.html')


@app.route('/posts/<post_id>')
def post(post_id):
    db = get_db()
    cursor = db.cursor()
    result = cursor.execute(
        'SELECT * from post WHERE id = ?', (post_id,)
    ).fetchone()
    post_dict = {'id': result[0], 'title': result[1], 'content': result[2]}
    return render_template('post.title.html', post=post_dict)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        cursor = db.cursor()
        user = cursor.execute('SELECT * FROM user WHERE username = ?', (username,)).fetchone()
        if user and User(user[0], user[1], user[2]).check_password(password):
            login_user(User(user[0], user[1], user[2]))
            return redirect(url_for('blog'))
        else:
            return render_template('login.html', message='Invalid username or password')
    return render_template('login.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('blog'))


@app.route('/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    db = get_db()
    cursor = db.cursor()
    post = cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    if post and post[3] == current_user.id:
        cursor.execute('DELETE FROM post WHERE id = ?', (post_id,))
        return redirect(url_for('blog'))
    else:
        return redirect(url_for('blog'))


def user_is_liking(user_id, post_id):
    db = get_db()
    cursor = db.cursor()
    like = cursor.execute(
        'SELECT * FROM like WHERE user_id = ? AND post_id = ?',
        (user_id, post_id)).fetchone()
    return bool(like)


@app.route('/like/<int:post_id>')
@login_required
def like_post(post_id):
    db = get_db()
    cursor = db.cursor()
    post = cursor.execute('SELECT * FROM post WHERE id = ?', (post_id,)).fetchone()
    if post:
        if user_is_liking(current_user.id, post_id):
            cursor.execute(
                'DELETE FROM like WHERE user_id = ? AND post_id',
                (current_user.id, post_id))
            connection.commit()
            print('You unliked post.')
    else:
        cursor.execute(
            'INSERT INTO like (user_id, post_id) VALUES (?, ?)',
            (current_user.id, post_id))
        connection.commit()
        print('You liked this post!')


    return redirect(url_for('blog'))
    return 'Post not found', 404

if __name__ == "__main__":
    app.run(debug=True)
