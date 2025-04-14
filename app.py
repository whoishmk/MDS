import sqlite3
from flask import Flask, request, session, redirect, url_for, render_template, flash
from passlib.hash import bcrypt

app = Flask(__name__)
app.secret_key = 'REPLACE_WITH_A_SECURE_RANDOM_KEY'  # Replace with something more secure in production

DATABASE = 'database.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    # Return rows as dictionaries instead of tuples for convenience
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """
    Home page route. Shows a welcome message if logged in,
    else prompts user to either log in or register.
    """
    if 'username' in session:
        return render_template('index.html', username=session['username'])
    return render_template('index.html', username=None)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """
    Registration page route. Creates a new user in the database
    if username does not exist.
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        if not username or not password:
            flash("Username and password cannot be empty.")
            return redirect(url_for('register'))

        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # Check if username already exists
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            existing_user = cursor.fetchone()
            if existing_user:
                flash("Username already taken. Please choose another.")
                return redirect(url_for('register'))

            # Hash the password
            password_hash = bcrypt.hash(password)

            # Insert new user into DB
            cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                           (username, password_hash))
            conn.commit()
            flash("Successfully registered. Please log in.")
            return redirect(url_for('login'))
        finally:
            conn.close()

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    Login page route. Checks username/password. If correct, stores
    username in session and redirects to index.
    """
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']

        conn = get_db_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
            user = cursor.fetchone()
        finally:
            conn.close()

        if user:
            stored_password_hash = user['password_hash']
            if bcrypt.verify(password, stored_password_hash):
                # Store username in session
                session['username'] = user['username']
                flash("Logged in successfully.")
                return redirect(url_for('index'))
            else:
                flash("Incorrect password.")
        else:
            flash("No user found with that username.")

        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    """
    Logs the user out by clearing the session.
    """
    session.pop('username', None)
    flash("You have been logged out.")
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
