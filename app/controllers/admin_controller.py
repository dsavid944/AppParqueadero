from flask import Blueprint, request, redirect, render_template, url_for, flash
from ..models import Tarifa, Usuario
from .. import db

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.route("/configuracion", methods=["GET", "POST"])
def configuracion():
    if request.method == "POST":
        tarifa_id = request.form.get("tarifa_id")
        nuevo_costo = request.form.get("nuevo_costo")

        # Lógica para actualizar la tarifa
        tarifa = Tarifa.query.get(tarifa_id)
        if tarifa:
            tarifa.costo = nuevo_costo
            db.session.commit()
            flash("Precio actualizado correctamente.", "success")
        else:
            flash("Tarifa no encontrada.", "error")

        # Aquí podrías agregar más lógica para permisos y edición de usuarios si fuera necesario.

    tarifas = Tarifa.query.all()
    usuarios = Usuario.query.all()
    return render_template(
        "admin/configuracion.html", tarifas=tarifas, usuarios=usuarios
    )


@admin_blueprint.route("/reportes", methods=["GET"])
def reportes():
    # Lógica para mostrar reportes
    return render_template("admin/reportes.html")
