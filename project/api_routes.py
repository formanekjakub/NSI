from flask import Blueprint, request, jsonify
from flask_login import login_required
from database import db, delete_measurement, clear_measurements

api_bp = Blueprint('api', __name__)

@api_bp.route('/data', methods=['POST'])
@login_required
def insert_data():
    # Vloží novou naměřenou hodnotu.
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
    # Smaže záznam podle ID.
    delete_measurement(data_id)
    return jsonify({'message': 'Data smazana'}), 200

@api_bp.route('/delete_all', methods=['DELETE'])
@login_required
def clear_all():
    print("jou")
    clear_measurements()
    return jsonify({'message': 'Data smazana'}), 200