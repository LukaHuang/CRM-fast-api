import uuid
from datetime import datetime
from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)
    product_id = Column(UUID(as_uuid=True), ForeignKey("products.id"), nullable=False)
    order_no = Column(String(50))
    amount = Column(Numeric(10, 2))
    payment_method = Column(String(50))
    purchased_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    customer = relationship("Customer", back_populates="purchases")
    product = relationship("Product", back_populates="purchases")
