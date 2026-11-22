import html
import logging
from urllib.parse import urlparse, parse_qs

from config import (
    bot,
    INTRO_TOPIC_LINK,
    NETWORKING_TOPIC_LINK,
    DEFAULT_INTRO_TOPIC_LINK,
    DEFAULT_NETWORKING_TOPIC_LINK,
)
from base import get_member_publish_data


def parse_topic_link(link):
    link = (link or "").strip()

    if not link:
        raise ValueError("Topic link is empty")

    if "://" not in link:
        link = "https://" + link

    parsed = urlparse(link)
    parts = [p for p in parsed.path.split("/") if p]
    query = parse_qs(parsed.query)

    try:
        if parts[0] == "c":
            chat_id = int(f"-100{parts[1]}")
            numbers = parts[2:]
        else:
            chat_id = f"@{parts[0]}"
            numbers = parts[1:]

        if "thread" in query:
            thread_id = int(query["thread"][0])
        else:
            thread_id = int(numbers[0])
    except (IndexError, ValueError):
        raise ValueError(f"Invalid topic link: {link}")

    return chat_id, thread_id


def split_lines(lines, limit=4000):
    chunks = []
    current = ""

    for line in lines:
        if current and len(current) + len(line) + 1 > limit:
            chunks.append(current)
            current = line
        else:
            current = f"{current}\n{line}" if current else line

    if current:
        chunks.append(current)

    return chunks


async def post_introduction(target, fields):
    chat_id, thread_id = target
    lines = ["📋 <b>معرفی عضو جدید</b>", ""]

    for label, value in fields:
        lines.append(f"<b>{html.escape(str(label))}:</b> {html.escape(str(value))}")

    for chunk in split_lines(lines):
        await bot.send_message(
            chat_id=chat_id,
            message_thread_id=thread_id,
            text=chunk,
            parse_mode="HTML"
        )


async def post_networking(target, name, contact):
    chat_id, thread_id = target
    text = (
        f"🤝 <b>{html.escape(str(name))}</b>\n"
        f"📞 راه ارتباطی: {html.escape(str(contact))}"
    )
    await bot.send_message(
        chat_id=chat_id,
        message_thread_id=thread_id,
        text=text,
        parse_mode="HTML"
    )


def configured_target(link, default_link, name):
    """Parse a topic link from .env. Returns None while it still has the placeholder value."""
    if link == default_link:
        logging.warning("%s is not configured in .env, skipping this post.", name)
        return None

    try:
        return parse_topic_link(link)
    except ValueError:
        logging.exception("%s in .env is not a valid topic link", name)
        return None


async def publish_member(user_id):
    intro_target = configured_target(INTRO_TOPIC_LINK, DEFAULT_INTRO_TOPIC_LINK, "INTRO_TOPIC_LINK")
    networking_target = configured_target(
        NETWORKING_TOPIC_LINK, DEFAULT_NETWORKING_TOPIC_LINK, "NETWORKING_TOPIC_LINK"
    )

    if not intro_target and not networking_target:
        return

    try:
        data = get_member_publish_data(user_id)
    except Exception:
        logging.exception("Member Data Error")
        return

    if not data:
        logging.error("No registration data found for user %s", user_id)
        return

    name = data["name"] or "بدون نام"
    contact = data["contact"] or "ثبت نشده"

    if intro_target:
        try:
            await post_introduction(intro_target, data["fields"])
        except Exception:
            logging.exception("Introduction Topic Error")

    if networking_target:
        try:
            await post_networking(networking_target, name, contact)
        except Exception:
            logging.exception("Networking Topic Error")
