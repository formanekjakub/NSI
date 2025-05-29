from flask import Blueprint, request, jsonify
from flask_login import login_required
from database import db, delete_measurement, clear_measurements, get_threshold, set_threshold
from mqtt import publish_command
import json   

api_bp = Blueprint('api', __name__)

@api_bp.route('/data', methods=['POST'])
@login_required
def insert_data():
    # Inserts a new measured value.
    data_json = request.get_json()
    if not data_json or 'temperature' not in data_json:
        return jsonify({'error': 'Neni uvedena teplota'}), 400

    new_data = Data(temperature=data_json['temperature'])
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'message': 'Data uspesne vlozeny', 'id': new_data.id}), 201

@api_bp.route('/data/<int:data_id>', methods=['DELETE'])
@login_required
def delete_data(data_id):
    # Deletes a record by ID.
    delete_measurement(data_id)
    return jsonify({'message': 'Data smazana'}), 200

@api_bp.route('/delete_all', methods=['DELETE'])
@login_required
def clear_all():
    print("jou")
    # Clears all measurements.
    clear_measurements()
    return jsonify({'message': 'Data smazana'}), 200

@api_bp.route('/threshold', methods=['GET'])
@login_required
def api_get_threshold():
    # Returns the current threshold.
    return jsonify({'threshold': get_threshold()})

@api_bp.route('/threshold', methods=['POST'])
@login_required
def api_set_threshold():
    # Sets a new threshold value.
    body = request.get_json() or {}
    if 'threshold' not in body:
        return jsonify({'error': 'No threshold provided'}), 400
    try:
        t = int(body['threshold'])
    except ValueError:
        return jsonify({'error': 'Invalid threshold'}), 400

    set_threshold(t)
    # Send the new threshold to the Raspberry Pi.
    publish_command(json.dumps({'threshold': t}))
    return jsonify({'message': 'Threshold updated', 'threshold': t})
