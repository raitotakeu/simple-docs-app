from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from extensions import db
from models import User, Document

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Database configuration (SQLite)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Home route
@app.route('/')
def index():
    if 'user_id' in session:
        user_id = session['user_id']
        user_documents = Document.query.filter_by(user_id=user_id).all()
        return render_template('index.html', user_documents=user_documents, logged_in=True)
    return render_template('index.html', logged_in=False)

# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('Username already exists!')
            return redirect('/register')
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html')

# Login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            session['username'] = user.username
            return redirect('/')
        flash('Invalid credentials')
    return render_template('login.html')

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# Dashboard
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect('/login')
    user_id = session['user_id']
    user_documents = Document.query.filter_by(user_id=user_id).all()
    return render_template('dashboard.html', documents=user_documents)

# Create document
@app.route('/create', methods=['GET', 'POST'])
def create():
    if 'user_id' not in session:
        return redirect('/login')
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        new_doc = Document(title=title, content=content, user_id=session['user_id'])
        db.session.add(new_doc)
        db.session.commit()
        return redirect('/dashboard')
    return render_template('create.html')

# Edit document
@app.route('/edit/<int:doc_id>', methods=['GET', 'POST'])
def edit(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        return redirect('/dashboard')
    if request.method == 'POST':
        doc.title = request.form['title']
        doc.content = request.form['content']
        db.session.commit()
        return redirect('/dashboard')
    return render_template('edit.html', document=doc)

# Delete document
@app.route('/delete/<int:doc_id>')
def delete(doc_id):
    if 'user_id' not in session:
        return redirect('/login')
    doc = Document.query.get_or_404(doc_id)
    if doc.user_id != session['user_id']:
        return redirect('/dashboard')
    db.session.delete(doc)
    db.session.commit()
    return redirect('/dashboard')

# Create DB and run server
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run()
