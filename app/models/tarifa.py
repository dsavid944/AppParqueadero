from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime


class Tarifa(db.Model):
    __tablename__ = 'tarifas'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(255), nullable=False)
    costo = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_vehiculo = db.Column(db.Enum('carro', 'moto'), nullable=False)
    vigencia_inicio = db.Column(db.DateTime, nullable=False)
    vigencia_fin = db.Column(db.DateTime, nullable=False)
