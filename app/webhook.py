from typing import Union

from fastapi import HTTPException, APIRouter, Request
from pydantic import BaseModel
from dotenv import load_dotenv

import os
import logging
import requests

from app.database import database

load_dotenv()

# Define your Telegram bot token
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
WEBHOOK_URL = os.getenv('BASE_URL') + "/webhook"


router = APIRouter()

class Update(BaseModel):
    update_id: int
    message: dict


@router.post("", tags=["telegram"])
async def webhook(update: Update):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

    if update.message.get("text").startswith("/start refId"):
        telegram_id = update.message.get("from").get("id")

        user_id = await database.fetchrow(
            """
            SELECT user_id
            FROM public."user"
            WHERE telegram_id = $1
            """, telegram_id
        )

        if user_id is None:

            ref_id = update.message.get("text").split(" ")[1][5:]

            await database.execute(
                """
                UPDATE public.friend_for
                SET list_of_ids = array_append(list_of_ids, $2)
                WHERE user_id = (
                                    SELECT user_id
                                    FROM public."user"
                                    WHERE telegram_id = $1
                                )       
                """, ref_id, telegram_id
            )

            payload = {
                "chat_id": ref_id,
                "text": f"You have just get subscriber by ID: {telegram_id}!",
            }

            requests.post(url, json=payload)

    if update.message.get("text").startswith("/help"):
        pass

    reply_markup = {
        "inline_keyboard": [[{
            "text": "go to game",
            "web_app": {"url":"https://telegramminiapp-seven.vercel.app/"}
        }]]
    }

    payload = {
        "chat_id": update.message.get('from').get('id'),
        "text": ,
        "reply_markup": reply_markup,
    }

    response = requests.post(url, json=payload)
    return {"Status": "ok"}


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
