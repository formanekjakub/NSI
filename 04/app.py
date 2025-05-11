from flask import Flask, render_template, redirect, url_for, request
from database import get_all_measurements, init_db, clear_measurements
from mqtt import start_mqtt, send_command


app = Flask(__name__)

# global variables
led_state = False
measure_state = False
current_period = 10

@app.route("/")
def index():
    return redirect(url_for('dashboard'))

@app.route("/dashboard")
def dashboard():
    measurements = get_all_measurements()
    return render_template("dashboard.html", measurements=measurements,
                           led_state=led_state, measure_state=measure_state,
                           current_period=current_period)


@app.route("/clear", methods=["POST"])
def clear():
    clear_measurements()
    return redirect(url_for('dashboard'))


@app.route("/control", methods=["POST"])
def control():
    global led_state, measure_state, current_period

    action = request.form.get("action")
    period = request.form.get("period")

    if action:
        send_command(action)
        if action == "LED ON":
            led_state = True
        elif action == "LED OFF":
            led_state = False
        elif action == "MEASURE ON":
            measure_state = True
        elif action == "MEASURE OFF":
            measure_state = False

    if period:
        try:
            p = int(period)
            if p > 0 and p != current_period:
                current_period = p
                send_command(f"SET PERIOD {p}")
        except ValueError:
            print("Neplatná hodnota periody:", period)

    return redirect(url_for("dashboard"))


if __name__ == "__main__":
    init_db()
    start_mqtt()
    app.run(host='0.0.0.0', port=4000, debug=True, use_reloader=False)

