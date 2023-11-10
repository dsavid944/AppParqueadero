from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Importa la extensión Flask-Migrate
from flask_login import LoginManager, UserMixin


# Inicializar SQLAlchemy aquí, sin parámetros
db = SQLAlchemy()

# Inicializar Flask Login Manager aquí, sin parámetros
login_manager = LoginManager()

# Inicializar Flask Migrate aquí, sin parámetros
migrate = Migrate()

def create_app():
    
    app = Flask(__name__)

    # Configuración de la clave secreta y la base de datos
    app.config['SECRET_KEY'] = 'tu_clave_secreta_super_secreta'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@127.0.0.1:3307/parqueadero_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Vincular las instancias de las extensiones con la aplicación creada
    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)
    
    # Registra los blueprints usando la función register_blueprints
    from .controllers.main_controller import register_blueprints
    register_blueprints(app)
    
    # Configuración de la sesión de login
    login_manager.login_view = 'auth.login'
    
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))
  
    # Importar aquí los modelos para evitar importaciones circulares
    from app.models import Usuario, Rol, Celda, Vehiculo, HistorialVehiculo, Tarifa, Transaccion, Novedad
    
    # Configurar aquí el cargador de usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return Usuario.query.get(int(user_id))

    return app


    # Crear tablas de base de datos si no existen
    with app.app_context():
        db.create_all()
        
  

