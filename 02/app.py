from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
import os


from database import db, User, Data
from api_routes import api_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ShellNotPass'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'  # pripojeni k databazy
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.urandom(24) #pouze pro odhlaseni kdyz se aplikace vypne

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
    sort_order = request.args.get('sort', 'asc').lower()
    if sort_order == 'desc':
        data = Data.query.order_by(Data.created_at.desc()).all()
    else:
        data = Data.query.order_by(Data.created_at.asc()).all()
    return render_template('dashboard.html', data=data)


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
    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=True)
