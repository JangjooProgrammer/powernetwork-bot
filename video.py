import json
import logging
import os
from aiogram import F, types
from aiogram.exceptions import TelegramBadRequest
from config import vid_router, bot
from base import set_videos_completed, registration_key

FILE_IDS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "video_file_ids.json")
VIDEO_KEYS = ("video1", "video2")

processing_users = set()


def load_file_ids():
    try:
        with open(FILE_IDS_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def seen_keyboard(callback_data):
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="✅ ویدیو را دیدم", callback_data=callback_data)]
    ])


async def remove_buttons(message):
    try:
        await message.edit_reply_markup(reply_markup=None)
    except (TelegramBadRequest, AttributeError):
        pass


async def remove_message(message):
    try:
        await message.delete()
    except (TelegramBadRequest, AttributeError):
        await remove_buttons(message)


async def send_first_video(message: types.Message):
    file_ids = load_file_ids()

    if not all(file_ids.get(key) for key in VIDEO_KEYS):
        logging.error("Video file_ids are missing in %s", FILE_IDS_PATH)
        await message.answer("❌ ویدیوها هنوز آماده نشده‌اند. لطفاً کمی بعد دوباره /start را بزنید.")
        return

    try:
        await message.answer(
            "🎬 الان یک ویدیوی معرفی برایت ارسال می‌کنیم.\n\n"
            "لطفاً آن را کامل ببین و بعد زیرش روی «ویدیو را دیدم» بزن."
        )
        await message.answer_video(video=file_ids["video1"], reply_markup=seen_keyboard("video1_seen"))
    except Exception:
        logging.exception("Video Error")
        await message.answer("❌ در ارسال ویدیو مشکلی پیش آمد. لطفاً دوباره /start را بزنید.")


@vid_router.callback_query(F.data == "video1_seen")
async def video1_seen(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in processing_users:
        await callback.answer()
        return

    processing_users.add(user_id)

    try:
        await callback.answer("ویدیوی دوم در حال ارسال است...")
        file_ids = load_file_ids()
        await bot.send_video(chat_id=user_id, video=file_ids["video2"], reply_markup=seen_keyboard("video2_seen"))
        await remove_message(callback.message)
    except Exception:
        logging.exception("Video Error")
        await bot.send_message(
            chat_id=user_id,
            text="❌ در ارسال ویدیو مشکلی پیش آمد. لطفاً دوباره روی «ویدیو را دیدم» بزنید."
        )
    finally:
        processing_users.discard(user_id)


@vid_router.callback_query(F.data == "video2_seen")
async def video2_seen(callback: types.CallbackQuery):
    user_id = callback.from_user.id

    if user_id in processing_users:
        await callback.answer()
        return

    processing_users.add(user_id)

    try:
        await callback.answer()
        set_videos_completed(user_id)
        await bot.send_message(
            chat_id=user_id,
            text=(
                "✅ ویدیوهای شروع را دیدی.\n\n"
                "حالا اول روی «ثبت نام» بزن و فرم معرفی را تکمیل کن، بعد روی «عضویت در گروه» بزن."
            ),
            reply_markup=registration_key
        )
        await remove_message(callback.message)
    except Exception:
        logging.exception("Video Error")
    finally:
        processing_users.discard(user_id)
