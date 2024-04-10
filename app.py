from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)

def create_database_with_problems():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, email TEXT UNIQUE, password TEXT, is_admin INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS problems (id INTEGER PRIMARY KEY, title TEXT, description TEXT, difficulty TEXT, input_examples TEXT, output_examples TEXT, test_input TEXT, test_output TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS submissions (id INTEGER PRIMARY KEY, user_id INTEGER, problem_id INTEGER, code TEXT, result TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Check if the admin account exists, if not, create it
    c.execute("SELECT * FROM users WHERE email='admin@example.com'")
    admin_exists = c.fetchone()
    if not admin_exists:
        c.execute("INSERT INTO users (email, password, is_admin) VALUES ('admin@example.com', 'admin_password', 1)")

    # Check if problems exist, if not, create some sample problems


    conn.commit()
    conn.close()

create_database_with_problems()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM users WHERE email=? AND password=?', (email, password))
        user = c.fetchone()
        conn.close()
        if user:
            session['email'] = email
            session['is_admin'] = user[3]
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email/password. Please try again.', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        try:
            c.execute('INSERT INTO users (email, password, is_admin) VALUES (?, ?, ?)', (email, password, 0))
            conn.commit()
            conn.close()
            flash('Registration successful. Please log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists. Please use a different email.', 'error')
            conn.close()
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'email' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM problems")
        problems = c.fetchall()
        conn.close()
        if session['is_admin']:
            return render_template('admin_dashboard.html', problems=problems)
        else:
            return render_template('user_dashboard.html', problems=problems)
    return redirect(url_for('login'))

@app.route('/add_problem', methods=['GET', 'POST'])
def add_problem():
    if 'email' in session and session['is_admin']:
        if request.method == 'POST':
            title = request.form['title']
            description = request.form['description']
            difficulty = request.form['difficulty']
            input_examples = request.form['input_examples']
            output_examples = request.form['output_examples']
            test_input_file = request.files['test_input']
            test_output_file = request.files['test_output']
            
            # Save uploaded files
            test_input_filename = os.path.join(app.config['UPLOAD_FOLDER'], test_input_file.filename)
            test_input_file.save(test_input_filename)
            test_output_filename = os.path.join(app.config['UPLOAD_FOLDER'], test_output_file.filename)
            test_output_file.save(test_output_filename)
            
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO problems (title, description, difficulty, input_examples, output_examples, test_input, test_output) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                    (title, description, difficulty, input_examples, output_examples, test_input_filename, test_output_filename))
            conn.commit()
            conn.close()
            
            flash('Problem added successfully', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('add_problem.html')
    else:
        flash('You need to log in as admin to add a problem.', 'error')
        return redirect(url_for('login'))
    
@app.route('/problems')
def problems():
    if 'email' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM problems')
        problems = c.fetchall()
        conn.close()
        return render_template('problems.html', problems=problems)
    return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
