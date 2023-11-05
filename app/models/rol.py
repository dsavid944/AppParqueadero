from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime


class Rol(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    usuarios = db.relationship('Usuario', backref='rol', lazy='dynamic')
