from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from database import init_db, clear_measurements, delete_measurement, insert_measurement, get_last_n_measurements, get_all_pots, get_threshold
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
    sort_order   = request.args.get('sort', 'desc').lower()
    n            = request.args.get('n', default=20, type=int)

    # 1) Read raw pot_id
    pot_id_raw = request.args.get('pot_id', '')
    try:
        selected = int(pot_id_raw)
    except (ValueError, TypeError):
        selected = None

    # 2) Load all pots for the dropdown
    pots = get_all_pots()
    threshold = get_threshold()
    

    # 3) Only fetch data if we have a valid integer pot_id
    if selected is not None:
        measurements = get_last_n_measurements(n, sort=sort_order, pot_id=selected)
    else:
        measurements = []

    # 4) Prepare your chart series
    labels     = [r['timestamp_received'] for r in measurements]
    temps      = [r['temperature']        for r in measurements]
    humidities = [r['humidity']           for r in measurements]
    moistures  = [r['soil_moisture']      for r in measurements]
    lights     = [r['light']              for r in measurements]

    chart_info = [
      ('Teplota [°C]', 'temperature'),
      ('Vlhkost [%]',  'humidity'),
      ('Půdní vlhkost','soil_moisture'),
      ('Světlo',       'light')
    ]

    return render_template(
      'dashboard.html',
      pots=pots,
      selected_pot_id=selected,
      n=n,
      sort=sort_order,
      measurements=measurements,
      labels=labels, temps=temps,
      humidities=humidities,
      moistures=moistures, lights=lights,
      chart_info=chart_info,
      threshold=threshold
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


if __name__ == "__main__":
    init_db()
    start_mqtt()
    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=True)
