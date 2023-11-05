from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime


class Transaccion(db.Model):
    __tablename__ = 'transacciones'
    id = db.Column(db.Integer, primary_key=True)
    historial_vehiculo_id = db.Column(db.Integer, db.ForeignKey('historial_vehiculos.id'))
    fecha_hora_pago = db.Column(db.DateTime, nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    metodo_pago = db.Column(db.Enum('efectivo', 'tarjeta', 'transferencia'), nullable=False)