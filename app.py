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


if __name__ == '__main__':
    app.run(debug=True)
