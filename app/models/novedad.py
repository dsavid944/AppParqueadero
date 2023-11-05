from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime



class Novedad(db.Model):
    __tablename__ = 'novedades'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.Text, nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    reportado_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    vehiculo_id = db.Column(db.Integer, db.ForeignKey('vehiculos.id'))