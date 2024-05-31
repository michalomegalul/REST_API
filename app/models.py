import uuid
from datetime import datetime

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID
from typing import TYPE_CHECKING

db = SQLAlchemy()

if TYPE_CHECKING:
    from flask_sqlalchemy.model import Model
else:
    Model = db.Model


class Product(Model):
    __tablename__ = "products"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(200), nullable=True)
    lowest_price = db.Column(db.Integer, nullable=True)
    offers = db.relationship(
        "Offer", backref="product", lazy="dynamic", cascade="all, delete-orphan"
    )


class Offer(Model):
    __tablename__ = "offers"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    price = db.Column(db.Integer, nullable=False)
    items_in_stock = db.Column(db.Integer, nullable=False)
    product_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("products.id"), nullable=False
    )
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
