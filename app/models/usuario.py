from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime



class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    vehiculos = db.relationship('Vehiculo', backref='propietario', lazy='dynamic')
    novedades_reportadas = db.relationship('Novedad', backref='reportador', lazy='dynamic')
    rol = db.relationship('Rol', back_populates='usuarios')
    

    
    # Puedes añadir un método para verificar si el usuario es admin
    def es_admin(self):
        return self.rol.name == 'admin'