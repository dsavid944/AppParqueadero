from app import db  # Importa db de app
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255))
    rol_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    last_login = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.Enum('active', 'inactive'), default='active')
    vehiculos = db.relationship('Vehiculo', backref='propietario', lazy='dynamic')
    novedades_reportadas = db.relationship('Novedad', backref='reportador', lazy='dynamic')
    rol = db.relationship('Rol', back_populates='usuarios')
    
    
    @staticmethod
    def is_username_taken(username):
        return Usuario.query.filter_by(username=username).first() is not None

    @staticmethod
    def is_email_taken(email):
        return Usuario.query.filter_by(email=email).first() is not None
    
    def set_password(self, password):
        self.password = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password, password)

