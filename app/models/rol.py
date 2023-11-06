from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime


class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Enum('admin', 'user'), default='user')

    # La relación debe ser 'back_populates' en lugar de 'backref' si ya tienes una referencia en la clase Usuario
    usuarios = db.relationship('Usuario', back_populates='rol')
