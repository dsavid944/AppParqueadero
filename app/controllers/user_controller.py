from flask import Blueprint, render_template, request, redirect, url_for, flash
from ..models import (
    Usuario,
    Vehiculo,
    HistorialVehiculo,
    Transaccion,
    Novedad,
    Celda,
    Tarifa,
)
from .. import db
from flask_login import login_required, current_user
from datetime import datetime
from decimal import Decimal

user_blueprint = Blueprint("user", __name__, url_prefix="/user")


@user_blueprint.route("/gestion", methods=["GET", "POST"])
@login_required
def gestion():
    if request.method == "POST":
        # Aquí debería ir la lógica para manejar POST requests, como registrar entradas o salidas, hacer pagos, etc.
        pass

    # Lógica para recuperar datos necesarios para la gestión de vehículos
    vehiculos = (
        Vehiculo.query.all()
    )  # o filtrar según el usuario actual con current_user.vehiculos
    historial = (
        HistorialVehiculo.query.all()
    )  # o una versión filtrada para el usuario actual
    transacciones = Transaccion.query.all()  # o filtrar por vehículo/usuario
    novedades = Novedad.query.all()  # o filtrar por usuario

    return render_template(
        "user/gestion.html",
        vehiculos=vehiculos,
        historial=historial,
        transacciones=transacciones,
        novedades=novedades,
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
        if vehiculo:
            # Buscar el registro de historial más reciente sin fecha de salida
            registro_historial = (
                HistorialVehiculo.query.filter_by(
                    vehiculo_id=vehiculo.id, fecha_hora_salida=None
                )
                .order_by(HistorialVehiculo.fecha_hora_entrada.desc())
                .first()
            )
            if registro_historial:
                # Registrar la salida del vehículo
                registro_historial.fecha_hora_salida = datetime.now()

                # Liberar la celda ocupada por el vehículo
                celda_ocupada = Celda.query.get(registro_historial.celda_id)
                celda_ocupada.estado = "libre"

                # Guardar los cambios en la base de datos
                db.session.commit()
                flash("Salida de vehículo registrada con éxito.")
            else:
                flash(
                    "No se encontró entrada pendiente de salida para la placa proporcionada."
                )
        else:
            flash("Vehículo no registrado.")

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
    # Suponiendo que la fecha_hora_salida ya ha sido asignada en el historial del vehículo
    duracion_estancia = historial_vehiculo.fecha_hora_salida - historial_vehiculo.fecha_hora_entrada
    
    # Necesitas acceder al tipo de vehículo a través del objeto vehículo asociado
    tipo_vehiculo = historial_vehiculo.vehiculo.tipo  # Accede al tipo desde el objeto vehiculo relacionado

    tarifa_id, monto = obtener_tarifa(
        duracion_estancia, tipo_vehiculo
    )
    return tarifa_id, monto



@user_blueprint.route("/pago", methods=["GET", "POST"])
@login_required
def registrar_pago():
    if request.method == "POST":
        placa = request.form.get("placa_vehiculo")
        metodo_pago = request.form.get("metodo_pago")

        # Primero, encuentra el vehículo por placa
        vehiculo = Vehiculo.query.filter_by(placa=placa).first()
        if not vehiculo:
            flash("No se encontró el vehículo con la placa proporcionada.")
            return redirect(url_for("user.gestion"))
        
        # Encuentra el último historial del vehículo que no tiene hora de salida
        historial_vehiculo = (
            HistorialVehiculo.query.filter_by(vehiculo_id=vehiculo.id, fecha_hora_salida=None)
            .order_by(HistorialVehiculo.fecha_hora_entrada.desc())
            .first()
        )
        if not historial_vehiculo:
            flash("No se encontró un historial activo para la placa proporcionada.")
            return redirect(url_for("user.gestion"))

        # Asignamos la fecha de salida antes de calcular la tarifa
        historial_vehiculo.fecha_hora_salida = datetime.now()

        # Calcula la tarifa en base a la estancia y recupera el tarifa_id correspondiente
        tarifa_id, monto = calcular_tarifa(historial_vehiculo)
        if tarifa_id is None or monto is None:
            flash("No se pudo calcular la tarifa para el vehículo.")
            return redirect(url_for("user.gestion"))

        # Crear la transacción con la tarifa correspondiente
        nueva_transaccion = Transaccion(
            historial_vehiculo_id=historial_vehiculo.id,
            tarifa_id=tarifa_id,
            fecha_hora_pago=datetime.now(),
            monto=monto,
            metodo_pago=metodo_pago,
        )

        # Añadir la nueva transacción y guardar los cambios en la base de datos
        db.session.add(nueva_transaccion)
        db.session.commit()

        flash("Pago registrado con éxito.")
        return redirect(url_for("user.gestion"))

    # Si el método no es POST, renderiza el template de pagos
    return render_template("user/pagos.html")



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

