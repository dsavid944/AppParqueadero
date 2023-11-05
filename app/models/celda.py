from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime



class Celda(db.Model):
    __tablename__ = 'celdas'
    id = db.Column(db.Integer, primary_key=True)
    numero = db.Column(db.Integer, unique=True, nullable=False)
    estado = db.Column(db.Enum('libre', 'ocupada'), nullable=False, default='libre')
    tipo_vehiculo = db.Column(db.Enum('carro', 'moto'), nullable=False)
    historial_vehiculos = db.relationship('HistorialVehiculo', backref='celda', lazy='dynamic')