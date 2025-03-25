from flask import Blueprint, request, jsonify
from pymongo import MongoClient
import os
from bson import ObjectId
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from database import citas_collection
import requests

# Blueprint
cita_bp = Blueprint('citas', __name__)

# Conexión a MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['clinicaDB']
citas_collection = db['citas']

# Función para enviar notificación por WhatsApp
def enviar_whatsapp(nombre, fecha, hora, servicio):
    telefono = "5212229141895"  # ← Cambia esto por tu número de WhatsApp con lada (ej. 5212221234567)
    api_key = "3954495"      # ← Reemplaza con tu API Key de CallMeBot

    mensaje = f"Nueva cita agendada:\n📌 Nombre: {nombre}\n📅 Fecha: {fecha} {hora}\n💼 Servicio: {servicio}"

    url = "https://api.callmebot.com/whatsapp.php"
    params = {
        "phone": telefono,
        "text": mensaje,
        "apikey": api_key
    }

    try:
        response = requests.get(url, params=params)
        print("✅ WhatsApp enviado" if response.status_code == 200 else "❌ Error al enviar WhatsApp")
    except Exception as e:
        print("❌ Error enviando WhatsApp:", str(e))


# Ruta para crear nueva cita
@cita_bp.route('/api/citas', methods=['POST'])
@jwt_required()
def crear_cita():
    data = request.get_json()
    email_usuario = get_jwt_identity()  # El email viene del token JWT

    nueva_cita = {
        "nombre": data["nombre"],
        "email": data["email"],
        "telefono": data["telefono"],
        "fecha": data["fecha"],
        "hora": data["hora"],
        "servicio": data["servicio"],
        "comentarios": data["comentarios"],
        "usuario": email_usuario
    }

    citas_collection.insert_one(nueva_cita)

    # Enviar notificación por WhatsApp
    enviar_whatsapp(
        data["nombre"],
        data["fecha"],
        data["hora"],
        data["servicio"]
    )

    return jsonify({ "mensaje": "Cita agendada" }), 201


# Ruta para obtener todas las citas (admin)
@cita_bp.route('/api/citas', methods=['GET'])
@jwt_required()
def obtener_citas():
    jwt_data = get_jwt()
    if jwt_data.get("rol") != "admin":
        return jsonify({ "error": "Acceso denegado" }), 403

    citas = list(citas_collection.find())
    for cita in citas:
        cita["_id"] = str(cita["_id"])
    return jsonify(citas)


# Ruta para obtener citas del usuario autenticado
@cita_bp.route('/api/mis-citas', methods=['GET'])
@jwt_required()
def mis_citas():
    email = get_jwt_identity()
    citas = list(citas_collection.find({ "usuario": email }))
    for cita in citas:
        cita["_id"] = str(cita["_id"])
    return jsonify(citas)


# Ruta para obtener una cita por ID
@cita_bp.route('/api/citas/<id>', methods=['GET'])
def obtener_cita(id):
    cita = citas_collection.find_one({"_id": ObjectId(id)})
    if cita:
        cita["_id"] = str(cita["_id"])
        return jsonify(cita), 200
    else:
        return jsonify({"error": "Cita no encontrada"}), 404


# Ruta para eliminar una cita (solo admin)
@cita_bp.route('/api/citas/<id>', methods=['DELETE'])
@jwt_required()
def eliminar_cita(id):
    jwt_data = get_jwt()
    if jwt_data.get("rol") != "admin":
        return jsonify({ "error": "Acceso denegado" }), 403

    resultado = citas_collection.delete_one({ "_id": ObjectId(id) })

    if resultado.deleted_count > 0:
        return jsonify({ "mensaje": "Cita eliminada" }), 200
    else:
        return jsonify({ "error": "Cita no encontrada" }), 404
