"""Helper: send a video to your bot and it replies with the video's file_id.

Telegram file_ids belong to one bot, so they must be taken from the same bot that
will use them. Copy the ids into video_file_ids.json (see video_file_ids.example.json).

Run it only while main.py is stopped (two polling instances of one bot conflict):
    python get_file_id.py
"""
import asyncio

from aiogram import Dispatcher, F, types

from config import bot

dp = Dispatcher()


@dp.message(F.video)
async def show_video_id(message: types.Message):
    await message.reply(f"<code>{message.video.file_id}</code>", parse_mode="HTML")


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
