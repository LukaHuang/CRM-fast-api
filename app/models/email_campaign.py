import uuid
import enum
from datetime import datetime
from sqlalchemy import Column, String, Text, DateTime, Integer, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


class CampaignStatus(str, enum.Enum):
    DRAFT = "draft"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"


class RecipientFilter(str, enum.Enum):
    ALL = "all"
    PURCHASED = "purchased"
    EVENT_ATTENDED = "event_attended"
    NOT_PURCHASED = "not_purchased"


class EmailCampaign(Base):
    __tablename__ = "email_campaigns"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(200), nullable=False)
    subject = Column(String(500), nullable=False)
    template_id = Column(String(50))
    content_html = Column(Text, nullable=False)
    content_text = Column(Text)

    recipient_filter = Column(
        Enum(RecipientFilter),
        default=RecipientFilter.ALL
    )

    status = Column(Enum(CampaignStatus), default=CampaignStatus.DRAFT)

    total_recipients = Column(Integer, default=0)
    sent_count = Column(Integer, default=0)
    failed_count = Column(Integer, default=0)

    started_at = Column(DateTime)
    completed_at = Column(DateTime)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    email_logs = relationship("EmailLog", back_populates="campaign")
