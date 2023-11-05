from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime


class HistorialVehiculo(db.Model):
    __tablename__ = 'historial_vehiculos'
    id = db.Column(db.Integer, primary_key=True)
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))
    fecha_hora_entrada = db.Column(db.DateTime, nullable=False)
    fecha_hora_salida = db.Column(db.DateTime)
    celda_id = db.Column(db.Integer, db.ForeignKey('celdas.id'))
    transacciones = db.relationship('Transaccion', backref='historial_vehiculo', lazy='dynamic')