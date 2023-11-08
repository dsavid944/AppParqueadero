from flask import Blueprint, request, redirect, render_template, url_for, flash, session
from ..models import Usuario, Rol
from flask_login import login_user, logout_user, login_required, current_user
from app import db
import re

auth_blueprint = Blueprint("auth", __name__, url_prefix="/auth")

def is_password_strong(password):
    """Verifica si la contraseña es fuerte usando expresiones regulares."""
    strong_password_regex = re.compile(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[!@#$%^&*(),.?\":{}|<>]).{8,}$")
    return strong_password_regex.match(password) is not None

@auth_blueprint.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        
        # Obtener el número de intentos fallidos o establecerlo en 0 si no existe
        failed_attempts = session.get('failed_attempts', 0)

        user = Usuario.query.filter_by(username=username).first()
        if user and user.check_password(password) and failed_attempts < 5:
            login_user(user)
            session['failed_attempts'] = 0  # Reset the failed login attempt counter
            return redirect(url_for("main.home"))
        
        # Incrementar los intentos fallidos si la autenticación falla
        failed_attempts += 1
        session['failed_attempts'] = failed_attempts

        if failed_attempts >= 5:
            flash("Has alcanzado el número máximo de intentos. Inténtalo más tarde.", "error")
        else:
            flash("Nombre de usuario o contraseña incorrecta", "error")
        
    return render_template("auth/login.html", failed_attempts=session.get('failed_attempts', 0))


@auth_blueprint.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        password = request.form.get("password")
        role_id = request.form.get("role")

        # Validación de disponibilidad de email y username y fortaleza de contraseña
        if Usuario.is_username_taken(username):
            flash("El nombre de usuario ya está registrado.", "error")
        elif Usuario.is_email_taken(email):
            flash("El email ya está registrado.", "error")
        elif not is_password_strong(password):
            flash("La contraseña no cumple con los requisitos de seguridad.", "error")
        else:
            # Validación de rol y creación de usuario
            role = Rol.query.get(role_id)
            if not role:
                flash("Rol seleccionado no es válido", "error")
            else:
                user = Usuario(email=email, username=username, rol_id=role.id)
                user.set_password(password)  # Asegurar que la contraseña se hashee
                try:
                    db.session.add(user)
                    db.session.commit()
                    flash("Registro exitoso. Ahora puedes iniciar sesión.", "success")
                    return redirect(url_for("auth.login"))
                except Exception as e:
                    db.session.rollback()
                    flash("Error al registrar el usuario. Por favor, intenta de nuevo.", "error")

    # Si algo falla o es GET request, mostrar el formulario de registro
    roles = Rol.query.all()
    return render_template("auth/register.html", roles=roles)

@auth_blueprint.route("/logout")
@login_required
def logout():
    logout_user()
    session.pop('failed_attempts', None)  # Clear the failed login attempt counter
    flash("Has cerrado sesión con éxito", "success")
    return redirect(url_for("auth.login"))


