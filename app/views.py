from flask import Blueprint, request, jsonify
from .models import Product, Offer, db
from .tasks import fetch_offers


api_bp = Blueprint("api", __name__)


@api_bp.route("/products", methods=["POST"])
def add_product():
    data = request.get_json()
    new_product = Product(name=data["name"], description=data.get("description", ""))
    db.session.add(new_product)
    db.session.commit()
    return jsonify({"id": new_product.id}), 201


@api_bp.route("/products/<uuid:product_id>", methods=["PUT"])
def update_product(product_id):
    data = request.json
    product = Product.query.get_or_404(product_id)
    product.name = data["name"]
    product.description = data["description"]
    db.session.commit()
    return jsonify({"message": "Product updated successfully"})


@api_bp.route("/products/<uuid:product_id>", methods=["DELETE"])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    return jsonify({"message": "Product deleted successfully"})


@api_bp.route("/products/<uuid:product_id>/offers", methods=["GET"])
def get_product_offers(product_id):
    offers = Offer.query.filter_by(product_id=product_id).all()
    offers_data = [
        {
            "id": str(offer.id),
            "price": offer.price,
            "items_in_stock": offer.items_in_stock,
            "timestamp": offer.timestamp,
        }
        for offer in offers
    ]
    return jsonify(offers_data)


@api_bp.route("/update_offers", methods=["GET"])
def update_offers():
    fetch_offers()
    return jsonify({"message": "Offers updated successfully"})


@api_bp.route("/products", methods=["GET"])
def get_products():
    products = Product.query.all()
    products_data = [
        {
            "id": str(product.id),
            "name": product.name,
            "description": product.description,
        }
        for product in products
    ]
    return jsonify(products_data)
