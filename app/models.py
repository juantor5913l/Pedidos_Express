from app import db
from datetime import datetime

class Producto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    precio = db.Column(db.Integer, nullable=False)
    imagen = db.Column(db.String(200))
    disponible = db.Column(db.Boolean, default=True)


class Pedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cliente = db.Column(db.String(100))
    telefono = db.Column(db.String(20))
    mesa = db.Column(db.String(200))
    total = db.Column(db.Integer)
    estado = db.Column(db.String(50), default="Recibido")


class DetallePedido(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pedido_id = db.Column(db.Integer, db.ForeignKey('pedido.id'))
    producto_id = db.Column(db.Integer, db.ForeignKey('producto.id'))
    cantidad = db.Column(db.Integer)

    producto = db.relationship('Producto')