from flask import Blueprint, render_template
from ..models import HistorialVehiculo

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/gestion', methods=['GET'])
def gestion():
    # Lógica para la gestión de entradas, salidas, pagos, y novedades
    return render_template('user/gestion.html')
