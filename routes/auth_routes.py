from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from database import usuarios_collection

auth_bp = Blueprint('auth_bp', __name__)

# Registrar nuevo usuario (opcional, o solo lo usas una vez para crear al admin)
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    rol = data.get('rol', 'usuario')  # Por defecto es usuario

    if usuarios_collection.find_one({ "email": email }):
        return jsonify({ "error": "Usuario ya existe" }), 400

    hashed_password = generate_password_hash(password)
    usuarios_collection.insert_one({
        "email": email,
        "password": hashed_password,
        "rol": rol
    })

    return jsonify({ "mensaje": "Usuario registrado correctamente" }), 201

# Login
@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = usuarios_collection.find_one({ "email": email })
    if not user or not check_password_hash(user['password'], password):
        return jsonify({ "error": "Credenciales inválidas" }), 401

    # Creamos el token con el email como identidad y el rol como claim adicional
    access_token = create_access_token(
        identity=email,
        additional_claims={ "rol": user["rol"] }
    )

    return jsonify({ "token": access_token }), 200
