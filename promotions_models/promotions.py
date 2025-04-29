from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text
from models import db
from promotions_models.promotion_products import promotion_products

class Promotion(db.Model):
    __tablename__ = 'promotions'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), nullable=False)
    description = Column(Text)
    discount_type = Column(String(20), nullable=False)  # 'percent' ou 'fixed'
    discount_value = Column(Float, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamento com produtos
    products = db.relationship(
        'Product',
        secondary=promotion_products,
        backref=db.backref('promotions', lazy='dynamic'),
        lazy='dynamic'
    )

    def is_active(self):
        now = datetime.utcnow()
        return self.active and self.start_date <= now <= self.end_date
