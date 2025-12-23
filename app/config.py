import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://localhost/crm_db")

# Gmail API 設定
GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET", "")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI", "http://localhost:8000/api/email/oauth/callback")

# 憑證檔案路徑
GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "credentials/token.json")
