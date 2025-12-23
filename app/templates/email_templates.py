from typing import Dict, Optional
from dataclasses import dataclass


@dataclass
class EmailTemplate:
    id: str
    name: str
    description: str
    subject_template: str
    html_template: str
    text_template: str


HOLIDAY_TEMPLATES: Dict[str, EmailTemplate] = {
    "double11": EmailTemplate(
        id="double11",
        name="雙11 購物節",
        description="雙11 年度購物節促銷郵件",
        subject_template="{customer_name}，雙11 限時優惠等你來！",
        html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #ff6b6b, #ff4757); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 36px; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333; margin-bottom: 20px; }}
        .offer-box {{ background-color: #fff5f5; border: 2px dashed #ff4757; padding: 20px; text-align: center; margin: 20px 0; border-radius: 10px; }}
        .offer-box .discount {{ font-size: 48px; color: #ff4757; font-weight: bold; }}
        .footer {{ background-color: #333; color: #999; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>雙 11 購物節</h1>
        </div>
        <div class="content">
            <p class="greeting">親愛的 {customer_name}，您好！</p>
            <p>一年一度的雙11購物節來了！我們為您準備了專屬優惠：</p>
            <div class="offer-box">
                <div class="discount">全館 8 折</div>
                <p>限時 24 小時，錯過等明年！</p>
            </div>
            <p>感謝您一直以來的支持，祝您購物愉快！</p>
        </div>
        <div class="footer">
            <p>此郵件由 CRM 系統自動發送</p>
        </div>
    </div>
</body>
</html>
        """,
        text_template="""
親愛的 {customer_name}，您好！

雙11購物節來了！

一年一度的雙11購物節開跑，我們為您準備了專屬優惠：
- 全館商品 8 折優惠
- 限時 24 小時

感謝您一直以來的支持！
        """
    ),

    "christmas": EmailTemplate(
        id="christmas",
        name="聖誕節",
        description="聖誕節祝福與促銷郵件",
        subject_template="{customer_name}，聖誕快樂！獨家優惠等你拿",
        html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #2d5016, #4a7c23); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 0; font-size: 32px; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333; margin-bottom: 20px; }}
        .gift-box {{ background-color: #f8fff5; border: 2px solid #4a7c23; padding: 25px; text-align: center; margin: 20px 0; border-radius: 10px; }}
        .footer {{ background-color: #2d5016; color: #a8d080; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-size: 40px;">🎄</div>
            <h1>Merry Christmas!</h1>
        </div>
        <div class="content">
            <p class="greeting">親愛的 {customer_name}，聖誕快樂！</p>
            <p>在這個溫馨的季節，我們想對您說聲感謝。感謝您這一年來的支持與信任！</p>
            <div class="gift-box">
                <div style="font-size: 60px;">🎁</div>
                <div style="font-size: 18px; color: #2d5016; margin-top: 15px;">送您一份聖誕驚喜<br>結帳輸入 <strong>XMAS2024</strong> 享 9 折優惠</div>
            </div>
            <p>願您與家人共度美好時光，新的一年幸福滿滿！</p>
        </div>
        <div class="footer">
            <p>祝您聖誕快樂，新年如意！</p>
        </div>
    </div>
</body>
</html>
        """,
        text_template="""
親愛的 {customer_name}，聖誕快樂！

在這個溫馨的季節，我們想對您說聲感謝。
感謝您這一年來的支持與信任！

送您聖誕驚喜：
結帳輸入 XMAS2024 享 9 折優惠

願您與家人共度美好時光，新的一年幸福滿滿！
        """
    ),

    "lunar_new_year": EmailTemplate(
        id="lunar_new_year",
        name="農曆新年",
        description="農曆新年賀歲郵件",
        subject_template="{customer_name}，新年快樂！蛇年行大運",
        html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #c41e3a, #8b0000); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: #ffd700; margin: 0; font-size: 36px; }}
        .content {{ padding: 40px 30px; background: linear-gradient(to bottom, #fff9f9, #ffffff); }}
        .greeting {{ font-size: 18px; color: #333; margin-bottom: 20px; }}
        .blessing-box {{ background-color: #c41e3a; color: #ffd700; padding: 25px; text-align: center; margin: 20px 0; border-radius: 10px; }}
        .footer {{ background-color: #c41e3a; color: #ffd700; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>恭賀新禧</h1>
            <div style="color: #ffd700; font-size: 24px; margin-top: 10px;">🐍 蛇年行大運 🐍</div>
        </div>
        <div class="content">
            <p class="greeting">親愛的 {customer_name}，新年快樂！</p>
            <p>值此新春佳節，我們全體同仁向您致上最誠摯的祝福：</p>
            <div class="blessing-box">
                <div style="font-size: 24px; line-height: 1.8;">
                    🧧 恭喜發財 🧧<br>
                    萬事如意 • 心想事成<br>
                    闔家平安 • 身體健康
                </div>
            </div>
            <div style="text-align: center; margin: 30px 0;">
                <div style="font-size: 60px;">🧧</div>
                <p style="color: #c41e3a; font-size: 18px;">新春開運紅包<br>全館滿 1000 折 100</p>
            </div>
        </div>
        <div class="footer">
            <p>恭祝 新年快樂 財源廣進！</p>
        </div>
    </div>
</body>
</html>
        """,
        text_template="""
親愛的 {customer_name}，新年快樂！

值此新春佳節，我們全體同仁向您致上最誠摯的祝福：

🧧 恭喜發財 🧧
萬事如意 • 心想事成
闔家平安 • 身體健康

新春開運紅包
全館滿 1000 折 100

恭祝 新年快樂 財源廣進！
        """
    ),

    "mid_autumn": EmailTemplate(
        id="mid_autumn",
        name="中秋節",
        description="中秋節祝福郵件",
        subject_template="{customer_name}，中秋佳節愉快！",
        html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; padding: 0; background-color: #f5f5f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #1a237e, #311b92); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: #ffd54f; margin: 10px 0 0 0; font-size: 32px; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333; margin-bottom: 20px; }}
        .moon-box {{ background: linear-gradient(to bottom, #fff8e1, #ffffff); border: 2px solid #ffd54f; padding: 25px; text-align: center; margin: 20px 0; border-radius: 50px; }}
        .footer {{ background-color: #1a237e; color: #b39ddb; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-size: 80px;">🌕</div>
            <h1>中秋佳節愉快</h1>
        </div>
        <div class="content">
            <p class="greeting">親愛的 {customer_name}，中秋節快樂！</p>
            <p>月圓人團圓，在這個充滿溫馨的節日，願您與家人共享天倫之樂。</p>
            <div class="moon-box">
                <p style="font-size: 20px; color: #1a237e;">🥮 中秋限定優惠 🥮</p>
                <p style="font-size: 16px; color: #666;">活動期間購物享免運優惠</p>
            </div>
            <p>感謝您的支持，祝您佳節愉快、闔家歡樂！</p>
        </div>
        <div class="footer">
            <p>但願人長久，千里共嬋娟</p>
        </div>
    </div>
</body>
</html>
        """,
        text_template="""
親愛的 {customer_name}，中秋節快樂！

月圓人團圓，在這個充滿溫馨的節日，
願您與家人共享天倫之樂。

🥮 中秋限定優惠
活動期間購物享免運優惠

感謝您的支持，祝您佳節愉快、闔家歡樂！
        """
    ),

    "valentines": EmailTemplate(
        id="valentines",
        name="情人節",
        description="情人節促銷郵件",
        subject_template="{customer_name}，情人節快樂！",
        html_template="""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Microsoft JhengHei', Arial, sans-serif; margin: 0; padding: 0; background-color: #fff0f5; }}
        .container {{ max-width: 600px; margin: 0 auto; background-color: #ffffff; }}
        .header {{ background: linear-gradient(135deg, #ff69b4, #ff1493); padding: 40px 20px; text-align: center; }}
        .header h1 {{ color: white; margin: 10px 0 0 0; font-size: 32px; }}
        .content {{ padding: 40px 30px; }}
        .greeting {{ font-size: 18px; color: #333; margin-bottom: 20px; }}
        .love-box {{ background-color: #fff0f5; border: 2px solid #ff69b4; padding: 25px; text-align: center; margin: 20px 0; border-radius: 20px; }}
        .footer {{ background-color: #ff69b4; color: white; padding: 20px; text-align: center; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <div style="font-size: 40px;">💕 💖 💕</div>
            <h1>Happy Valentine's Day</h1>
        </div>
        <div class="content">
            <p class="greeting">親愛的 {customer_name}，情人節快樂！</p>
            <p>在這個充滿愛的日子，願您與心愛的人共度美好時光。</p>
            <div class="love-box">
                <p style="font-size: 24px; color: #ff1493;">💝 情人節限定 💝</p>
                <p style="font-size: 16px; color: #666;">雙人套餐 8 折優惠<br>訂購即贈精美禮品包裝</p>
            </div>
        </div>
        <div class="footer">
            <p>Love is in the air 💕</p>
        </div>
    </div>
</body>
</html>
        """,
        text_template="""
親愛的 {customer_name}，情人節快樂！

在這個充滿愛的日子，願您與心愛的人共度美好時光。

💝 情人節限定
雙人套餐 8 折優惠
訂購即贈精美禮品包裝
        """
    ),
}


def get_template(template_id: str) -> Optional[EmailTemplate]:
    return HOLIDAY_TEMPLATES.get(template_id)


def get_all_templates() -> Dict[str, EmailTemplate]:
    return HOLIDAY_TEMPLATES


def render_template(template_id: str, customer_name: str = "親愛的顧客") -> Optional[dict]:
    template = get_template(template_id)
    if not template:
        return None

    return {
        "subject": template.subject_template.format(customer_name=customer_name),
        "html": template.html_template.format(customer_name=customer_name),
        "text": template.text_template.format(customer_name=customer_name),
    }
