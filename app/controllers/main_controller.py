from flask import Blueprint, render_template

# Importamos los blueprints de otros módulos
from .admin_controller import admin_blueprint
from .user_controller import user_blueprint
from .auth_controller import auth_blueprint

# Creamos el Blueprint para este controlador principal
main_blueprint = Blueprint('main', __name__)

# Ruta de inicio que muestra las opciones de navegación disponibles
@main_blueprint.route('/')
@main_blueprint.route('/home') 
def home():
    return render_template('main.html')

# Función para registrar blueprints a la app principal
def register_blueprints(app):
    app.register_blueprint(auth_blueprint)
    app.register_blueprint(admin_blueprint)
    app.register_blueprint(user_blueprint)
    app.register_blueprint(main_blueprint)
