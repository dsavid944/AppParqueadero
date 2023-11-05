from flask import Blueprint, request, redirect, render_template, url_for, flash
from ..models import Tarifa, Usuario

admin_blueprint = Blueprint('admin', __name__, url_prefix='/admin')

@admin_blueprint.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if request.method == 'POST':
        # Aquí iría la lógica para cambiar configuraciones como precios o permisos.
        pass
    return render_template('admin/configuracion.html')

@admin_blueprint.route('/reportes', methods=['GET'])
def reportes():
    # Lógica para mostrar reportes
    return render_template('admin/reportes.html')
