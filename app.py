from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Database initialization
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT)''')
c.execute('''CREATE TABLE IF NOT EXISTS problems (id INTEGER PRIMARY KEY, problem_text TEXT, solved BOOLEAN)''')
conn.commit()
conn.close()

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (email, password) VALUES (?, ?)', (email, password))
            conn.commit()
            conn.close()
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            conn.close()
            return 'Email already exists. Please use a different email.'
    return render_template('register.html')


if __name__ == '__main__':
    app.run(debug=True)
