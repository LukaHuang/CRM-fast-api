from datetime import datetime
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import and_

from app.models import Customer, Purchase, EventRegistration
from app.models.email_campaign import EmailCampaign, CampaignStatus, RecipientFilter
from app.models.email_log import EmailLog, EmailStatus
from app.services.gmail_service import gmail_service
from app.templates.email_templates import render_template, get_template, get_all_templates


class EmailService:
    def __init__(self, db: Session):
        self.db = db

    def get_recipients_by_filter(
        self, recipient_filter: RecipientFilter
    ) -> List[Customer]:
        """根據篩選條件取得收件人列表"""
        query = self.db.query(Customer)

        if recipient_filter == RecipientFilter.ALL:
            return query.all()

        elif recipient_filter == RecipientFilter.PURCHASED:
            # 有購買紀錄的顧客
            purchased_customer_ids = (
                self.db.query(Purchase.customer_id).distinct().subquery()
            )
            return query.filter(Customer.id.in_(purchased_customer_ids)).all()

        elif recipient_filter == RecipientFilter.EVENT_ATTENDED:
            # 有參加活動的顧客
            attended_customer_ids = (
                self.db.query(EventRegistration.customer_id).distinct().subquery()
            )
            return query.filter(Customer.id.in_(attended_customer_ids)).all()

        elif recipient_filter == RecipientFilter.NOT_PURCHASED:
            # 沒有購買紀錄的顧客
            purchased_customer_ids = (
                self.db.query(Purchase.customer_id).distinct().subquery()
            )
            return query.filter(~Customer.id.in_(purchased_customer_ids)).all()

        return []

    def get_recipients_count(self, recipient_filter: RecipientFilter) -> int:
        """取得收件人數量"""
        return len(self.get_recipients_by_filter(recipient_filter))

    def get_recipients_preview(
        self, recipient_filter: RecipientFilter, limit: int = 10
    ) -> dict:
        """預覽收件人列表"""
        recipients = self.get_recipients_by_filter(recipient_filter)
        total_count = len(recipients)
        sample = recipients[:limit]

        return {
            "filter": recipient_filter,
            "total_count": total_count,
            "sample_recipients": [
                {
                    "id": str(r.id),
                    "name": r.name,
                    "email": r.email,
                }
                for r in sample
            ],
        }

    def create_campaign(
        self,
        name: str,
        subject: str,
        content_html: str,
        content_text: Optional[str] = None,
        template_id: Optional[str] = None,
        recipient_filter: RecipientFilter = RecipientFilter.ALL,
    ) -> EmailCampaign:
        """建立郵件活動"""
        total_recipients = self.get_recipients_count(recipient_filter)

        campaign = EmailCampaign(
            name=name,
            subject=subject,
            template_id=template_id,
            content_html=content_html,
            content_text=content_text,
            recipient_filter=recipient_filter,
            total_recipients=total_recipients,
        )
        self.db.add(campaign)
        self.db.commit()
        self.db.refresh(campaign)
        return campaign

    def get_campaign(self, campaign_id: UUID) -> Optional[EmailCampaign]:
        """取得單一活動"""
        return self.db.query(EmailCampaign).filter(EmailCampaign.id == campaign_id).first()

    def get_campaigns(
        self, skip: int = 0, limit: int = 50
    ) -> List[EmailCampaign]:
        """取得活動列表"""
        return (
            self.db.query(EmailCampaign)
            .order_by(EmailCampaign.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def send_campaign(self, campaign_id: UUID) -> dict:
        """執行發送活動"""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return {"success": False, "error": "找不到活動"}

        if campaign.status == CampaignStatus.SENDING:
            return {"success": False, "error": "活動正在發送中"}

        if campaign.status == CampaignStatus.COMPLETED:
            return {"success": False, "error": "活動已完成發送"}

        if not gmail_service.is_authenticated():
            return {"success": False, "error": "Gmail 尚未授權"}

        # 更新狀態為發送中
        campaign.status = CampaignStatus.SENDING
        campaign.started_at = datetime.utcnow()
        self.db.commit()

        # 取得收件人
        recipients = self.get_recipients_by_filter(campaign.recipient_filter)

        sent_count = 0
        failed_count = 0

        for customer in recipients:
            # 個人化內容
            subject = campaign.subject.replace("{customer_name}", customer.name or "親愛的顧客")
            html_content = campaign.content_html.replace(
                "{customer_name}", customer.name or "親愛的顧客"
            )
            text_content = None
            if campaign.content_text:
                text_content = campaign.content_text.replace(
                    "{customer_name}", customer.name or "親愛的顧客"
                )

            # 建立發送紀錄
            email_log = EmailLog(
                campaign_id=campaign.id,
                customer_id=customer.id,
                recipient_email=customer.email,
                recipient_name=customer.name,
                subject=subject,
            )
            self.db.add(email_log)
            self.db.commit()

            # 發送郵件
            success, message_id, error = gmail_service.send_email(
                to_email=customer.email,
                subject=subject,
                html_content=html_content,
                text_content=text_content,
            )

            # 更新發送紀錄
            if success:
                email_log.status = EmailStatus.SENT
                email_log.gmail_message_id = message_id
                email_log.sent_at = datetime.utcnow()
                sent_count += 1
            else:
                email_log.status = EmailStatus.FAILED
                email_log.error_message = error
                failed_count += 1

            self.db.commit()

        # 更新活動狀態
        campaign.sent_count = sent_count
        campaign.failed_count = failed_count
        campaign.status = CampaignStatus.COMPLETED
        campaign.completed_at = datetime.utcnow()
        self.db.commit()

        return {
            "success": True,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "total": len(recipients),
        }

    def send_test_email(
        self, template_id: str, recipient_email: str, recipient_name: str = "測試用戶"
    ) -> dict:
        """發送測試郵件"""
        if not gmail_service.is_authenticated():
            return {"success": False, "error": "Gmail 尚未授權"}

        rendered = render_template(template_id, recipient_name)
        if not rendered:
            return {"success": False, "error": f"找不到範本: {template_id}"}

        success, message_id, error = gmail_service.send_email(
            to_email=recipient_email,
            subject=rendered["subject"],
            html_content=rendered["html"],
            text_content=rendered["text"],
        )

        if success:
            return {"success": True, "message_id": message_id}
        else:
            return {"success": False, "error": error}

    def get_email_logs(
        self, campaign_id: Optional[UUID] = None, skip: int = 0, limit: int = 100
    ) -> List[EmailLog]:
        """取得發送紀錄"""
        query = self.db.query(EmailLog)
        if campaign_id:
            query = query.filter(EmailLog.campaign_id == campaign_id)
        return query.order_by(EmailLog.created_at.desc()).offset(skip).limit(limit).all()
