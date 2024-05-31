from flask import Blueprint, jsonify, request, current_app
from .models import db, Offer, Product
from .tasks import fetch_offers, register_product_and_create_offer
import logging

logger = logging.getLogger(__name__)

api_bp = Blueprint("api", __name__)


@api_bp.route("/products", methods=["POST"])
def add_product():
    try:
        data = request.get_json()
        new_product = Product(
            name=data["name"], description=data.get("description", "")
        )
        db.session.add(new_product)
        db.session.commit()

        logger.info(f"New product created: {new_product.id}")

        from app import create_app

        app = create_app()
        register_product_and_create_offer(app, new_product)

        return jsonify({"id": new_product.id}), 201
    except Exception as e:
        logger.error(f"Error adding new product: {e}")
        return jsonify({"error": "Failed to add new product"}), 500


@api_bp.route("/products/<uuid:product_id>", methods=["PUT"])
def update_product(product_id):
    try:
        data = request.json
        product = Product.query.get_or_404(product_id)
        product.name = data["name"]
        product.description = data["description"]
        db.session.commit()
        return jsonify({"message": "Product updated successfully"})
    except Exception as e:
        logger.error(f"Error updating product {product_id}: {e}")
        return jsonify({"error": "Failed to update product"}), 500


@api_bp.route("/products/<uuid:product_id>", methods=["DELETE"])
def delete_product(product_id):
    try:
        product = Product.query.get_or_404(product_id)
        db.session.delete(product)
        db.session.commit()
        return jsonify({"message": "Product deleted successfully"})
    except Exception as e:
        logger.error(f"Error deleting product {product_id}: {e}")
        return jsonify({"error": "Failed to delete product"}), 500


@api_bp.route("/products/<uuid:product_id>/offers", methods=["GET"])
def get_product_offers(product_id):
    try:
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
    except Exception as e:
        logger.error(f"Error fetching offers for product {product_id}: {e}")
        return jsonify({"error": "Failed to fetch offers"}), 500


@api_bp.route("/update_offers", methods=["GET"])
def update_offers():
    try:
        fetch_offers(current_app)
        return jsonify({"message": "Offers updated successfully"})
    except Exception as e:
        logger.error(f"Error updating offers: {e}")
        return jsonify({"error": "Failed to update offers"}), 500


@api_bp.route("/products", methods=["GET"])
def get_products():
    try:
        products = Product.query.all()
        products_data = [
            {
                "id": str(product.id),
                "name": product.name,
                "description": product.description,
                "lowest_price": min(offer.price for offer in product.offers)
                if product.offers
                else "No offers available",
            }
            for product in products
        ]
        return jsonify(products_data)
    except Exception as e:
        logger.error(f"Error fetching products: {e}")
        return jsonify({"error": "Failed to fetch products"}), 500
