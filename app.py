import os
from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

# Cargar variables de entorno (Estándar de seguridad)
load_dotenv()

app = Flask(__name__)

# Configuración de Base de Datos
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['API_KEY'] = os.getenv('MY_SECRET_API_KEY') # Llave privada

db = SQLAlchemy(app)

# Modelo de Datos (Cumpliendo con persistencia y auditoría)
class ServerMetric(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    memory_usage = db.Column(db.String(20))
    battery_level = db.Column(db.Integer)
    temperature = db.Column(db.Float)
    status = db.Column(db.String(20))

with app.app_context():
    db.create_all()

# Middleware de Seguridad (Solo permite acceso con la llave correcta)
def validate_api_key():
    key = request.headers.get('X-API-KEY')
    return key == app.config['API_KEY']

@app.route('/metrics', methods=['POST'])
def save_metrics():
    if not validate_api_key():
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.json
    try:
        new_entry = ServerMetric(
            memory_usage=data['memory'],
            battery_level=data['battery'],
            temperature=data['temp'],
            status=data['status']
        )
        db.session.add(new_entry)
        db.session.commit()
        return jsonify({"message": "Data stored successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/metrics/latest', methods=['GET'])
def get_latest():
    # No requiere API Key para que el Dashboard sea fácil de leer (o puedes agregarle)
    last_metric = ServerMetric.query.order_by(ServerMetric.timestamp.desc()).first()
    if last_metric:
        return jsonify({
            "memory": last_metric.memory_usage,
            "battery": last_metric.battery_level,
            "temp": last_metric.temperature,
            "status": last_metric.status,
            "last_update": last_metric.timestamp.isoformat()
        })
    return jsonify({"message": "No data available"}), 404

if __name__ == '__main__':
    app.run(debug=False) # Debug en False para producción