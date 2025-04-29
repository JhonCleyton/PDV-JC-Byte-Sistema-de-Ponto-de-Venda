from sqlalchemy import Column, Integer, ForeignKey, Table
from models import db

promotion_products = Table(
    'promotion_products', db.metadata,
    Column('promotion_id', Integer, ForeignKey('promotions.id'), primary_key=True),
    Column('product_id', Integer, ForeignKey('products.id'), primary_key=True)
)
