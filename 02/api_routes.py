from flask import Blueprint, request, jsonify
from database import db, Data

api_bp = Blueprint('api', __name__)

@api_bp.route('/data', methods=['POST'])
def insert_data():
    # Vloží novou naměřenou hodnotu.
    data_json = request.get_json()
    if not data_json or 'temperature' not in data_json:
        return jsonify({'error': 'Neni uvedena teplota'}), 400

    new_data = Data(temperature=data_json['temperature'])
    db.session.add(new_data)
    db.session.commit()

    return jsonify({'message': 'Data uspesne vlozeny', 'id': new_data.id}), 201


@api_bp.route('/data', methods=['GET'])
def get_data():
    # Vrátí všechny naměřené hodnoty
    # ziska parametru sort
    sort_order = request.args.get('sort', 'asc').lower()
    # Pokud je zadano desc, seřadíme sestupně, jinak vzestupně
    if sort_order == 'desc':
        data_objects = Data.query.order_by(Data.created_at.desc()).all()
    else:
        data_objects = Data.query.order_by(Data.created_at.asc()).all()

    data_list = []
    for obj in data_objects:
        data_list.append({
            'id': obj.id,
            'temperature': obj.temperature,
            'created_at': obj.created_at.isoformat()
        })
    return jsonify(data_list), 200


@api_bp.route('/data/last', methods=['GET'])
def get_last_data():
    # Vrátí poslední naměřenou hodnotu.
    data_obj = Data.query.order_by(Data.created_at.desc()).first()
    if not data_obj:
        return jsonify({'error': 'Zadna data nenalezena'}), 404
    return jsonify({
        'id': data_obj.id,
        'temperature': data_obj.temperature,
        'created_at': data_obj.created_at.isoformat()
    }), 200


@api_bp.route('/data/<int:data_id>', methods=['GET'])
def get_data_by_id(data_id):
    # Vrátí hodnotu s daným ID.
    data_obj = Data.query.get_or_404(data_id)
    return jsonify({
        'id': data_obj.id,
        'temperature': data_obj.temperature,
        'created_at': data_obj.created_at.isoformat()
    }), 200


@api_bp.route('/data/oldest', methods=['DELETE'])
def delete_oldest_data():
    # Smaže nejstarší naměřenou hodnotu.
    data_obj = Data.query.order_by(Data.created_at.asc()).first()
    if not data_obj:
        return jsonify({'error': 'Zádna data k smazani'}), 404
    db.session.delete(data_obj)
    db.session.commit()
    return jsonify({'message': 'Nejstarsi data smazana', 'id': data_obj.id}), 200


@api_bp.route('/data/<int:data_id>', methods=['DELETE'])
def delete_data(data_id):
    # Smaže záznam podle ID.
    data_obj = Data.query.get_or_404(data_id)
    db.session.delete(data_obj)
    db.session.commit()
    return jsonify({'message': 'Data smazana'}), 200
