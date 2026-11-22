# 🌐 PowerNetwork Bot

**English** · [فارسی](README.fa.md)

A Telegram bot designed for onboarding and managing members of a networking community: educational onboarding videos, an introduction form, automated member showcase publishing to group topics, and a coaching system. This is a personal project, built to show off Telegram bot development skills.

🤖 **Try the bot:** [@your_bot_username](https://t.me/your_bot_username) <!-- TODO: demo bot link -->

## ✨ Features

### For users
- Welcome message and automatic account registration upon `/start`
- Two sequential onboarding videos: each video unlocks a "✅ I watched the video" button, and after the second video, the "Register" button becomes available
- 8-step member profile submission form (Name, City, Skills, Fields of activity, Value offered to the network, Assistance needed, Contact method, Notes) with input validation for 11-digit phone numbers, emails, or Telegram handles
- Automated submission summary and welcome voice note sent after completing registration
- Automatic broadcast of member profiles to the group's "Member Introductions" topic, plus name and contact method to the "Networking" topic
- "Join Group" button providing the group invite link, and "Apply for Coaching" button to request coaching
- Built-in help guide with `/help`

### For admins
- User statistics and registered user directory
- Broadcast announcements to all users (text, photo, and video)
- Coach roster management (add and remove coaches)
- Automated dispatch of applicant information directly to the assigned coach

## 🛠 Tech stack

Python • aiogram 3 • SQLite • FSM • asyncio • python-dotenv

## 📁 Project structure

| File | Responsibility |
|---|---|
| `main.py` | Bot entry point, `/start` handler, and coaching requests |
| `config.py` | Configuration loaded from `.env`, bot setup, and router registration |
| `database.py` | Creates SQLite tables and registers the admin account |
| `base.py` | Database helper functions and reply/inline keyboards |
| `video.py` | Educational onboarding video delivery and watch tracking |
| `form.py` | Registration form flow and group invite handling |
| `group_topic.py` | Automated publishing of member profiles to group topics |
| `voice.py` | Welcome voice note delivery |
| `manager.py` | Admin panel and coach management system |
| `helper.py` | Help guide and user instructions |
| `get_file_id.py` | Utility helper script to obtain Telegram `file_id` for videos |

## 🔗 Group link configuration

Group links are configured in `.env` and default to placeholder values (`https://t.me/your_group`):

| Variable | Usage |
|---|---|
| `GROUP_INVITE_LINK` | Group invite link sent when a user clicks "Join Group" |
| `INTRO_TOPIC_LINK` | Link to the "Member Introductions" group topic |
| `NETWORKING_TOPIC_LINK` | Link to the "Networking" group topic |

Until you update these links, the bot runs without errors but will skip posting member introductions to the group (emitting a warning in the logs). Each topic can be configured independently. To get a topic link, right-click any message inside that topic and select "Copy Message Link". The bot must be an administrator in the group with permission to post in topics.

## 🚀 Running the bot

The project is developed with Python 3.11.

```bash
git clone https://github.com/JangjooProgrammer/powernetwork-bot.git
cd powernetwork-bot

python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

Copy `.env.example`, rename it to `.env`, and fill in your bot token, admin ID, and group links:

```env
BOT_TOKEN=your_bot_token_here
ADMIN_ID=123456789
ADMIN_USERNAME=admin_username

GROUP_INVITE_LINK=https://t.me/your_group
INTRO_TOPIC_LINK=https://t.me/your_group/2
NETWORKING_TOPIC_LINK=https://t.me/your_group/3
```

### Video setup
Telegram `file_id`s are unique per bot token. To set up onboarding videos:
1. Stop the main bot and run `python get_file_id.py`.
2. Send both videos to your bot; the bot will reply with each video's `file_id`.
3. Rename `video_file_ids.example.json` to `video_file_ids.json` and paste your IDs.
4. Stop `get_file_id.py`.

### Welcome voice note (optional)
Place an audio file named `welcome.ogg` in the `voice/` directory (or specify its custom path in `VOICE_PATH`). The bot will upload it on first use and cache the `file_id`. If the file is omitted, this step is automatically skipped.

```bash
python main.py
```

Database tables and the admin account are created automatically on the first run.

## 🔒 Security notes

- `.env`, the database file (`case.db`), log files, and cached `file_id` JSON files are never committed to git.
- The bot token, admin ID, and group links are strictly loaded from `.env`.