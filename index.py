import os.path
from werkzeug.security import generate_password_hash, check_password_hash

from flask import render_template, redirect, url_for, Flask, request, jsonify
from models.Book import db, Book
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models.User import User

app = Flask(__name__, template_folder=os.path.abspath('/home/saber/flaskProject/templates'))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Use your actual database URI
app.config['SECRET_KEY'] = 'asdfhj0843hyfoqjfrfu9054ore'
db.init_app(app)

with app.app_context():
    db.create_all()

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.form
        new_user = User(name=data['name'], email=data['email'])
        new_user.set_password(data['password'])
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        user = User.query.filter_by(email=data['email']).first()
        if user and user.check_password(data['password']):
            login_user(user)
            return redirect(url_for('get_books'))
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/books', methods=['GET'])
@login_required
def get_books():
    books = Book.query.all()
    return render_template('books/index.html', books=books)


@app.route('/books/store', methods=['POST'])
@login_required
def add_book():
    if request.method == 'POST':
        data = request.form
        new_book = Book(title=data['title'], author=data['author'], publication_year=data['publication_year'],
                        language=data['language'])
        db.session.add(new_book)
        db.session.commit()
        return redirect(url_for('get_books'))

@app.route('/books/new', methods=['GET'])
@login_required
def new_book():
    return render_template('books/create.html')

@app.route('/books/<int:id>', methods=['GET'])
@login_required
def get_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    return render_template('books/show.html', book=book)

@app.route('/books/edit/<int:id>', methods=['GET'])
@login_required
def edit_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    return render_template('books/edit.html', book=book)

@app.route('/books/update/<int:id>', methods=['POST'])
@login_required
def update_book(id):
    # Accept the form request
    data = request.form
    book = Book.query.get(id)
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    book.title = data['title']
    book.author = data['author']
    book.publication_year = data['publication_year']
    book.language = data['language']
    db.session.commit()
    return redirect(url_for('get_books'))


@app.route('/books/delete/<int:id>', methods=['GET'])
@login_required
def delete_book(id):
    book = Book.query.get(id)
    if book is None:
        return jsonify({'message': 'Book not found'}), 404
    db.session.delete(book)
    db.session.commit()
    return redirect(url_for('get_books'))
