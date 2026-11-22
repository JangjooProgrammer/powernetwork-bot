import re
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import StateFilter
from config import form_router, GROUP_INVITE_LINK
from base import save_form_info, has_completed_videos, has_form
from voice import try_send_welcome_voice
from group_topic import publish_member

class FormStates(StatesGroup):
    waiting_for_full_name = State()
    waiting_for_city = State()
    waiting_for_skills = State()
    waiting_for_active_fields = State()
    waiting_for_contribution = State()
    waiting_for_needed_help = State()
    waiting_for_contact = State()
    waiting_for_extra_info = State()
    
from aiogram import F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext



@form_router.message(F.text == "ثبت نام")
async def start_form(message: Message, state: FSMContext):
    if not has_completed_videos(message.from_user.id):
        await message.answer(
            "❌ ابتدا باید ویدیوهای شروع را مشاهده کنید."
        )
        return

    await state.clear()
    await state.set_state(FormStates.waiting_for_full_name)

    await message.answer(
        "✍️ بیایید فرم معرفی اعضا را تکمیل کنیم.\n\n"
        "1️⃣ نام و نام خانوادگی خود را وارد کنید:"
    )


JOIN_TEXT = f"""لینک عضویت 



{GROUP_INVITE_LINK}



ورود رو به مجموعه تبریک میگم و خیلی خوش حالم که اینجایی 



برای عضویت بعد اینکه وارد گروه شدی روی لگو گروه ضربه بزن تا به همه روم ها دسترسی داشته باشی





روی دکمه اقدام برای کوچ بزن تا درخواستت ثبت بشه و بعد از بررسی ادمین، یک کوچ مجموعه برایت مشخص می‌شود. منتظر پیام کوچ باش."""





@form_router.message(F.chat.type == "private", F.text == "عضویت در گروه")

async def join_group(message: Message):

    if not has_form(message.from_user.id):

        await message.answer("❌ ابتدا باید ثبت نام را تکمیل کنید.")

        return



    await message.answer(JOIN_TEXT)





# 1. Full name
@form_router.message(FormStates.waiting_for_full_name, F.text)
async def get_full_name(message: Message, state: FSMContext):
    full_name = message.text.strip()

    if len(full_name) < 3:
        await message.answer("❌ لطفاً نام و نام خانوادگی معتبر وارد کنید.")
        return

    await state.update_data(full_name=full_name)
    await state.set_state(FormStates.waiting_for_city)
    await message.answer("2️⃣ در کدام شهر زندگی می‌کنید？")

# 2. City
@form_router.message(FormStates.waiting_for_city, F.text)
async def get_city(message: Message, state: FSMContext):
    city = message.text.strip()

    if len(city) < 2:
        await message.answer("❌ لطفاً نام شهر را معتبر وارد کنید.")
        return

    await state.update_data(city=city)

    await state.set_state(FormStates.waiting_for_skills)

    await message.answer("3️⃣ تخصص‌ها و مهارت‌های شما چیست؟")


# 3. Skills
@form_router.message(FormStates.waiting_for_skills, F.text)
async def get_skills(message: Message, state: FSMContext):
    skills = message.text.strip()

    if len(skills) < 2:
        await message.answer("❌ لطفاً حداقل یک مهارت وارد کنید.")
        return

    await state.update_data(skills=skills)

    await state.set_state(FormStates.waiting_for_active_fields)

    await message.answer(
        "4️⃣ در چه زمینه‌هایی فعال‌تر هستید؟"
    )


# 4. Active fields
@form_router.message(FormStates.waiting_for_active_fields, F.text)
async def get_active_fields(message: Message, state: FSMContext):
    active_fields = message.text.strip()

    if len(active_fields) < 2:
        await message.answer("❌ لطفاً زمینه فعالیت خود را وارد کنید.")
        return

    await state.update_data(active_fields=active_fields)

    await state.set_state(FormStates.waiting_for_contribution)

    await message.answer(
        "5️⃣ چه کمکی می‌توانید به شبکه ارائه دهید؟"
    )


# 5. Contribution
@form_router.message(FormStates.waiting_for_contribution, F.text)
async def get_contribution(message: Message, state: FSMContext):
    contribution = message.text.strip()

    if len(contribution) < 2:
        await message.answer("❌ لطفاً پاسخ خود را وارد کنید.")
        return

    await state.update_data(contribution=contribution)

    await state.set_state(FormStates.waiting_for_needed_help)

    await message.answer(
        "6️⃣ چه کسانی یا در چه زمینه‌هایی می‌توانند به شما کمک کنند؟"
    )


# 6. Needed help
@form_router.message(FormStates.waiting_for_needed_help, F.text)
async def get_needed_help(message: Message, state: FSMContext):
    needed_help = message.text.strip()

    if len(needed_help) < 2:
        await message.answer("❌ لطفاً پاسخ خود را وارد کنید.")
        return

    await state.update_data(needed_help=needed_help)

    await state.set_state(FormStates.waiting_for_contact)

    await message.answer(
        "7️⃣ راه ارتباطی شما چیست؟\n\n"
        "یکی از این موارد را وارد کنید:\n"
        "📞 شماره تماس 11 رقمی، مثل 09121234567\n"
        "📧 ایمیل، مثل name@example.com\n"
        "✈️ آیدی تلگرام با @، مثل @ali_rezaei"
    )


PERSIAN_DIGITS = {ord(chr(0x06F0 + i)): str(i) for i in range(10)} | {ord(chr(0x0660 + i)): str(i) for i in range(10)}
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+\-]+@(?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,}")
TELEGRAM_LINK_RE = re.compile(r"(?:https?://)?(?:www\.)?(?:t|telegram)\.me/@?([A-Za-z0-9_]+)/?", re.IGNORECASE)
TELEGRAM_USERNAME_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{3,30}[A-Za-z0-9]")
PHONE_INTL_RE = re.compile(r"(?:\+98|0098|98)(\d{10})")
PHONE_RE = re.compile(r"0\d{10}")
DIGITS_ONLY_RE = re.compile(r"\+?\d+")

PHONE_ERROR = "❌ شماره تماس باید دقیقاً 11 رقم باشد.\nنمونه: 09121234567"
EMAIL_ERROR = "❌ ایمیل واردشده معتبر نیست.\nنمونه: name@example.com"
TELEGRAM_ERROR = (
    "❌ آیدی تلگرام معتبر نیست.\n"
    "آیدی باید با @ شروع شود، با حرف انگلیسی شروع شود و بین 5 تا 32 کاراکتر "
    "(حروف انگلیسی، عدد یا _) باشد.\n"
    "نمونه: @ali_rezaei"
)
CONTACT_ERROR = (
    "❌ راه ارتباطی معتبر نیست. یکی از این موارد را وارد کنید:\n\n"
    "📞 شماره تماس 11 رقمی، مثل 09121234567\n"
    "📧 ایمیل، مثل name@example.com\n"
    "✈️ آیدی تلگرام با @، مثل @ali_rezaei"
)


def validate_contact(text):
    value = text.strip()

    link = TELEGRAM_LINK_RE.fullmatch(value)
    if link:
        value = "@" + link.group(1)

    if value.startswith("@"):
        if TELEGRAM_USERNAME_RE.fullmatch(value[1:]):
            return value, None
        return None, TELEGRAM_ERROR

    if "@" in value:
        if len(value) <= 254 and EMAIL_RE.fullmatch(value):
            return value, None
        return None, EMAIL_ERROR

    digits = re.sub(r"[\s\-().]", "", value.translate(PERSIAN_DIGITS))

    if not DIGITS_ONLY_RE.fullmatch(digits):
        return None, CONTACT_ERROR

    international = PHONE_INTL_RE.fullmatch(digits)
    phone = "0" + international.group(1) if international else digits

    if PHONE_RE.fullmatch(phone):
        return phone, None

    return None, PHONE_ERROR


# 7. Contact
@form_router.message(FormStates.waiting_for_contact, F.text)
async def get_contact(message: Message, state: FSMContext):
    contact, error = validate_contact(message.text)

    if error:
        await message.answer(error)
        return

    await state.update_data(contact=contact)

    await state.set_state(FormStates.waiting_for_extra_info)

    await message.answer(
        "8️⃣ آیا توضیحات یا اطلاعات بیشتری برای معرفی خود دارید؟\n\n"
        "اگر ندارید، عبارت «ندارم» را ارسال کنید."
    )


# 8. Extra information
@form_router.message(FormStates.waiting_for_extra_info, F.text)
async def get_extra_info(message: Message, state: FSMContext):
    extra_info = message.text.strip()

    if not extra_info:
        await message.answer("❌ لطفاً پاسخ خود را وارد کنید.")
        return

    if extra_info.lower() in {"ندارم", "ندارم.", "خیر", "no", "none"}:
        extra_info = ""

    await state.update_data(extra_info=extra_info)

    form_data = await state.get_data()

    save_form_info(message.from_user.id, form_data)

    await state.clear()

    result = f"""
✅ فرم معرفی شما با موفقیت تکمیل شد.

👤 نام و نام خانوادگی:
{form_data["full_name"]}

📍 شهر:
{form_data["city"]}

💻 تخصص/مهارت:
{form_data["skills"]}

🎯 زمینه‌های فعالیت:
{form_data["active_fields"]}

🤝 کمک به شبکه:
{form_data["contribution"]}

🔍 کمک موردنیاز:
{form_data["needed_help"]}

📞 راه ارتباط:
{form_data["contact"]}

📝 موارد بیشتر:
{extra_info or "ذکر نشده"}
"""

    await message.answer(result)
    await message.answer(
        "✅ ثبت نام شما با موفقیت انجام شد.\n\n"
        "حالا روی «عضویت در گروه» بزن تا لینک ورود برایت ارسال شود."
    )
    await publish_member(message.from_user.id)
    await try_send_welcome_voice(message.from_user.id)

# Handle non-text messages while filling the form
@form_router.message(
    StateFilter(
        FormStates.waiting_for_full_name,
        FormStates.waiting_for_city,
        FormStates.waiting_for_skills,
        FormStates.waiting_for_active_fields,
        FormStates.waiting_for_contribution,
        FormStates.waiting_for_needed_help,
        FormStates.waiting_for_contact,
        FormStates.waiting_for_extra_info
    )
)
async def handle_non_text(message: Message):
    await message.answer(
        "❌ لطفاً پاسخ این سؤال را به‌صورت متن ارسال کنید."
    )