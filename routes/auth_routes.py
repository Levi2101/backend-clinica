from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token
from database import usuarios_collection
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re

auth_bp = Blueprint('auth_bp', __name__)

# Límite de intentos para prevenir fuerza bruta (usa IP como referencia)
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "10 per minute"])

# Función para validar email
def email_valido(email):
    return re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email)

# Función para validar contraseña segura
def password_segura(password):
    return (
        len(password) >= 8 and
        re.search(r'[A-Z]', password) and
        re.search(r'[a-z]', password) and
        re.search(r'[0-9]', password) and
        re.search(r'[\W_]', password)
    )

# Registrar nuevo usuario
@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')
    rol = data.get('rol', 'usuario')

    # Nuevos campos
    nombre = data.get('nombre', '').strip()
    fecha_nacimiento = data.get('fechaNacimiento', '').strip()
    sexo = data.get('sexo', '').strip()

    if not email_valido(email):
        return jsonify({ "error": "Email no válido" }), 400

    if not password_segura(password):
        return jsonify({ 
            "error": "La contraseña debe tener mínimo 8 caracteres, una mayúscula, una minúscula, un número y un símbolo." 
        }), 400

    if usuarios_collection.find_one({ "email": email }):
        return jsonify({ "error": "El usuario ya existe" }), 400

    hashed_password = generate_password_hash(password)
    usuarios_collection.insert_one({
        "email": email,
        "password": hashed_password,
        "rol": rol,
        "nombre": nombre,
        "fechaNacimiento": fecha_nacimiento,
        "sexo": sexo
    })

    return jsonify({ "mensaje": "Usuario registrado correctamente" }), 201


# Login con límite de intentos
@auth_bp.route('/api/login', methods=['POST'])
@limiter.limit("5 per minute")  # Límite por IP
def login():
    data = request.get_json()
    email = data.get('email', '').strip()
    password = data.get('password', '')

    # Validar entradas
    if not email_valido(email) or not password:
        return jsonify({ "error": "Credenciales inválidas" }), 401

    user = usuarios_collection.find_one({ "email": email })
    if not user or not check_password_hash(user['password'], password):
        return jsonify({ "error": "Credenciales inválidas" }), 401  # No revela si el usuario existe

    access_token = create_access_token(
        identity=email,
        additional_claims={ "rol": user["rol"] }
    )

    return jsonify({ "token": access_token }), 200
