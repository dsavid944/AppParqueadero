from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime


class Vehiculo(db.Model):
    __tablename__ = 'vehiculos'
    id = db.Column(db.Integer, primary_key=True)
    placa = db.Column(db.String(10), unique=True, nullable=False)
    tipo = db.Column(db.Enum('carro', 'moto'), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    modelo = db.Column(db.String(50))
    color = db.Column(db.String(30))
    propietario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    historial = db.relationship('HistorialVehiculo', backref='vehiculo', lazy='dynamic')