import os

from dotenv import load_dotenv
from aiogram import Dispatcher, Router, Bot

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "")

# Group links. Defaults are placeholders; set the real ones in .env
DEFAULT_GROUP_INVITE_LINK = "https://t.me/your_group"
DEFAULT_INTRO_TOPIC_LINK = "https://t.me/your_group/2"
DEFAULT_NETWORKING_TOPIC_LINK = "https://t.me/your_group/3"

GROUP_INVITE_LINK = os.getenv("GROUP_INVITE_LINK") or DEFAULT_GROUP_INVITE_LINK
INTRO_TOPIC_LINK = os.getenv("INTRO_TOPIC_LINK") or DEFAULT_INTRO_TOPIC_LINK
NETWORKING_TOPIC_LINK = os.getenv("NETWORKING_TOPIC_LINK") or DEFAULT_NETWORKING_TOPIC_LINK

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is not set. Create a .env file (see .env.example).")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

vid_router = Router(name= "vid_router")
form_router = Router(name= "form_router")
manager_router = Router(name= "manager_router")
helper_router = Router(name= "helper_router")

dp.include_router(vid_router)
dp.include_router(form_router)
dp.include_router(manager_router)
dp.include_router(helper_router)

desc = """
   
   1. start(no spam) 
   2. accounting automatic
   3. helper
   4. welcome message
   5. uploading video
   6. powernetwork apply 
   7. sending form in group (moarefi aza/ shabake sazi)
   8. voice after sending form
   9. group entrance 
   10. coaches / random state handles 
"""