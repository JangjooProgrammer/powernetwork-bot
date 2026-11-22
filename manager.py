from aiogram import Router, F, types, Bot
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from config import manager_router, bot
from base import (
    get_all_users,
    get_user_count,
    inline_url_maker,
    inline_query_maker,
    get_user_by_id,
    add_coach,
    get_all_coaches,
    remove_coach,
    get_non_coaches,
    assign_coach,
    get_form_request,
    get_pending_requests
)
import sqlite3
import asyncio
import logging
import os
import datetime
import config
        
class BroadcastState(StatesGroup):
    waiting_for_message = State()

@manager_router.message(F.text.startswith("ارسال پیام همگانی"))
async def ask_broadcast_message(message: types.Message, state: FSMContext):
    if is_admin(message.from_user.id):
        await message.answer("✍️ لطفاً متن/عکس/ویدیو پیام خود را ارسال کنید.")
        await state.set_state(BroadcastState.waiting_for_message)

@manager_router.message(BroadcastState.waiting_for_message)
async def send_broadcast(message: types.Message, state: FSMContext, bot):
    await message.reply("پیام شما در صف ارسال قرار گرفت...")
    users = get_all_users()
    success, failed = 0, 0

    for user in users:
        user_id = user[0]
        try:
            if message.text:
                await bot.send_message(chat_id=user_id, text=message.text)
            elif message.photo:
                await bot.send_photo(chat_id=user_id, photo=message.photo[-1].file_id, caption=message.caption)
            elif message.video:
                await bot.send_video(chat_id=user_id, video=message.video.file_id, caption=message.caption)
            success += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            logging.warning("Broadcast to %s failed: %s", user_id, e)
            failed += 1
            continue

    await message.answer(f"✅ پیام همگانی ارسال شد.\n\nموفق: {success} ||| ناموفق: {failed}")
    await state.clear()

@manager_router.message(F.text.startswith("آمار ربات"))
async def send_stats(message: types.Message):
    if is_admin(message.from_user.id):
        users = get_user_count()

        text = f"👥 تعداد کل کاربران: {users}\n\n"

        await message.answer(text)

@manager_router.message(F.text.startswith("لیست کاربران"))
async def list_users(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    users = get_all_users()
    if not users:
        await bot.send_message(chat_id= message.from_user.id, text= "کاربری ثبت نشده است❌")
        return

    for i in users:
        await bot.send_message(
            chat_id=message.from_user.id,
            text=f"""👤 نام کاربر: {i[2] or "ندارد"}
🆔 آیدی کاربر: {i[0]}
🎖 یوزرنیم کاربر: {i[1] or "ندارد"}"""
        )
        await asyncio.sleep(0.1)


def is_admin(user_id):
    user = get_user_by_id(user_id)
    return user is not None and user[3] == 1


def coaches_text():
    coaches = get_all_coaches()
    text = "👥 لیست کوچ های مجموعه:\n\n"

    if not coaches:
        return text + "هنوز هیچ کوچ‌ای ثبت نشده است."

    for i, coach in enumerate(coaches, 1):
        username = f"@{coach[1]}" if coach[1] else "ندارد"
        text += f"{i}. {coach[2] or 'بدون نام'}\n🆔 {coach[0]}\n👤 {username}\n\n"

    return text


def coaches_keyboard():
    coaches = get_all_coaches()
    keyboard = []

    for coach in coaches:
        name = coach[2] or coach[1] or str(coach[0])
        keyboard.append([types.InlineKeyboardButton(text=f"❌ حذف {name}", callback_data=f"remove_coach_{coach[0]}")])

    keyboard.append([types.InlineKeyboardButton(text="➕ افزودن کوچ", callback_data="add_coach_menu")])
    return types.InlineKeyboardMarkup(inline_keyboard=keyboard)


@manager_router.message(F.text.startswith("لیست کوچ ها"))
async def show_coaches(message: types.Message):
    if not is_admin(message.from_user.id):
        return

    await message.answer(coaches_text(), reply_markup=coaches_keyboard())


@manager_router.callback_query(F.data == "add_coach_menu")
async def show_users_for_coach(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی غیرمجاز", show_alert=True)
        return

    users = get_non_coaches()

    if not users:
        await callback.answer("کاربری برای اضافه کردن وجود ندارد.", show_alert=True)
        return

    keyboard = [
        [types.InlineKeyboardButton(text=f"{u[2] or u[1] or str(u[0])} | {u[0]}", callback_data=f"confirm_add_coach_{u[0]}")]
        for u in users
    ]
    keyboard.append([types.InlineKeyboardButton(text="🔙 بازگشت", callback_data="back_coach_list")])

    await callback.message.edit_text(
        "کاربر موردنظر را برای اضافه شدن به لیست کوچ ها انتخاب کن:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()


@manager_router.callback_query(F.data.startswith("confirm_add_coach_"))
async def confirm_add_coach(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی غیرمجاز", show_alert=True)
        return

    user_id = int(callback.data.split("_")[-1])

    if add_coach(user_id):
        await callback.answer("کوچ با موفقیت اضافه شد.", show_alert=True)
        await callback.message.edit_text(coaches_text(), reply_markup=coaches_keyboard())
    else:
        await callback.answer("این کاربر قابل اضافه شدن نیست.", show_alert=True)


@manager_router.callback_query(F.data.startswith("remove_coach_"))
async def confirm_remove_coach(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی غیرمجاز", show_alert=True)
        return

    user_id = int(callback.data.split("_")[-1])

    if remove_coach(user_id):
        await callback.answer("کوچ با موفقیت حذف شد.", show_alert=True)
        await callback.message.edit_text(coaches_text(), reply_markup=coaches_keyboard())
    else:
        await callback.answer("کوچ موردنظر پیدا نشد.", show_alert=True)


@manager_router.callback_query(F.data == "back_coach_list")
async def back_coach_list(callback: types.CallbackQuery):
    if not is_admin(callback.from_user.id):
        await callback.answer("دسترسی غیرمجاز", show_alert=True)
        return

    await callback.message.edit_text(coaches_text(), reply_markup=coaches_keyboard())
    await callback.answer()
    
def check_manager(user_id):
    user = get_user_by_id(user_id)
    return user is not None and user[3] == 1

@manager_router.message(F.text == "ارسال اطلاعات کوچی برای کوچ")
async def show_coach_requests(message: types.Message):
    if not check_manager(message.from_user.id):
        return

    requests = get_pending_requests()
    keyboard = []

    for req in requests:
        keyboard.append([types.InlineKeyboardButton(
            text=f"{req[2]} | {req[3]}",
            callback_data=f"select_request_{req[0]}"
        )])

    if not requests:
        await message.answer("📭 در حال حاضر درخواست در انتظار بررسی وجود ندارد.")
        return

    await message.answer(
        "📋 متقاضی موردنظر را انتخاب کن:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    )

@manager_router.callback_query(F.data.startswith("select_request_"))
async def select_coach_request(callback: types.CallbackQuery):
    if not check_manager(callback.from_user.id):
        await callback.answer("دسترسی غیرمجاز", show_alert=True)
        return

    request_id = int(callback.data.split("_")[-1])
    request = get_form_request(request_id)

    if not request or request[10] != "pending":
        await callback.answer("این درخواست دیگر در انتظار بررسی نیست.", show_alert=True)
        return

    coaches = get_all_coaches()
    if not coaches:
        await callback.answer("هیچ کوچی در ربات ثبت نشده است.", show_alert=True)
        return

    keyboard = []
    for coach in coaches:
        name = coach[2] or coach[1] or str(coach[0])
        keyboard.append([types.InlineKeyboardButton(
            text=name,
            callback_data=f"assign_{request_id}_{coach[0]}"
        )])

    await callback.message.edit_text(
        f"👤 متقاضی: {request[2]}\n🆔 شناسه: {request[1]}\n\nکوچ موردنظر را انتخاب کن:",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=keyboard)
    )
    await callback.answer()

@manager_router.callback_query(F.data.startswith("assign_"))
async def send_coach_information(callback: types.CallbackQuery):
    if not check_manager(callback.from_user.id):
        await callback.answer("دسترسی غیرمجاز", show_alert=True)
        return

    _, request_id, coach_id = callback.data.split("_")
    request_id, coach_id = int(request_id), int(coach_id)

    request = get_form_request(request_id)
    coach = get_user_by_id(coach_id)

    if not request or request[10] != "pending":
        await callback.answer("این درخواست قبلاً بررسی شده است.", show_alert=True)
        return

    if not coach or coach[4] != 1:
        await callback.answer("کوچ موردنظر معتبر نیست.", show_alert=True)
        return

    text = (
        "🎯 <b>اطلاعات متقاضی کوچ</b>\n\n"
        f"👤 نام و نام خانوادگی: {request[2]}\n"
        f"🆔 شناسه تلگرام: <code>{request[1]}</code>\n"
        f"🏙 شهر: {request[3]}\n"
        f"💡 مهارت‌ها: {request[4]}\n"
        f"🎯 حوزه‌های فعالیت: {request[5]}\n"
        f"🤝 زمینه همکاری: {request[6]}\n"
        f"🆘 کمک موردنیاز: {request[7]}\n"
        f"📞 اطلاعات تماس: {request[8]}\n"
        f"📝 توضیحات بیشتر: {request[9] or 'ندارد'}"
    )

    try:
        # ارسال اطلاعات به کوچ
        await bot.send_message(
            chat_id=coach_id,
            text=text,
            parse_mode="HTML"
        )

        # ثبت تخصیص در دیتابیس
        if not assign_coach(request_id, coach_id):
            await callback.answer(
                "ارسال انجام شد اما ثبت تخصیص در دیتابیس ناموفق بود.",
                show_alert=True
            )
            return

        await callback.message.edit_text(
            f"✅ اطلاعات {request[2]} با موفقیت برای کوچ ارسال شد."
        )
        await callback.answer("اطلاعات ارسال شد.")

    except Exception as e:
        logging.exception("Coach Send Error")
        await callback.answer(
            "ارسال اطلاعات ناموفق بود. درخواست همچنان در انتظار بررسی است.",
            show_alert=True
        )
