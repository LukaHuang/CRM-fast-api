from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from enum import Enum


class RecipientFilterEnum(str, Enum):
    ALL = "all"
    PURCHASED = "purchased"
    EVENT_ATTENDED = "event_attended"
    NOT_PURCHASED = "not_purchased"


class CampaignStatusEnum(str, Enum):
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    SENDING = "sending"
    COMPLETED = "completed"
    FAILED = "failed"


# 郵件範本
class EmailTemplateInfo(BaseModel):
    id: str
    name: str
    description: str
    subject_template: str
    preview_text: str


class EmailTemplateListResponse(BaseModel):
    templates: List[EmailTemplateInfo]


class EmailTemplatePreview(BaseModel):
    template_id: str
    customer_name: Optional[str] = "親愛的顧客"


class EmailTemplatePreviewResponse(BaseModel):
    subject: str
    html_content: str
    text_content: str


# 郵件活動
class EmailCampaignCreate(BaseModel):
    name: str
    subject: str
    template_id: Optional[str] = None
    content_html: str
    content_text: Optional[str] = None
    recipient_filter: RecipientFilterEnum = RecipientFilterEnum.ALL
    recipient_mode: str = "filter"  # "filter" 或 "manual"
    recipient_ids: Optional[List[str]] = None  # 手動模式的顧客 ID 列表
    scheduled_at: Optional[datetime] = None  # 排程發送時間


class EmailCampaignResponse(BaseModel):
    id: UUID
    name: str
    subject: str
    template_id: Optional[str]
    recipient_filter: RecipientFilterEnum
    recipient_mode: str
    status: CampaignStatusEnum
    total_recipients: int
    sent_count: int
    failed_count: int
    scheduled_at: Optional[datetime]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# 發送請求
class SendTestEmailRequest(BaseModel):
    template_id: str
    recipient_email: EmailStr
    recipient_name: Optional[str] = "測試用戶"


# 發送紀錄
class EmailLogResponse(BaseModel):
    id: UUID
    campaign_id: UUID
    customer_id: UUID
    recipient_email: str
    recipient_name: Optional[str]
    subject: Optional[str]
    status: str
    error_message: Optional[str]
    opened_at: Optional[datetime]
    open_count: int = 0
    sent_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


# 收件人預覽
class RecipientPreviewResponse(BaseModel):
    filter: RecipientFilterEnum
    total_count: int
    sample_recipients: List[dict]


# OAuth 狀態
class OAuthStatusResponse(BaseModel):
    is_configured: bool
    is_authenticated: bool
    user_email: Optional[str] = None
    message: str
