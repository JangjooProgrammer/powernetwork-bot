from aiogram import types, filters, F
from config import dp, bot
from base import manager_key, user_key, get_user_by_id, insertinto_accounts,   submit_coach_request, registration_key, has_completed_videos
import logging
import asyncio, database, video, manager, form, voice, group_topic, helper

logging.basicConfig(filename='main.log', level=logging.INFO, filemode='a', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@dp.message(filters.CommandStart())
async def start_with_login(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    user = get_user_by_id(user_id)

    if user is None:
        insertinto_accounts((user_id, username, first_name, 0, 0))
        user = get_user_by_id(user_id)

    if user[3] == 1:
        await message.reply(
            text="به پنل مدیریت ربات پاورنتورک خوش آمدید. شما ادمین هستید.",
            reply_markup=manager_key
        )
    
    elif user[4] == 1:
        await message.reply(
                    text="به ربات پاورنتورک خوش آمدید شما کوچ هستید",
                    reply_markup=None
                )
        
    else:
        name = (
            f'<a href="tg://user?id={user_id}">'
            f'{first_name or "کاربر عزیز"}'
            f'</a>'
        )

        text = f"""
🌟 <b>سلام {name} جان به سوپرگروه PowerNetwork خوش اومدی!</b>

خیلی خوشحالیم که به جمع ما اضافه شدی. 🤝

اینجا قراره کنار آدم‌های هم‌مسیر رشد کنیم، ارتباطات ارزشمند بسازیم و با کمک هم به نسخه قوی‌تری از خودمون تبدیل بشیم. 🚀

🎬 <b>قبل از هر فعالیتی، لطفاً دو ویدیوی زیر رو با دقت و به‌طور کامل تماشا کن.</b>

این ویدیوها بهت کمک می‌کنن با فضای گروه، قوانین و نحوه فعالیت آشنا بشی و بدونی چطور می‌تونی بیشترین بهره رو از این جمع ببری.

📝 <b>بعد از تماشای ویدیوها، طبق فرم مشخص‌شده خودت رو کامل معرفی کن</b> تا سایر اعضا بیشتر باهات آشنا بشن و بتونیم ارتباط بهتری با هم داشته باشیم.

💪 به جمع حرفه‌ای‌های <b>PowerNetwork</b> خوش اومدی!

✨ <i>اینجا مسیر رشد رو در کنار هم طی می‌کنیم.</i>
"""
        completed = has_completed_videos(user_id)
        keyboard = registration_key if completed else user_key
        await message.reply(text=text, reply_markup=keyboard, parse_mode="HTML")

        if not completed:
            await video.send_first_video(message)

@dp.message(F.text == "اقدام برای کوچ")
async def apply_for_coach(message: types.Message):

    result = submit_coach_request(message.from_user.id)

    if result == "no_form":
        await message.answer(
            "❌ ابتدا باید فرم معرفی اعضا را تکمیل کنید."
        )

    elif result == "already_pending":
        await message.answer(
            "درخواست شما قبلاً ثبت شده است. لطفاً منتظر بررسی ادمین باشید."
        )

    elif result == "already_assigned":
        await message.answer(
            "شما قبلاً به یک کوچ اختصاص داده شده‌اید."
        )

    elif result == "completed":
        await message.answer(
            "درخواست قبلی شما رسیدگی شده است."
        )

    elif result == "submitted":
        await message.answer(
            "✅ درخواست اقدام برای کوچ شما با موفقیت ثبت شد.\n\n"
            "منتظر کوچ‌های قدرتمند مجموعه باشید 💪"
        )

    else:
        await message.answer(
            "❌ در ثبت درخواست مشکلی پیش آمد. لطفاً با پشتیبانی تماس بگیرید."
        )
        
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())