from fastapi import HTTPException, APIRouter
from pydantic import BaseModel
import logging
import requests


# Define your Telegram bot token
TELEGRAM_BOT_TOKEN = "1797534752:AAGA1qFWEWXSnyxUOd6sJZqCi2j0BxU1EJg"
WEBHOOK_URL = f"https://8cd4-89-107-97-177.ngrok-free.app/webhook/{TELEGRAM_BOT_TOKEN}"


router = APIRouter()

class Update(BaseModel):
    update_id: int
    message: dict


@router.post(f"/{TELEGRAM_BOT_TOKEN}")
async def webhook(update: Update):
    logging.info(update)

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    reply_markup = {
        "inline_keyboard": [[{
            "text": "go to game",
            "web_app": {"url":"https://windbnb-seven-blue.vercel.app"}
        }]]
    }

    payload = {
        "chat_id": update.message.get('from').get('id'),
        "text": """
            How to play Coin Earn ⚡️
    
💰 Tap to earn
Tap the screen and collect coins.

⛏ Mine
Upgrade cards that will give you passive income opportunities.

⏰ Profit per hour
The exchange will work for you on its own, even when you are not in the game for 3 hours.
Then you need to log in to the game again.

📈 LVL
The more coins you have on your balance, the higher the level of your exchange is and the faster you can earn more coins.

👥 Friends
Invite your friends and you’ll get bonuses. Help a friend move to the next leagues and you'll get even more bonuses.

🪙 Token listing
At the end of the season, a token will be released and distributed among the players.
Dates will be announced in our announcement channel. Stay tuned!

/help to get this guide
        """,
        "reply_markup": reply_markup,
    }

    response = requests.post(url, json=payload)
    logging.info(response)
    return {"status": "ok"}

@router.on_event("startup")
async def on_startup():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/setWebhook"
    payload = {"url": WEBHOOK_URL}
    response = requests.post(url, json=payload)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to set webhook")
    logging.info(f"Webhook set: {WEBHOOK_URL}")
    print(f"Webhook set: {WEBHOOK_URL}")

@router.on_event("shutdown")
async def on_shutdown():
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/deleteWebhook"
    response = requests.post(url)
    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail="Failed to delete webhook")
    logging.info("Webhook deleted")

@router.get("/")
async def root():
    return {"message": "Hello World, you are at telegram webhook"}