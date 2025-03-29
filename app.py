from flask import Flask
from flask_cors import CORS
import os
from dotenv import load_dotenv
from flask_jwt_extended import JWTManager
from routes.auth_routes import auth_bp
from routes.citas_routes import cita_bp

load_dotenv()

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})
#permitir solo el de mi pagina
#CORS(app, resources={r"/*": {"origins": ["https://clinica-7d2a8.web.app"]}})

# Clave secreta JWT
app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "clave-super-secreta")
jwt = JWTManager(app)

# Blueprints
app.register_blueprint(cita_bp)
app.register_blueprint(auth_bp)

# Ruta simple para probar que el backend está activo
@app.route("/")
def home():
    return "API activa"

# Solo para desarrollo local
if __name__ == '__main__':
    # Render necesita 0.0.0.0 y el puerto de entorno
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
