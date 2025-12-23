from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.email_campaign import EmailCampaign, CampaignStatus
from app.services.email_service import EmailService


class SchedulerService:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self._started = False

    def start(self):
        """啟動排程器"""
        if self._started:
            return

        # 每分鐘檢查待發送的排程活動
        self.scheduler.add_job(
            self._check_scheduled_campaigns,
            trigger=IntervalTrigger(minutes=1),
            id="check_scheduled_campaigns",
            name="檢查排程活動",
            replace_existing=True,
        )

        self.scheduler.start()
        self._started = True
        print("排程器已啟動")

    def stop(self):
        """停止排程器"""
        if self._started:
            self.scheduler.shutdown()
            self._started = False
            print("排程器已停止")

    def _check_scheduled_campaigns(self):
        """檢查並執行到期的排程活動"""
        db: Session = SessionLocal()
        try:
            # 查找所有已到期的排程活動（使用本地時間比對）
            now = datetime.now()
            print(f"[排程檢查] 目前時間: {now}")
            campaigns = db.query(EmailCampaign).filter(
                EmailCampaign.status == CampaignStatus.SCHEDULED,
                EmailCampaign.scheduled_at <= now
            ).all()
            print(f"[排程檢查] 找到 {len(campaigns)} 個待發送活動")

            for campaign in campaigns:
                print(f"執行排程活動: {campaign.name} (ID: {campaign.id})")
                service = EmailService(db)
                result = service.send_campaign(campaign.id)
                if result["success"]:
                    print(f"活動 {campaign.name} 發送完成: {result['sent_count']} 成功, {result['failed_count']} 失敗")
                else:
                    print(f"活動 {campaign.name} 發送失敗: {result.get('error', '未知錯誤')}")

        except Exception as e:
            print(f"排程檢查錯誤: {e}")
        finally:
            db.close()

    def get_scheduled_jobs(self):
        """取得所有排程任務"""
        return [
            {
                "id": job.id,
                "name": job.name,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
            }
            for job in self.scheduler.get_jobs()
        ]


# 全域實例
scheduler_service = SchedulerService()
