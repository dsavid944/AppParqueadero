from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import Usuario, Vehiculo, HistorialVehiculo, Transaccion, Novedad, Celda, Tarifa
from .. import db
from flask_login import login_required, current_user
from datetime import datetime

user_blueprint = Blueprint('user', __name__, url_prefix='/user')

@user_blueprint.route('/gestion', methods=['GET', 'POST'])
@login_required
def gestion():
    if request.method == 'POST':
        # Aquí debería ir la lógica para manejar POST requests, como registrar entradas o salidas, hacer pagos, etc.
        pass

    # Lógica para recuperar datos necesarios para la gestión de vehículos
    vehiculos = Vehiculo.query.all()  # o filtrar según el usuario actual con current_user.vehiculos
    historial = HistorialVehiculo.query.all()  # o una versión filtrada para el usuario actual
    transacciones = Transaccion.query.all()  # o filtrar por vehículo/usuario
    novedades = Novedad.query.all()  # o filtrar por usuario
    tipos_vehiculo = ['carro', 'moto']

    return render_template(
        'user/gestion.html',
        vehiculos=vehiculos,
        historial=historial,
        transacciones=transacciones,
        novedades=novedades,
        tipos_vehiculo=tipos_vehiculo
    )

@user_blueprint.route('/entrada', methods=['POST'])
@login_required
def registrar_entrada():
    if request.method == 'POST':
        placa = request.form.get('placa')  # Obtener la placa del formulario
        tipo_vehiculo = request.form.get('tipo_vehiculo')  # Obtener el tipo de vehículo del formulario
        
        # Verificar si el vehículo ya está registrado
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()

        # Si el vehículo no está registrado, crear una nueva instancia y registrarla
        if request.method == 'POST':
        # Recoger todos los datos del formulario
            placa = request.form.get('placa')
            tipo_vehiculo = request.form.get('tipo_vehiculo')
            marca = request.form.get('marca')
            modelo = request.form.get('modelo')  
            color = request.form.get('color')
            usuario_id = current_user.id
        
        # Verificar si el vehículo ya está registrado
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()

        # Si el vehículo no está registrado, crear una nueva instancia y registrarla
        if vehiculo is None:
            # Crear el nuevo vehículo con todos los datos
            nuevo_vehiculo = Vehiculo(
                placa=placa,
                tipo=tipo_vehiculo,
                marca=marca,
                modelo=modelo,
                color=color,
                usuario_id=usuario_id  # Asegúrate de que este campo se esté recogiendo o gestionando adecuadamente
            )
            
            # Añadir el nuevo vehículo a la sesión y hacer commit para generar su ID
            db.session.add(nuevo_vehiculo)
            db.session.commit()

            # Asignar el vehículo recién creado a la variable vehiculo para seguir con la lógica de entrada
            vehiculo = nuevo_vehiculo
            flash('Vehículo registrado con éxito.')

         # Buscar una celda libre para el tipo de vehículo
        celda_libre = Celda.query.filter_by(estado='libre', tipo_vehiculo=tipo_vehiculo).first()
        if celda_libre is None:
            flash('No hay celdas libres para el tipo de vehículo.')
            return redirect(url_for('user.gestion'))
        else:
            # Si encontramos celda libre, procedemos
            flash('Celda libre encontrada: ' + str(celda_libre.id))  # Para depuración

        # Registrar la entrada del vehículo
        nueva_entrada = HistorialVehiculo(
            vehiculo_id=vehiculo.id,
            fecha_hora_entrada=datetime.now(),
            celda_id=celda_libre.id
        )
        db.session.add(nueva_entrada)

        # Actualizar el estado de la celda a 'ocupada'
        celda_libre.estado = 'ocupada'
        db.session.commit()  # Confirmar cambios

        flash('Entrada de vehículo registrada con éxito.')
        return redirect(url_for('user.gestion'))
    
    # Si el método no es POST
    return redirect(url_for('user.gestion'))


@user_blueprint.route('/salida', methods=['POST'])
@login_required
def registrar_salida():
    if request.method == 'POST':
        historial_id = request.form.get('historial_id')  # ID del historial de vehículo
        
        # Buscar el registro del historial por ID
        registro_historial = HistorialVehiculo.query.get(historial_id)
        if registro_historial and registro_historial.fecha_hora_salida is None:
            # Registrar la salida del vehículo
            registro_historial.fecha_hora_salida = datetime.now()
            
            # Liberar la celda ocupada por el vehículo
            celda_ocupada = Celda.query.get(registro_historial.celda_id)
            celda_ocupada.estado = 'libre'
            
            # Guardar los cambios en la base de datos
            db.session.commit()
            flash('Salida de vehículo registrada con éxito.')
        else:
            flash('Registro de salida no válido o ya registrado.')
        
        return redirect(url_for('user.gestion'))
    return redirect(url_for('user.gestion'))


@user_blueprint.route('/pago', methods=['POST'])
@login_required
def registrar_pago():
    if request.method == 'POST':
        historial_id = request.form.get('historial_id')
        monto = request.form.get('monto')  # Este monto se puede calcular o recibir como input
        metodo_pago = request.form.get('metodo_pago')

        # Crear la transacción
        nueva_transaccion = Transaccion(
            historial_vehiculo_id=historial_id,
            fecha_hora_pago=datetime.now(),
            monto=monto,
            metodo_pago=metodo_pago
        )

        # Añadir la nueva transacción y guardar los cambios en la base de datos
        db.session.add(nueva_transaccion)
        db.session.commit()

        flash('Pago registrado con éxito.')
        return redirect(url_for('user.gestion'))
    return redirect(url_for('user.gestion'))


@user_blueprint.route('/novedad', methods=['POST'])
@login_required
def reportar_novedad():
    if request.method == 'POST':
        descripcion = request.form.get('descripcion')
        vehiculo_id = request.form.get('vehiculo_id')

        # Crear la novedad
        nueva_novedad = Novedad(
            descripcion=descripcion,
            vehiculo_id=vehiculo_id,
            fecha_hora_reporte=datetime.now(),
            usuario_id=current_user.id  # Asociar la novedad al usuario actual
        )

        # Añadir la novedad y guardar los cambios en la base de datos
        db.session.add(nueva_novedad)
        db.session.commit()

        flash('Novedad reportada con éxito.')
        return redirect(url_for('user.gestion'))
    return redirect(url_for('user.gestion'))
