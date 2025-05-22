import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash

from database import db, User, fetch_all
from mqtt import run_mqtt, send_command
from api_routes import api_blueprint

# Initialize Flask application
def create_app():
    application = Flask(__name__)
    application.config['SECRET_KEY'] = os.urandom(24)  # secret for session
    application.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
    application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Setup database
    db.init_app(application)
    from database import setup_database
    with application.app_context():
        db.create_all()
        setup_database()  # ensure measurements table exists
        db.create_all()

    # Setup login manager
    login_mgr = LoginManager()
    login_mgr.login_view = 'signin'
    login_mgr.init_app(application)

    @login_mgr.user_loader
    def load_user_by_id(uid):
        return User.query.get(int(uid))

    # Register API blueprint
    application.register_blueprint(api_blueprint, url_prefix='/api')

    # Global control flags
    led_enabled = False
    measuring = False
    interval_seconds = 10

    # Start MQTT client
    run_mqtt()

    @application.route('/')
    def root_redirect():
        return redirect(url_for('dashboard_view'))

    @application.route('/dashboard')
    @login_required
    def dashboard_view():
        # Determine ordering
        order = request.args.get('sort', 'desc').lower()
        records = fetch_all(order)

        # Chart preparation
        labels = [r[3] for r in records]
        temps = [r[1] for r in records]

        # Render with control flags
        return render_template('dashboard.html', measurements=records,
                               labels=labels, temps=temps, sort=order,
                               led_enabled=led_enabled, measuring=measuring,
                               interval_seconds=interval_seconds)

    @application.route('/register', methods=['GET', 'POST'])
    def signup():
        if request.method == 'POST':
            name = request.form.get('username')
            pwd = request.form.get('password')

            # Validate inputs
            if not name or not pwd:
                flash('Zadejte uživatelské jméno nebo heslo.')
                return redirect(url_for('signup'))

            if User.query.filter_by(username=name).first():
                flash('Tento uživatel už existuje.')
                return redirect(url_for('signup'))

            # Create new user
            user = User(username=name, password=generate_password_hash(pwd))
            db.session.add(user)
            db.session.commit()

            flash('Registrace proběhla úspěšně, můžete se přihlásit')
            return redirect(url_for('signin'))

        return render_template('register.html')

    @application.route('/login', methods=['GET', 'POST'])
    def signin():
        if request.method == 'POST':
            name = request.form.get('username')
            pwd = request.form.get('password')
            user = User.query.filter_by(username=name).first()

            # Verify credentials
            if user and check_password_hash(user.password, pwd):
                login_user(user, remember=False)
                return redirect(url_for('dashboard_view'))
            flash('Neplatné přihlašovací údaje')
            return redirect(url_for('signin'))

        return render_template('login.html')

    @application.route('/logout')
    def signout():
        logout_user()
        return redirect(url_for('signin'))

    @application.route('/control', methods=['POST'])
    def handle_control():
        nonlocal led_enabled, measuring, interval_seconds
        cmd = request.form.get('action')
        new_int = request.form.get('period')

        # Command section
        if cmd:
            send_command(cmd)
            if cmd == 'LED ON': led_enabled = True
            elif cmd == 'LED OFF': led_enabled = False
            elif cmd == 'MEASURE ON': measuring = True
            elif cmd == 'MEASURE OFF': measuring = False

        # Interval section
        if new_int:
            try:
                val = int(new_int)
                if val > 0 and val != interval_seconds:
                    interval_seconds = val
                    send_command(f'SET INTERVAL {val}')
            except ValueError:
                print('Invalid interval:', new_int)

        return redirect(url_for('dashboard_view'))

    return application

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=4000, debug=True)