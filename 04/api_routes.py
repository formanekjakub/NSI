from flask import Blueprint, request, jsonify
from flask_login import login_required
from database import remove_record, wipe_records

api_blueprint = Blueprint('api', __name__)

@api_blueprint.route('/data', methods=['POST'])
@login_required
def create_entry():
    # Insert new measurement via API
    payload = request.get_json()
    if not payload or 'temperature' not in payload:
        return jsonify({'error': 'Není uvedena teplota'}), 400

    entry = Data(temperature=payload['temperature'])
    db.session.add(entry)
    db.session.commit()
    return jsonify({'message': 'Data vložena', 'id': entry.id}), 201

@api_blueprint.route('/data/<int:item_id>', methods=['DELETE'])
@login_required
def remove_entry(item_id):
    # Delete specific record
    remove_record(item_id)
    return jsonify({'message': 'Data smazána'}), 200

@api_blueprint.route('/clear', methods=['POST'])
@login_required
def clear_entries():
    # Wipe all measurements
    wipe_records()
    return jsonify({'message': 'Vše smazáno'}), 200