from flask import Flask, render_template, redirect, url_for
from database import get_all_measurements, init_db, clear_measurements
from mqtt import start_mqtt

app = Flask(__name__)

@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    measurements = get_all_measurements()
    return render_template("dashboard.html", measurements=measurements)


@app.route("/clear", methods=["POST"])
def clear():
    clear_measurements()
    return redirect(url_for('dashboard'))

if __name__ == "__main__":
    init_db()
    start_mqtt()
    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=False)
