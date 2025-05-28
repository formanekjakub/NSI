from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from database import get_all_measurements, init_db, clear_measurements, delete_measurement, insert_measurement
from mqtt import start_mqtt, publish_command


from database import db, User
from api_routes import api_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ShellNotPass'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # pripojeni k databazy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) #pouze pro odhlaseni kdyz se aplikace vypne

# global variables
is_led_on = False
is_measuring = False
measurement_interval = 10


db.init_app(app)

# Vytvoření tabulek hned po inicializaci aplikace
with app.app_context():
    db.create_all()

# nastaveni loginu
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'  # kam presmerujeme neprihlaseneho uzivatele


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Registrace BluePrintu s API
app.register_blueprint(api_bp, url_prefix='/api')


############ web cast
@app.route('/')
def index():
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
@login_required
def dashboard():
    # sorting
    sort_order = request.args.get('sort', 'desc').lower()
    measurements = get_all_measurements(sort_order)

    # Prepare chart data
    labels = [row['timestamp_received'] for row in measurements]
    temps = [row['temperature'] for row in measurements]
    humidities = [row['humidity'] for row in measurements]
    moistures = [row['soil_moisture'] for row in measurements]
    lights = [row['light'] for row in measurements]

    # Dummy values for now — replace these with your actual logic or state
    period = 10
    led_on = True
    measuring = True

    chart_info = [
    ('Teplota [°C]', 'temperature'),
    ('Vlhkost [%]', 'humidity'),
    ('Půdní vlhkost', 'soil_moisture'),
    ('Světlo', 'light')
    ]

    return render_template(
        'dashboard.html',
        measurements=measurements,
        labels=labels,
        temps=temps,
        humidities=humidities,
        moistures=moistures,
        lights=lights,
        chart_info=chart_info,
        current_period=period,
        led_state=led_on,
        measure_state=measuring,
        sort=sort_order
    )



@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash('Zadejte uživatelské jméno nebo heslo.')
            return redirect(url_for('register'))

        existing_user = User.query.filter_by(username=username).first()  # nacte posledniho uzivatele do promenne
        if existing_user:
            flash('Tento uživatel už existuje.')
            redirect(url_for('register'))
        # ulozeni do databaze
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        flash('Registrace proběhla úspěšně, můžete se přihlásit')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session.permanent = False
            login_user(user, remember=False)
            return redirect(url_for('dashboard'))
        else:
            flash('Neplatné přihlašovací údaje')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/control", methods=["POST"])
def control():
    global is_led_on, is_measuring, measurement_interval

    # Read form inputs
    command_str = request.form.get("action")
    new_interval = request.form.get("period")

    # Handle action commands
    if command_str:
        publish_command(command_str)
        if command_str == "LED ON":
            is_led_on = True
        elif command_str == "LED OFF":
            is_led_on = False
        elif command_str == "MEASURE ON":
            is_measuring = True
        elif command_str == "MEASURE OFF":
            is_measuring = False

    # Handle period adjustment
    if new_interval:
        try:
            interval_val = int(new_interval)
            # Only send update if it's a positive change
            if interval_val > 0 and interval_val != measurement_interval:
                measurement_interval = interval_val
                publish_command(f"SET INTERVAL {interval_val}")
        except ValueError:
            print("Invalid interval value:", new_interval)

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    start_mqtt()
    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=True)
