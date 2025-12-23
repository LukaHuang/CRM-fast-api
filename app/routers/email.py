from datetime import datetime
from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.email import (
    EmailTemplateInfo,
    EmailTemplateListResponse,
    EmailTemplatePreview,
    EmailTemplatePreviewResponse,
    EmailCampaignCreate,
    EmailCampaignResponse,
    SendTestEmailRequest,
    EmailLogResponse,
    RecipientPreviewResponse,
    RecipientFilterEnum,
    OAuthStatusResponse,
)
from app.services.gmail_service import gmail_service
from app.services.email_service import EmailService
from app.templates.email_templates import get_all_templates, render_template
from app.models.email_campaign import RecipientFilter

router = APIRouter(prefix="/api/email", tags=["email"])


# ==================== OAuth ====================


@router.get("/oauth/status", response_model=OAuthStatusResponse)
def get_oauth_status():
    """檢查 OAuth 授權狀態"""
    is_configured = gmail_service.is_configured()
    is_authenticated = gmail_service.is_authenticated()
    user_email = None
    message = ""

    if not is_configured:
        message = "請先在 .env 設定 GOOGLE_CLIENT_ID 和 GOOGLE_CLIENT_SECRET"
    elif not is_authenticated:
        message = "請點擊授權按鈕連結 Gmail"
    else:
        user_email = gmail_service.get_user_email()
        message = f"已連結 Gmail: {user_email}"

    return OAuthStatusResponse(
        is_configured=is_configured,
        is_authenticated=is_authenticated,
        user_email=user_email,
        message=message,
    )


@router.get("/oauth/authorize")
def authorize_gmail():
    """重定向到 Google OAuth 授權頁面"""
    if not gmail_service.is_configured():
        raise HTTPException(status_code=400, detail="OAuth 尚未設定")
    auth_url = gmail_service.get_authorization_url()
    return RedirectResponse(url=auth_url)


@router.get("/oauth/callback")
def oauth_callback(request: Request):
    """OAuth 回調處理"""
    authorization_response = str(request.url)
    success = gmail_service.handle_oauth_callback(authorization_response)

    if success:
        # 授權成功，重定向回前端
        return RedirectResponse(url="/?tab=email&oauth=success")
    else:
        return RedirectResponse(url="/?tab=email&oauth=failed")


@router.post("/oauth/revoke")
def revoke_oauth():
    """撤銷 OAuth 授權"""
    success = gmail_service.revoke_credentials()
    if success:
        return {"success": True, "message": "已撤銷授權"}
    raise HTTPException(status_code=500, detail="撤銷授權失敗")


# ==================== 範本 ====================


@router.get("/templates", response_model=EmailTemplateListResponse)
def list_templates():
    """取得所有郵件範本"""
    templates = get_all_templates()
    template_list = [
        EmailTemplateInfo(
            id=t.id,
            name=t.name,
            description=t.description,
            subject_template=t.subject_template,
            preview_text=t.text_template[:100] + "..." if len(t.text_template) > 100 else t.text_template,
        )
        for t in templates.values()
    ]
    return EmailTemplateListResponse(templates=template_list)


@router.post("/templates/preview", response_model=EmailTemplatePreviewResponse)
def preview_template(request: EmailTemplatePreview):
    """預覽郵件範本"""
    rendered = render_template(request.template_id, request.customer_name)
    if not rendered:
        raise HTTPException(status_code=404, detail=f"找不到範本: {request.template_id}")

    return EmailTemplatePreviewResponse(
        subject=rendered["subject"],
        html_content=rendered["html"],
        text_content=rendered["text"],
    )


# ==================== 收件人 ====================


@router.get("/recipients/preview", response_model=RecipientPreviewResponse)
def preview_recipients(
    filter: RecipientFilterEnum = RecipientFilterEnum.ALL,
    db: Session = Depends(get_db),
):
    """預覽收件人列表"""
    service = EmailService(db)
    # 轉換 schema enum 到 model enum
    model_filter = RecipientFilter(filter.value)
    result = service.get_recipients_preview(model_filter)
    return RecipientPreviewResponse(**result)


# ==================== 活動 ====================


@router.post("/campaigns", response_model=EmailCampaignResponse)
def create_campaign(
    campaign: EmailCampaignCreate,
    db: Session = Depends(get_db),
):
    """建立郵件活動"""
    service = EmailService(db)
    model_filter = RecipientFilter(campaign.recipient_filter.value)
    created = service.create_campaign(
        name=campaign.name,
        subject=campaign.subject,
        content_html=campaign.content_html,
        content_text=campaign.content_text,
        template_id=campaign.template_id,
        recipient_filter=model_filter,
        recipient_mode=campaign.recipient_mode,
        recipient_ids=campaign.recipient_ids,
        scheduled_at=campaign.scheduled_at,
    )
    return created


@router.get("/campaigns", response_model=List[EmailCampaignResponse])
def list_campaigns(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db),
):
    """取得活動列表"""
    service = EmailService(db)
    return service.get_campaigns(skip=skip, limit=limit)


@router.get("/campaigns/{campaign_id}", response_model=EmailCampaignResponse)
def get_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    """取得單一活動"""
    service = EmailService(db)
    campaign = service.get_campaign(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="找不到活動")
    return campaign


@router.post("/campaigns/{campaign_id}/send")
def send_campaign(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    """發送活動郵件"""
    service = EmailService(db)
    result = service.send_campaign(campaign_id)
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


@router.get("/campaigns/{campaign_id}/logs", response_model=List[EmailLogResponse])
def get_campaign_logs(
    campaign_id: UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
):
    """取得活動的發送紀錄"""
    service = EmailService(db)
    return service.get_email_logs(campaign_id=campaign_id, skip=skip, limit=limit)


# ==================== 測試郵件 ====================


@router.post("/test")
def send_test_email(
    request: SendTestEmailRequest,
    db: Session = Depends(get_db),
):
    """發送測試郵件"""
    service = EmailService(db)
    result = service.send_test_email(
        template_id=request.template_id,
        recipient_email=request.recipient_email,
        recipient_name=request.recipient_name,
    )
    if not result["success"]:
        raise HTTPException(status_code=400, detail=result["error"])
    return result


# ==================== 開信追蹤 ====================

# 1x1 透明 PNG 圖片（base64）
TRANSPARENT_PIXEL = bytes([
    0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A, 0x00, 0x00, 0x00, 0x0D,
    0x49, 0x48, 0x44, 0x52, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
    0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4, 0x89, 0x00, 0x00, 0x00,
    0x0A, 0x49, 0x44, 0x41, 0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,
    0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00, 0x00, 0x00, 0x00, 0x49,
    0x45, 0x4E, 0x44, 0xAE, 0x42, 0x60, 0x82
])


@router.get("/track/{pixel_token}.png")
def track_email_open(
    pixel_token: str,
    db: Session = Depends(get_db),
):
    """追蹤郵件開啟（回傳 1x1 透明 PNG）"""
    service = EmailService(db)
    service.record_email_open(pixel_token)

    return Response(
        content=TRANSPARENT_PIXEL,
        media_type="image/png",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
        }
    )


@router.get("/campaigns/{campaign_id}/stats")
def get_campaign_stats(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    """取得活動統計（開信率等）"""
    service = EmailService(db)
    stats = service.get_campaign_stats(campaign_id)
    if not stats:
        raise HTTPException(status_code=404, detail="找不到活動")
    return stats


# ==================== 排程 ====================


@router.post("/campaigns/{campaign_id}/schedule")
def schedule_campaign(
    campaign_id: UUID,
    scheduled_at: datetime,
    db: Session = Depends(get_db),
):
    """設定或更新活動排程"""
    service = EmailService(db)
    campaign = service.update_campaign_schedule(campaign_id, scheduled_at)
    if not campaign:
        raise HTTPException(status_code=400, detail="無法設定排程（活動可能已發送或不存在）")
    return {"success": True, "scheduled_at": campaign.scheduled_at}


@router.delete("/campaigns/{campaign_id}/schedule")
def cancel_campaign_schedule(
    campaign_id: UUID,
    db: Session = Depends(get_db),
):
    """取消活動排程"""
    service = EmailService(db)
    campaign = service.cancel_campaign_schedule(campaign_id)
    if not campaign:
        raise HTTPException(status_code=400, detail="無法取消排程")
    return {"success": True, "message": "排程已取消"}


@router.get("/scheduler/status")
def get_scheduler_status():
    """取得排程器狀態"""
    from app.services.scheduler_service import scheduler_service
    jobs = scheduler_service.get_scheduled_jobs()
    return {
        "running": scheduler_service._started,
        "jobs": jobs
    }
