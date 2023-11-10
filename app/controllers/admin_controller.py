from flask import Blueprint, request, redirect, render_template, url_for, flash
from ..models import Tarifa, Usuario
from .. import db
from datetime import datetime
from flask_login import login_required, current_user

admin_blueprint = Blueprint("admin", __name__, url_prefix="/admin")


@admin_blueprint.route("/tarifa", methods=["GET", "POST"])
def tarifa():
    if request.method == "POST":
        action = request.form.get("action")

        if action == "update":
            tarifa_id = request.form.get("tarifa_id", type=int)
            nuevo_costo = request.form.get("nuevo_costo", type=float)

            # Lógica para actualizar la tarifa vigente
            tarifa = Tarifa.query.get(tarifa_id)
            if tarifa and tarifa.vigencia_inicio <= datetime.now() <= tarifa.vigencia_fin:
                tarifa.costo = nuevo_costo
                db.session.commit()
                flash("Precio actualizado correctamente.", "success")
            else:
                flash("Tarifa no encontrada o no está en periodo vigente.", "error")

        elif action == "add":
            descripcion = request.form.get("descripcion")
            tipo_vehiculo = request.form.get("tipo_vehiculo")
            costo = request.form.get("costo", type=float)
            vigencia_inicio = request.form.get("vigencia_inicio")
            vigencia_fin = request.form.get("vigencia_fin")

            nueva_tarifa = Tarifa(
                descripcion=descripcion,
                tipo_vehiculo=tipo_vehiculo,
                costo=costo,
                vigencia_inicio=datetime.strptime(vigencia_inicio, '%Y-%m-%d'),
                vigencia_fin=datetime.strptime(vigencia_fin, '%Y-%m-%d')
            )
            db.session.add(nueva_tarifa)
            db.session.commit()
            flash("Nueva tarifa añadida correctamente.", "success")

    tarifas = Tarifa.query.order_by(Tarifa.tipo_vehiculo, Tarifa.vigencia_inicio).all()
    now = datetime.now()

    return render_template("admin/tarifa.html", tarifas=tarifas, now=now)


@admin_blueprint.route("/reportes", methods=["GET"])
def reportes():
    # Lógica para mostrar reportes
    return render_template("admin/reportes.html")

def user_es_admin(user):
    return user.rol_id == 2

@admin_blueprint.route("/editar_user", methods=["GET", "POST"])
@login_required
def editar_user():
    user = current_user

    if request.method == "POST":
        # Aquí, asegúrate de no permitir que el usuario cambie su propio ID o rol si no es administrador
        user.email = request.form.get("email")
        user.username = request.form.get("username")

        # Omitir la actualización del rol si el usuario no es administrador
        if user_es_admin(user):
            user.rol_id = request.form.get("rol_id", type=int)
        
        db.session.commit()
        flash("Información del usuario actualizada con éxito.")
        return redirect(url_for("user.gestion"))

    return render_template("admin/edit_user.html", user=user)

@admin_blueprint.route("/cambiar_password", methods=["GET", "POST"])
@login_required
def cambiar_password():
    user = current_user

    if request.method == "POST":
        new_password = request.form.get("new_password")
        user.set_password(new_password)

        db.session.commit()
        flash("Contraseña actualizada con éxito.")
        return redirect(url_for("user.gestion"))

    return render_template("admin/cambiar_password.html", user=user)


@admin_blueprint.route("/manage_users")
def permiso_users():
    users = Usuario.query.all()
    return render_template("admin/permiso_users.html")

