import json
import logging
import os

from aiogram import types
from aiogram.exceptions import TelegramBadRequest
from config import bot

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VOICE_PATH = os.getenv("VOICE_PATH") or os.path.join(BASE_DIR, "voice", "welcome.ogg")
FILE_ID_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "voice_file_ids.json")
UPLOAD_TIMEOUT = 300


if not os.path.exists(FILE_ID_PATH):
    with open(FILE_ID_PATH, "w", encoding="utf-8") as f:
        json.dump({}, f)


def load_voice_ids():
    try:
        with open(FILE_ID_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def save_voice_ids(data):
    with open(FILE_ID_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f)


async def send_welcome_voice(user_id):
    data = load_voice_ids()
    file_id = data.get("welcome")

    if file_id:
        try:
            await bot.send_voice(chat_id=user_id, voice=file_id)
            return
        except TelegramBadRequest:
            data.pop("welcome", None)

    if not os.path.exists(VOICE_PATH):
        logging.warning("Welcome voice file not found: %s", VOICE_PATH)
        return

    msg = await bot.send_voice(
        chat_id=user_id,
        voice=types.FSInputFile(VOICE_PATH),
        request_timeout=UPLOAD_TIMEOUT
    )

    if msg.voice:
        data["welcome"] = msg.voice.file_id
        save_voice_ids(data)


async def try_send_welcome_voice(user_id):
    try:
        await send_welcome_voice(user_id)
    except Exception:
        logging.exception("Voice Error")