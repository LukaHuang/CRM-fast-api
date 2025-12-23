import os
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Tuple
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from app.config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    GOOGLE_REDIRECT_URI,
    GMAIL_TOKEN_PATH,
)

# 允許本地開發使用 HTTP（生產環境請移除）
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

SCOPES = [
    "https://www.googleapis.com/auth/gmail.send",
    "https://www.googleapis.com/auth/gmail.readonly",
]


class GmailService:
    def __init__(self):
        self.credentials: Optional[Credentials] = None
        self._load_credentials()

    def _get_client_config(self) -> dict:
        """取得 OAuth 客戶端設定"""
        return {
            "web": {
                "client_id": GOOGLE_CLIENT_ID,
                "client_secret": GOOGLE_CLIENT_SECRET,
                "redirect_uris": [GOOGLE_REDIRECT_URI],
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
            }
        }

    def _load_credentials(self):
        """從檔案載入已存的憑證"""
        if os.path.exists(GMAIL_TOKEN_PATH):
            try:
                with open(GMAIL_TOKEN_PATH, "r") as f:
                    token_data = json.load(f)
                self.credentials = Credentials(
                    token=token_data.get("token"),
                    refresh_token=token_data.get("refresh_token"),
                    token_uri=token_data.get("token_uri"),
                    client_id=token_data.get("client_id"),
                    client_secret=token_data.get("client_secret"),
                    scopes=token_data.get("scopes"),
                )
            except Exception as e:
                print(f"載入憑證失敗: {e}")
                self.credentials = None

    def _save_credentials(self):
        """儲存憑證到檔案"""
        if self.credentials:
            os.makedirs(os.path.dirname(GMAIL_TOKEN_PATH), exist_ok=True)
            token_data = {
                "token": self.credentials.token,
                "refresh_token": self.credentials.refresh_token,
                "token_uri": self.credentials.token_uri,
                "client_id": self.credentials.client_id,
                "client_secret": self.credentials.client_secret,
                "scopes": self.credentials.scopes,
            }
            with open(GMAIL_TOKEN_PATH, "w") as f:
                json.dump(token_data, f)

    def is_configured(self) -> bool:
        """檢查 OAuth 是否已設定"""
        return bool(GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET)

    def is_authenticated(self) -> bool:
        """檢查是否已完成授權"""
        return self.credentials is not None and self.credentials.valid

    def get_authorization_url(self) -> str:
        """取得 OAuth 授權 URL"""
        flow = Flow.from_client_config(
            self._get_client_config(),
            scopes=SCOPES,
            redirect_uri=GOOGLE_REDIRECT_URI,
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent",
        )
        return auth_url

    def handle_oauth_callback(self, authorization_response: str) -> bool:
        """處理 OAuth 回調"""
        try:
            flow = Flow.from_client_config(
                self._get_client_config(),
                scopes=SCOPES,
                redirect_uri=GOOGLE_REDIRECT_URI,
            )
            flow.fetch_token(authorization_response=authorization_response)
            self.credentials = flow.credentials
            self._save_credentials()
            return True
        except Exception as e:
            print(f"OAuth 回調處理失敗: {e}")
            return False

    def revoke_credentials(self) -> bool:
        """撤銷授權"""
        try:
            if os.path.exists(GMAIL_TOKEN_PATH):
                os.remove(GMAIL_TOKEN_PATH)
            self.credentials = None
            return True
        except Exception as e:
            print(f"撤銷授權失敗: {e}")
            return False

    def get_user_email(self) -> Optional[str]:
        """取得已授權的 Gmail 帳號"""
        if not self.is_authenticated():
            return None
        try:
            service = build("gmail", "v1", credentials=self.credentials)
            profile = service.users().getProfile(userId="me").execute()
            return profile.get("emailAddress")
        except HttpError as e:
            print(f"取得用戶信箱失敗: {e}")
            return None

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None,
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        發送郵件

        Returns:
            Tuple[bool, Optional[str], Optional[str]]: (成功, message_id, 錯誤訊息)
        """
        if not self.is_authenticated():
            return False, None, "Gmail 尚未授權"

        try:
            service = build("gmail", "v1", credentials=self.credentials)

            # 建立 MIME 郵件
            message = MIMEMultipart("alternative")
            message["to"] = to_email
            message["subject"] = subject

            # 加入純文字版本
            if text_content:
                text_part = MIMEText(text_content, "plain", "utf-8")
                message.attach(text_part)

            # 加入 HTML 版本
            html_part = MIMEText(html_content, "html", "utf-8")
            message.attach(html_part)

            # 編碼郵件
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

            # 發送
            sent_message = (
                service.users()
                .messages()
                .send(userId="me", body={"raw": raw_message})
                .execute()
            )

            return True, sent_message.get("id"), None

        except HttpError as e:
            error_msg = f"發送失敗: {e.reason if hasattr(e, 'reason') else str(e)}"
            return False, None, error_msg
        except Exception as e:
            return False, None, f"發送失敗: {str(e)}"


# 全域實例
gmail_service = GmailService()
