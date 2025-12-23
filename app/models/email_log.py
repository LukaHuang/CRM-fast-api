import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class EmailStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("email_campaigns.id"), nullable=False)
    customer_id = Column(UUID(as_uuid=True), ForeignKey("customers.id"), nullable=False)

    recipient_email = Column(String(255), nullable=False)
    recipient_name = Column(String(100))
    subject = Column(String(500))

    status = Column(Enum(EmailStatus), default=EmailStatus.PENDING)
    error_message = Column(Text)
    gmail_message_id = Column(String(100))

    sent_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    campaign = relationship("EmailCampaign", back_populates="email_logs")
    customer = relationship("Customer")
