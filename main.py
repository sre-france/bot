import os
from telegram.client import Telegram

API_ID = os.getenv("API_ID")
API_HASH = os.getenv("API_HASH")
BOT_TOKEN = os.getenv("BOT_TOKEN")
ENC_KEY = os.getenv("ENC_KEY")

tg = Telegram(
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    database_encryption_key=ENC_KEY,
)


def search_and_kick_out_spammers(update):
    msg_type = update["message"]["content"]["@type"]
    if msg_type == "messageChatAddMembers":
        chat_id = update["message"]["chat_id"]
        user_id = update["message"]["sender_user_id"]
        new_users = update["message"]["content"]["member_user_ids"]
        # Kick this user out of the group
        if user_id in new_users:
            params = {
                "chat_id": chat_id,
                "user_id": user_id,
                "status": {"@type": "chatMemberStatusBanned"},
            }
            result = tg.call_method("setChatMemberStatus", params=params, block=True)
    elif msg_type == "messageText":
        text = update["message"]["content"]["text"]["text"]
        # Defaut answer for the mandatory command /start
        if text == "/start":
            chat_id = update["message"]["chat_id"]
            msg = "Sorry, I have no powers here. I can only moderate a Telegram location-based group"
            tg.send_message(
                chat_id=chat_id, text=msg,
            )


if __name__ == "__main__":
    tg.login()
    tg.add_message_handler(search_and_kick_out_spammers)
    tg.idle()
