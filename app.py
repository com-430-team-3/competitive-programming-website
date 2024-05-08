from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
import subprocess

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.config['UPLOAD_FOLDER'] = 'uploads'  # Add this line to configure the upload folder

# Function to check the correctness of the code
def check_code(input_file_path, output_data, code, language):
    # Read input data from file
    with open(input_file_path, 'r') as input_file:
        input_data = input_file.read()

    with open(output_data, 'r') as output_file:
        output_data = output_file.read()

    # Print the type and content of input data
    print("Input data type:", type(input_data))
    print("Input data content:", input_data)

    print("OUT data type:", type(output_data))
    print("OUT data content:", output_data)

    # Execute the code
    if language == "C++":
        compile_process = subprocess.Popen(['g++', '-o', 'temp', '-x', 'c++', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        compile_stdout, compile_stderr = compile_process.communicate(input=code)
        if compile_stderr:
            return "Compilation Error: " + compile_stderr

        execute_process = subprocess.Popen(['./temp'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        execute_stdout, execute_stderr = execute_process.communicate(input=input_data)
    elif language == "Python":
        execute_process = subprocess.Popen(['python3', '-c', code], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        execute_stdout, execute_stderr = execute_process.communicate(input=input_data)
    else:
        return "Unsupported language"

    print("execute_stdout")
    print(execute_stdout)
    if execute_stderr:
        return "Runtime Error: " + execute_stderr

    print("RES")
    print(execute_stdout.strip())
    print("OUT")
    print(output_data.strip())
    # Compare output
    if execute_stdout.strip() == output_data.strip():
        return "Accepted"
    else:
        return "Wrong Answer"



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

@app.route('/delete_problem/<int:problem_id>', methods=['POST'])
def delete_problem(problem_id):
    if 'email' in session and session['is_admin']:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("DELETE FROM problems WHERE id=?", (problem_id,))
        conn.commit()
        conn.close()
        flash('Problem deleted successfully', 'success')
    return redirect(url_for('dashboard'))

@app.route('/problem_submissions/<int:problem_id>')
def problem_submissions(problem_id):
    if 'email' in session and session['is_admin']:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Query submissions for this problem
        c.execute('SELECT submissions.id, users.email, submissions.code, submissions.result, submissions.timestamp FROM submissions INNER JOIN users ON submissions.user_id = users.id WHERE problem_id = ?', (problem_id,))
        submissions = c.fetchall()
        conn.close()

        return render_template('problem_submissions.html', submissions=submissions)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('email', None)
    session.pop('is_admin', None)
    return redirect(url_for('login'))

@app.route('/view_problem/<int:problem_id>', methods=['GET', 'POST'])
def view_problem(problem_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM problems WHERE id = ?', (problem_id,))
    problem = c.fetchone()

    if request.method == 'POST':
        solution = request.form['solution']
        language = request.form['language']
        
        # Get problem's test input and output
        test_input = problem[6]
        test_output = problem[7]
        
        print("TESTS")
        print(test_input)
        print(test_output)
        # Check the correctness of the code
        result = check_code(test_input, test_output, solution, language)
            # Get user id
        c.execute('SELECT id FROM users WHERE email=?', (session['email'],))
        user_id = c.fetchone()[0]

        # Insert submission into database
        c.execute("INSERT INTO submissions (user_id, problem_id, code, result) VALUES (?, ?, ?, ?)", (user_id, problem_id, solution, result))
        conn.commit()
        conn.close()

        return render_template('view_problem.html', problem=problem, result=result)

    return render_template('view_problem.html', problem=problem)


@app.route('/user_submissions/<int:problem_id>')
def user_submissions(problem_id):
    if 'email' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        # Get user id
        c.execute('SELECT id FROM users WHERE email=?', (session['email'],))
        user_id = c.fetchone()[0]

        # Query submissions for this problem by this user
        c.execute('SELECT * FROM submissions WHERE problem_id = ? AND user_id = ?', (problem_id, user_id))
        submissions = c.fetchall()
        conn.close()

        return render_template('user_submissions.html', submissions=submissions, email=session['email'])
    return redirect(url_for('login'))

@app.route('/submission_history')
def submission_history():
    if 'email' in session:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT id FROM users WHERE email=?', (session['email'],))
        user_id = c.fetchone()[0]
        c.execute('SELECT * FROM submissions WHERE user_id=? ORDER BY timestamp DESC', (user_id,))
        submissions = c.fetchall()
        conn.close()
        return render_template('submission_history.html', submissions=submissions)
    return redirect(url_for('login'))

@app.route('/admin/submissions')
def admin_submissions():
    if 'email' in session and session['is_admin']:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute('SELECT * FROM submissions ORDER BY timestamp DESC')
        submissions = c.fetchall()
        conn.close()
        return render_template('admin_submissions.html', submissions=submissions)
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

@app.route('/submission/<int:submission_id>')
def view_submission(submission_id):
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute('SELECT * FROM submissions WHERE id = ?', (submission_id,))
    submission = c.fetchone()
    conn.close()
    return render_template('view_submission.html', code=submission[3])

@app.route('/admin/edit_problem/<int:problem_id>', methods=['GET', 'POST'])
def edit_problem(problem_id):
    if 'email' in session and session['is_admin']:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()

        if request.method == 'POST':
            # Get updated problem data from form
            title = request.form['title']
            description = request.form['description']
            difficulty = request.form['difficulty']
            input_examples = request.form['input_examples']
            output_examples = request.form['output_examples']

            # Update problem in database
            c.execute('UPDATE problems SET title=?, description=?, difficulty=?, input_examples=?, output_examples=? WHERE id=?', 
                    (title, description, difficulty, input_examples, output_examples, problem_id))
            conn.commit()

            flash('Problem updated successfully', 'success')
            return redirect(url_for('dashboard'))

        # Query problem data for the form
        c.execute('SELECT * FROM problems WHERE id = ?', (problem_id,))
        problem = c.fetchone()
        conn.close()

        return render_template('edit_problem.html', problem=problem)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
