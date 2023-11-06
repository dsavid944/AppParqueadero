from flask import Blueprint, request, redirect, render_template, url_for, flash
from ..models import Usuario, Rol
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, logout_user, login_required
from app import db

auth_blueprint = Blueprint('auth', __name__, url_prefix='/auth')

@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = Usuario.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        else:
            flash('Credenciales inválidas')
    return render_template('auth/login.html')

@auth_blueprint.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Has cerrado sesión con éxito', 'success')
    return redirect(url_for('auth.login'))

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.form.get('username')
        password = request.form.get('password')
        role_id = request.form.get('role')
        role = Rol.query.filter_by(id=role_id).first()
        
        if not role:
            flash('Rol seleccionado no es válido', 'error')
            return render_template('auth/register.html', roles=Rol.query.all())

        # Crear una instancia del usuario
        user = Usuario(username=username, password=generate_password_hash(password))
        user.role_id = role.id  # Asignar el rol al usuario

        # Agregar el usuario a la base de datos
        db.session.add(user)
        db.session.commit()

        flash('Registro exitoso. Ahora puedes iniciar sesión.', 'success')
        return redirect(url_for('auth.login'))
    else:
        # Si es una solicitud GET, pasamos los roles al template
        roles = Rol.query.all()  # Obtener todos los roles disponibles
        return render_template('auth/register.html', roles=roles)

    # Mostrar la página de registro si es una solicitud GET
    return render_template('auth/register.html')

