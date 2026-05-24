from flask import Blueprint, render_template, redirect, url_for, session, request
from app import db
from app.models import Producto, Pedido, DetallePedido

main = Blueprint("main", __name__)


# --------------------------
# MENU PRINCIPAL
# --------------------------

@main.route("/")
def menu():
    productos = Producto.query.all()
    carrito = session.get("carrito", {})
    total_items = sum(carrito.values())

    return render_template(
        "menu.html",
        productos=productos,
        total_items=total_items
    )


@main.route("/cargar-productos")
def cargar_productos():
    productos = [
        Producto(nombre="Hamburguesa clásica", precio=18000, imagen="hamburguesa.jpg"),
        Producto(nombre="Pizza personal", precio=22000, imagen="pizza.jpg"),
        Producto(nombre="Papas francesas", precio=9000, imagen="papas.jpg"),
        Producto(nombre="Perro caliente", precio=12000, imagen="perro.jpg"),
        Producto(nombre="Gaseosa", precio=5000, imagen="gaseosa.jpg"),
        Producto(nombre="Malteada", precio=11000, imagen="malteada.jpg"),
    ]

    for producto in productos:
        db.session.add(producto)

    db.session.commit()

    return "Productos cargados"


# --------------------------
# CARRITO
# --------------------------

@main.route("/agregar/<int:producto_id>")
def agregar(producto_id):
    carrito = session.get("carrito", {})
    producto_id = str(producto_id)

    carrito[producto_id] = carrito.get(producto_id, 0) + 1

    session["carrito"] = carrito

    return redirect(url_for("main.menu"))


@main.route("/carrito")
def carrito():
    carrito = session.get("carrito", {})
    productos = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        subtotal = producto.precio * cantidad
        total += subtotal

        productos.append({
            "producto": producto,
            "cantidad": cantidad,
            "subtotal": subtotal
        })

    return render_template("carrito.html", productos=productos, total=total)


@main.route("/sumar/<int:producto_id>")
def sumar(producto_id):
    carrito = session.get("carrito", {})
    producto_id = str(producto_id)

    if producto_id in carrito:
        carrito[producto_id] += 1

    session["carrito"] = carrito

    return redirect(url_for("main.carrito"))


@main.route("/restar/<int:producto_id>")
def restar(producto_id):
    carrito = session.get("carrito", {})
    producto_id = str(producto_id)

    if producto_id in carrito:
        carrito[producto_id] -= 1

        if carrito[producto_id] <= 0:
            del carrito[producto_id]

    session["carrito"] = carrito

    return redirect(url_for("main.carrito"))


# --------------------------
# CONFIRMAR PEDIDO
# --------------------------

@main.route("/confirmar", methods=["GET", "POST"])
def confirmar():
    carrito = session.get("carrito", {})

    if not carrito:
        return redirect(url_for("main.menu"))

    productos = []
    total = 0

    for producto_id, cantidad in carrito.items():
        producto = Producto.query.get(int(producto_id))
        subtotal = producto.precio * cantidad
        total += subtotal

        productos.append((producto, cantidad))

    if request.method == "POST":
        nombre = request.form["nombre"]
        telefono = request.form["telefono"]
        mesa = request.form["mesa"]

        pedido = Pedido(
            cliente=nombre,
            telefono=telefono,
            mesa=mesa,
            total=total
        )

        db.session.add(pedido)
        db.session.commit()

        for producto, cantidad in productos:
            detalle = DetallePedido(
                pedido_id=pedido.id,
                producto_id=producto.id,
                cantidad=cantidad
            )

            db.session.add(detalle)

        db.session.commit()

        session.pop("carrito", None)

        return redirect(url_for("main.estado", pedido_id=pedido.id))

    return render_template("pedido.html", total=total)


# --------------------------
# ESTADO PEDIDO
# --------------------------

@main.route("/estado/<int:pedido_id>")
def estado(pedido_id):
    pedido = Pedido.query.get_or_404(pedido_id)

    return render_template("estado.html", pedido=pedido)


@main.route("/buscar_pedido", methods=["GET", "POST"])
def buscar_pedido():
    if request.method == "POST":
        pedido_id = request.form["pedido_id"]
        return redirect(url_for("main.estado", pedido_id=pedido_id))

    return render_template("buscar_pedido.html")


# --------------------------
# PANEL ADMIN
# --------------------------

@main.route("/admin")
def admin():
    pedidos = Pedido.query.order_by(Pedido.id.desc()).all()
    pedidos_con_detalles = []

    for pedido in pedidos:
        detalles = DetallePedido.query.filter_by(pedido_id=pedido.id).all()

        pedidos_con_detalles.append({
            "pedido": pedido,
            "detalles": detalles
        })

    return render_template("admin.html", pedidos_con_detalles=pedidos_con_detalles)


@main.route("/cambiar_estado/<int:pedido_id>/<estado>")
def cambiar_estado(pedido_id, estado):
    pedido = Pedido.query.get_or_404(pedido_id)

    pedido.estado = estado

    db.session.commit()

    return redirect(url_for("main.admin"))
