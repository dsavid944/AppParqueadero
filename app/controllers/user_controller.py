from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from ..models import (
    Usuario,
    Vehiculo,
    HistorialVehiculo,
    Transaccion,
    Novedad,
    Celda,
    Tarifa
)
from .. import db
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal
from flask import send_file, abort
import os
from io import BytesIO
from reportlab.pdfgen import canvas

user_blueprint = Blueprint("user", __name__, url_prefix="/user")


@user_blueprint.route("/gestion", methods=["GET"])
@login_required
def gestion():
    # Obtener vehículos actualmente estacionados (aquellos sin fecha_hora_salida)
    historial_actual = (
        HistorialVehiculo.query.filter(HistorialVehiculo.fecha_hora_salida.is_(None))
        .join(Vehiculo)
        .add_columns(
            Vehiculo.placa,
            Vehiculo.tipo,
            HistorialVehiculo.fecha_hora_entrada,
            HistorialVehiculo.id.label("historial_id")
        )
        .all()
    )

    return render_template(
        "user/gestion.html",
        historial_actual=historial_actual,
    )



@user_blueprint.route("/entrada", methods=["GET", "POST"])
@login_required
def registrar_entrada():
    tipos_vehiculo = ["carro", "moto"]

    if request.method == "POST":
        placa = request.form.get("placa")
        tipo_vehiculo = request.form.get("tipo_vehiculo")

        # Verificar si el vehículo ya está registrado
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()

        # Si el vehículo ya está registrado, verificar si ya existe una entrada sin salida
        if vehiculo:
            entrada_activa = HistorialVehiculo.query.filter_by(
                vehiculo_id=vehiculo.id, fecha_hora_salida=None
            ).first()
            if entrada_activa:
                flash("Este vehículo ya tiene una entrada registrada sin salida.")
                return redirect(url_for("user.gestion"))

        # Si el vehículo no está registrado, crear una nueva instancia y registrarla
        else:
            marca = request.form.get("marca")
            modelo = request.form.get("modelo")
            color = request.form.get("color")
            usuario_id = current_user.id

            nuevo_vehiculo = Vehiculo(
                placa=placa,
                tipo=tipo_vehiculo,
                marca=marca,
                modelo=modelo,
                color=color,
                usuario_id=usuario_id,
            )
            db.session.add(nuevo_vehiculo)
            db.session.commit()
            vehiculo = nuevo_vehiculo
            flash("Vehículo registrado con éxito.")

        # Buscar una celda libre para el tipo de vehículo
        celda_libre = Celda.query.filter_by(
            estado="libre", tipo_vehiculo=tipo_vehiculo
        ).first()
        if celda_libre is None:
            flash("No hay celdas libres para el tipo de vehículo.")
            return redirect(url_for("user.gestion"))

        # Registrar la entrada del vehículo
        nueva_entrada = HistorialVehiculo(
            vehiculo_id=vehiculo.id,
            fecha_hora_entrada=datetime.now(),
            celda_id=celda_libre.id,
        )
        db.session.add(nueva_entrada)

        # Actualizar el estado de la celda a 'ocupada'
        celda_libre.estado = "ocupada"
        db.session.commit()

        flash("Entrada de vehículo registrada con éxito.")
        return redirect(url_for("user.gestion"))

    return render_template("user/entrada.html", tipos_vehiculo=tipos_vehiculo)


@user_blueprint.route("/salida", methods=["GET", "POST"])
@login_required
def registrar_salida():
    if request.method == "POST":
        placa = request.form.get("placa")  # Se obtiene la placa del formulario

        # Buscar el vehículo por la placa para obtener su ID
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()
        if not vehiculo:
            flash("Vehículo no registrado.")
            return redirect(url_for("user.gestion"))
        
        # Buscar el registro de historial más reciente sin fecha de salida
        registro_historial = (
            HistorialVehiculo.query.filter_by(
                vehiculo_id=vehiculo.id, fecha_hora_salida=None
            )
            .order_by(HistorialVehiculo.fecha_hora_entrada.desc())
            .first()
        )

        if registro_historial:
            # Calcula la tarifa provisionalmente (no asignes la salida aún)
            tarifa_id, monto = calcular_tarifa(registro_historial)
            
            # Guarda la información del pago en la sesión para usar en la siguiente página
            session['pago_info'] = {
                'historial_id': registro_historial.id,
                'monto': str(monto),  # Convertir Decimal a string para guardar en la sesión
                'tarifa_id': tarifa_id,
                'vehiculo_id': vehiculo.id,  # Guarda el ID del vehículo para liberar la celda luego
            }

            flash("Salida de vehículo preparada. Proceda con el pago.")
            return redirect(url_for("user.registrar_pago"))
        else:
            flash("No se encontró entrada pendiente de salida para la placa proporcionada.")
            return redirect(url_for("user.gestion"))

    return render_template("user/salida.html")


# Esta función encuentra la tarifa adecuada basada en la duración de la estancia y el tipo de vehículo
def obtener_tarifa(duracion_estancia, tipo_vehiculo):
    # Convertir duracion_estancia a minutos
    minutos_estancia = duracion_estancia.total_seconds() / 60
    # Asegúrate de que minutos_estancia sea un objeto Decimal
    minutos_estancia = Decimal(minutos_estancia)

    # Encuentra la tarifa que esté vigente y corresponda al tipo de vehículo
    tarifa_vigente = Tarifa.query.filter(
        Tarifa.tipo_vehiculo == tipo_vehiculo,
        Tarifa.vigencia_inicio <= datetime.now(),
        Tarifa.vigencia_fin >= datetime.now(),
    ).first()

    if tarifa_vigente:
        # Calcula el monto en base a la duración de la estancia
        monto = minutos_estancia * tarifa_vigente.costo
        return tarifa_vigente.id, round(
            monto, 2)  # Aseguramos que el monto tenga dos decimales

    # En caso de que no exista una tarifa vigente para el tipo de vehículo
    return None, None


# Esta función calcula la tarifa basada en la duración de la estancia del vehículo
def calcular_tarifa(historial_vehiculo):
    # Usa la hora actual como hora de salida provisional para el cálculo de la tarifa
    fecha_hora_salida_provisional = datetime.now()
    duracion_estancia = fecha_hora_salida_provisional - historial_vehiculo.fecha_hora_entrada
    
    tipo_vehiculo = historial_vehiculo.vehiculo.tipo
    tarifa_id, monto = obtener_tarifa(duracion_estancia, tipo_vehiculo)
    return tarifa_id, monto



@user_blueprint.route("/pago", methods=["GET", "POST"])
@login_required
def registrar_pago():
    if 'pago_info' not in session:
        flash("Información de pago no encontrada.")
        return redirect(url_for("user.gestion"))

    pago_info = session['pago_info']
    
    if request.method == "POST":
        metodo_pago = request.form.get("metodo_pago")

        historial_vehiculo = HistorialVehiculo.query.get(pago_info['historial_id'])
        if not historial_vehiculo or historial_vehiculo.fecha_hora_salida is not None:
            flash("No se encontró el historial del vehículo o ya se registró la salida.")
            return redirect(url_for("user.gestion"))
        
        # Si aún no se ha registrado la salida, hazlo ahora
        if historial_vehiculo.fecha_hora_salida is None:
            historial_vehiculo.fecha_hora_salida = datetime.now()

        # Crear la transacción con la tarifa correspondiente
        nueva_transaccion = Transaccion(
            historial_vehiculo_id=historial_vehiculo.id,
            tarifa_id=pago_info['tarifa_id'],
            fecha_hora_pago=datetime.now(),
            monto=Decimal(pago_info['monto']),
            metodo_pago=metodo_pago,
        )

        # Añadir la nueva transacción y guardar los cambios en la base de datos
        db.session.add(nueva_transaccion)
        db.session.commit()

        # Liberar la celda ocupada por el vehículo
        celda_ocupada = Celda.query.get(historial_vehiculo.celda_id)
        celda_ocupada.estado = "libre"

        # Limpia la información de pago de la sesión
        session.pop('pago_info', None)

        flash("Pago registrado con éxito.")

        # Redirige al ticket después de registrar el pago con éxito
        return redirect(url_for('user.generar_ticket', transaccion_id=nueva_transaccion.id))

    # Mostrar el formulario de pago con la información de la sesión si aún no se ha realizado el POST
    return render_template("user/pagos.html", 
                           monto=pago_info['monto'], 
                           metodo_pago=["efectivo", "transferencia", "tarjeta"], 
                           historial_id=pago_info['historial_id'])



@user_blueprint.route("/novedad", methods=["GET", "POST"])
@login_required
def reportar_novedad():
    if request.method == "POST":
        placa = request.form.get("placa")
        descripcion = request.form.get("descripcion")

        # Buscar el vehículo por placa para obtener su id
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()
        if not vehiculo:
            flash("No se encontró un vehículo con la placa proporcionada.")
            return redirect(url_for("user.novedad"))

        # Crear la novedad
        nueva_novedad = Novedad(
            descripcion=descripcion,
            vehiculo_id=vehiculo.id,
            fecha_hora=datetime.now(),
            reportado_por=current_user.id,  # Usar el nombre de campo correcto aquí
        )

        # Añadir la novedad y guardar los cambios en la base de datos
        db.session.add(nueva_novedad)
        db.session.commit()

        flash("Novedad reportada con éxito.")
        return redirect(url_for("user.gestion"))
    
    return render_template("user/novedad.html")


@user_blueprint.route("/ticket/<int:transaccion_id>")
@login_required
def generar_ticket(transaccion_id):
    # Recupera los datos necesarios para el ticket usando transaccion_id
    transaccion = Transaccion.query.get_or_404(transaccion_id)
    historial_vehiculo = HistorialVehiculo.query.get_or_404(transaccion.historial_vehiculo_id)
    vehiculo = Vehiculo.query.get_or_404(historial_vehiculo.vehiculo_id)
    tiempo_total = str((historial_vehiculo.fecha_hora_salida - historial_vehiculo.fecha_hora_entrada).total_seconds() // 3600) + ' horas'
    # Obtener la fecha y hora actuales
    fecha_actual = datetime.now()
    # Renderiza la plantilla con los datos del ticket
    return render_template('user/ticket.html', transaccion=transaccion, historial_vehiculo=historial_vehiculo, vehiculo=vehiculo, tiempo_total=tiempo_total, fecha=fecha_actual)

@user_blueprint.route('/historial_pagos')
@login_required
def historial_pagos():
    # Primero, obtenemos todos los vehículos del usuario actual
    vehiculos_usuario = Vehiculo.query.filter_by(usuario_id=current_user.id).all()
    ids_vehiculos = [vehiculo.id for vehiculo in vehiculos_usuario]
    
    # Luego, obtenemos todos los historiales que correspondan a esos vehículos
    historial_vehiculos = HistorialVehiculo.query.filter(HistorialVehiculo.vehiculo_id.in_(ids_vehiculos)).all()
    ids_historial = [hv.id for hv in historial_vehiculos]
    
    # Finalmente, obtenemos todas las transacciones asociadas a esos historiales
    pagos = Transaccion.query.filter(Transaccion.historial_vehiculo_id.in_(ids_historial)).order_by(Transaccion.fecha_hora_pago.desc()).all()
    
    # Estructurando la información para la plantilla
    pagos_historial = [{
        'fecha': pago.fecha_hora_pago.strftime('%d/%m/%Y'),
        'monto': str(pago.monto),
        'metodo': pago.metodo_pago,
        'recibo_url': url_for('user.descargar_recibo', pago_id=pago.id)
    } for pago in pagos]

    return render_template('user/historial_pagos.html', pagos=pagos_historial)



@user_blueprint.route('/descargar_recibo/<int:pago_id>')
@login_required
def descargar_recibo(pago_id):
    # Buscar la transacción y verificar permisos como antes
    transaccion = Transaccion.query.get_or_404(pago_id)
    historial_vehiculo = HistorialVehiculo.query.get_or_404(transaccion.historial_vehiculo_id)
    vehiculo = Vehiculo.query.get_or_404(historial_vehiculo.vehiculo_id)

    if vehiculo.usuario_id != current_user.id:
        abort(403)

    # Crear un buffer de bytes para el PDF
    buffer = BytesIO()

    # Crear el archivo PDF en memoria
    c = canvas.Canvas(buffer)
    c.drawString(100,750,"Recibo de Pago")
    c.drawString(100,735,f"ID de Transacción: {transaccion.id}")
    c.drawString(100,720,f"Fecha de Pago: {transaccion.fecha_hora_pago.strftime('%d/%m/%Y %H:%M')}")
    c.drawString(100,705,f"Monto: ${transaccion.monto}")
    c.drawString(100,690,f"Método de Pago: {transaccion.metodo_pago}")
    c.showPage()
    c.save()

    # Mover el puntero del buffer al principio para que 'send_file' lo lea desde el inicio
    buffer.seek(0)

    # Crear un nombre de archivo único
    pdf_filename = f"recibo_{pago_id}.pdf"

    # Enviar el buffer como un archivo PDF
    return send_file(buffer, as_attachment=True, download_name=pdf_filename, mimetype='application/pdf')