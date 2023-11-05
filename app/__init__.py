from flask import Flask
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

    # Configuración de la sesión de login
    login_manager.login_view = 'auth.login'

    # Importar y registrar blueprints
    from .controllers import admin_blueprint, user_blueprint, auth_blueprint
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(auth_blueprint)
    
    # Importar aquí los modelos para evitar importaciones circulares
    from app.models import Usuario, Rol, Celda, Vehiculo, HistorialVehiculo, Tarifa, Transaccion, Novedad, User
    
    # Configurar aquí el cargador de usuario para Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    return app

    # Crear tablas de base de datos si no existen
    with app.app_context():
        db.create_all()
        
  

