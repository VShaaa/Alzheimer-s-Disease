from flask import Flask, render_template, request, redirect,session, url_for
from flask_cors import CORS, cross_origin
import os
import secrets
import sqlite3


os.putenv('LANG', 'en_US.UTF-8')
os.putenv('LC_ALL', 'en_US.UTF-8')

app = Flask(__name__)
CORS(app)



app.config['SECRET_KEY'] = secrets.token_hex(16)
# Function to connect to SQLite database
def connect_db():
    conn = sqlite3.connect('users.db')
    return conn

# Function to create users table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            mobile TEXT NOT NULL,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            address TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert a new user into the database
def insert_user(name, email, mobile, username, password, address):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (name, email, mobile, username, password, address) 
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (name, email, mobile, username, password, address))
    conn.commit()
    conn.close()

# Function to authenticate user login
def authenticate_user(username, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? AND password = ?
    ''', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user

def user_exists(username):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE username = ? 
    ''', (username,))
    user = cursor.fetchall()
    conn.close()
    return user


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        mobile = request.form['mobile']
        username = request.form['username']
        password = request.form['password']
        address = request.form['address']

        # Check if user already exists
        if user_exists(username):
            error_message = 'Username already exists. Please choose a different username.'
            return render_template('register.html', error_message=error_message)

        # Insert user into the database
        insert_user(name, email, mobile, username, password, address)
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['login_username']
        password = request.form['login_password']

        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user[0]
            session['name'] = user[1]
            return redirect('http://localhost:8501/')
        else:
            error_message = 'Invalid username or password.'
            return render_template('login.html', error_message=error_message)
    return render_template('login.html')

@app.route("/admin_login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        first_name = request.form.get("login_username")
        last_name = request.form.get("login_password") 
        if first_name == 'admin' and last_name == 'admin':
            return redirect("/users")
    else:
        return render_template("admin.html")
    return render_template("admin.html")
@app.route('/users')
def users():
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, mobile, username, password, address FROM users')
    users = cursor.fetchall()
    return render_template('users.html', users=users)
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('name', None)
    return redirect(url_for('login'))
if __name__ == "__main__":
    create_table()
    app.run()