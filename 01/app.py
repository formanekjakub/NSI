from flask import Flask, render_template, request, redirect, url_for, session
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "ShellNotPass"

# Simple in-memory "database" of users:
USERS = {
    # "username": "hashed_password"
}

# saved data
DATA=[
    {"id": 0,"temperature": 21,"timestamp": "2025-01-01 01:00:00"},
    {"id": 1,"temperature": 33,"timestamp": "2025-01-01 01:05:52"},
    {"id": 2,"temperature": 38,"timestamp": "2025-01-01 01:10:23"},
    {"id": 3,"temperature": 21,"timestamp": "2025-01-01 01:15:17"},
    {"id": 4,"temperature": 24,"timestamp": "2025-01-01 01:20:08"},
    {"id": 5,"temperature": 35,"timestamp": "2025-01-01 01:25:42"},
    {"id": 6,"temperature": 40,"timestamp": "2025-01-01 01:30:00"},
    {"id": 7,"temperature": 37,"timestamp": "2025-01-01 01:35:19"},
    {"id": 8,"temperature": 37,"timestamp": "2025-01-01 01:40:25"},
    {"id": 9,"temperature": 20,"timestamp": "2025-01-01 01:45:53"},
    {"id": 10,"temperature": 35,"timestamp": "2025-01-01 01:50:15"},
    {"id": 11,"temperature": 34,"timestamp": "2025-01-01 01:55:19"},
    {"id": 12,"temperature": 28,"timestamp": "2025-01-01 02:00:46"},
    {"id": 13,"temperature": 23,"timestamp": "2025-01-01 02:05:55"},
    {"id": 14,"temperature": 25,"timestamp": "2025-01-01 02:10:20"},
    {"id": 15,"temperature": 23,"timestamp": "2025-01-01 02:15:43"},
    {"id": 16,"temperature": 23,"timestamp": "2025-01-01 02:20:52"},
    {"id": 17,"temperature": 31,"timestamp": "2025-01-01 02:25:47"},
    {"id": 18,"temperature": 29,"timestamp": "2025-01-01 02:30:35"},
    {"id": 19,"temperature": 31,"timestamp": "2025-01-01 02:35:52"},
    {"id": 20,"temperature": 35,"timestamp": "2025-01-01 02:40:28"},
    {"id": 21,"temperature": 26,"timestamp": "2025-01-01 02:45:53"},
    {"id": 22,"temperature": 35,"timestamp": "2025-01-01 02:50:50"},
    {"id": 23,"temperature": 28,"timestamp": "2025-01-01 02:55:56"},
    {"id": 24,"temperature": 39,"timestamp": "2025-01-01 03:00:31"},
    {"id": 25,"temperature": 36,"timestamp": "2025-01-01 03:05:56"},
    {"id": 26,"temperature": 39,"timestamp": "2025-01-01 03:10:40"},
    {"id": 27,"temperature": 23,"timestamp": "2025-01-01 03:15:47"},
    {"id": 28,"temperature": 31,"timestamp": "2025-01-01 03:20:11"},
    {"id": 29,"temperature": 21,"timestamp": "2025-01-01 03:25:43"},
    {"id": 30,"temperature": 23,"timestamp": "2025-01-01 03:30:58"},
    {"id": 32,"temperature": 28,"timestamp": "2025-01-01 03:35:51"},
    {"id": 31,"temperature": 29,"timestamp": "2025-01-01 03:40:46"},
    {"id": 33,"temperature": 31,"timestamp": "2025-01-01 03:45:38"},
    {"id": 34,"temperature": 40,"timestamp": "2025-01-01 03:50:09"},
    {"id": 35,"temperature": 37,"timestamp": "2025-01-01 03:55:26"},
    {"id": 36,"temperature": 32,"timestamp": "2025-01-01 04:00:25"},
    {"id": 37,"temperature": 39,"timestamp": "2025-01-01 04:05:03"},
    {"id": 38,"temperature": 31,"timestamp": "2025-01-01 04:10:39"},
    {"id": 39,"temperature": 31,"timestamp": "2025-01-01 04:15:16"},
    {"id": 40,"temperature": 32,"timestamp": "2025-01-01 04:20:14"},
    {"id": 41,"temperature": 33,"timestamp": "2025-01-01 04:25:03"},
    {"id": 42,"temperature": 21,"timestamp": "2025-01-01 04:30:01"},
    {"id": 43,"temperature": 34,"timestamp": "2025-01-01 04:35:24"},
    {"id": 44,"temperature": 39,"timestamp": "2025-01-01 04:40:10"},
    {"id": 45,"temperature": 36,"timestamp": "2025-01-01 04:45:47"},
    {"id": 46,"temperature": 40,"timestamp": "2025-01-01 04:50:18"},
    {"id": 47,"temperature": 27,"timestamp": "2025-01-01 04:55:35"},
    {"id": 48,"temperature": 37,"timestamp": "2025-01-01 05:00:11"},
    {"id": 49,"temperature": 38,"timestamp": "2025-01-01 05:05:45"}
]


@app.route('/')
def home():
    return redirect(url_for('login'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if username is USERS:
            return render_template('register.html', error="Smůla, tento uživatel již existuje. Zvol jiné jméno")

        hashed_pswd = generate_password_hash(password)
        USERS[username] = hashed_pswd
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # verify user
        if username not in USERS:
            return render_template('login.html', error="Tento uživatel neexistuje. Zkus se zaregistrovat.")
        stored_hash = USERS[username]
        if check_password_hash(stored_hash, password):
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Špatné heslo.")

    return render_template('login.html')

@app.route('/dashboard', defaults={'count': 15})  # default value (when nothing entered)
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    # If user is not logged in, redirect to login
    if 'username' not in session:
        return redirect(url_for('login'))

    # Default number of records when the user enters nothing
    count = 15

    if request.method == 'POST':
        # Read the value from the form (field named "count")
        count_str = request.form.get('count', '15')
        try:
            c = int(count_str)
            # If the number is less than 1, set at least 1
            if c < 1:
                c = 1
            count = c
        except ValueError:
            # If the user enters invalid input (e.g. a letter), keep the default value 15
            count = 15

    # Last measured value (last element in DATA, or None if DATA is empty)
    last_value = DATA[-1] if DATA else None
    # Select the last 'count' records; if fewer, returns only available
    last_n = DATA[-count:] if DATA else []

    return render_template('dashboard.html',
                           posledni_hodnota=last_value,
                           data=last_n,
                           count=count)


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect(url_for('home'))


@app.route('/delete_oldest', methods=['POST'])
def delete_oldest():
    if 'username' not in session:
        return redirect(url_for('login'))
    # only if DATA is not empty
    if DATA:
        DATA.pop(-1)
    return redirect(url_for('dashboard'))


# Starting the web application at 0.0.0.0:4000 with debug mode enabled
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=True)

#<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.2.0/dist/css/bootstrap.min.css">
