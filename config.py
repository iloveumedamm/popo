import os

from dotenv import load_dotenv

load_dotenv()

API_ID = os.environ.get('API_ID', '21748181')
API_HASH = os.environ.get('API_HASH', 'b1d962414e186e0778911f3183feac33')
BOT_TOKEN = os.environ.get('BOT_TOKEN', '6956498960:AAFekL2rqkfLP_herOZdD3zHrs9wa7T2uH8')
OWNER_ID = int(os.environ.get("OWNER_ID", ""))
ADMINS = (
    [int(i) for i in os.environ.get("ADMINS", "").split(" ")]
    if os.environ.get("ADMINS")
    else []
)
if OWNER_ID not in ADMINS:
    ADMINS.append(OWNER_ID)
MONGODB = os.environ.get('MONGODB', 'mongodb+srv://gafobey331:z8xpUDvwBJrVx6pX@cluster0.iqtnjjb.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
DATABASE_NAME = os.environ.get('DATABASE_NAME', '2')
COLLECTION_NAME = os.environ.get('COLLECTION_NAME', "laura-saving")
CHANNELS = os.environ.get('CHANNELS', "True")
CHANNELS_LIST = (
    [int(i) for i in os.environ.get("CHANNELS_LIST", "-1002133196746").split(" ")]
    if os.environ.get("CHANNELS_LIST")
    else []
)
FORCESUB = os.environ.get('FORCESUB', "True")
FILMS_LINK = os.environ.get('FILMS_LINK', 'https://t.me/HA_Films_World')
# Other Settings
UPDATE_CHANNEL =  int(os.environ.get('UPDATE_CHANNEL', '-1002133196746'))
USERNAME = os.environ.get('USERNAME', 'unratedmovbot')
HOWTO = os.environ.get('HOWTO', 'MdiskShortner_Link')
RESULTS_COUNT = int(os.environ.get('RESULT_COUNTS', 10))
AUTO_DELETE = os.environ.get('AUTO_DELETE', True)
AUTO_DELETE_TIME = int(os.environ.get('AUTO_DELETE_TIME', 300))
IMDB_TEMPLATE = os.environ.get("IMDB_TEMPLATE", "<b>Query: {query}</b> \n‌‌‌‌IMDb Data:\n\n🏷 Title: <a href={url}>{title}</a>\n🎭 Genres: {genres}\n📆 Year: <a href={url}/releaseinfo>{year}</a>\n🌟 Rating: <a href={url}/ratings>{rating}</a> / 10")
MAX_LIST_ELM = os.environ.get("MAX_LIST_ELM", 5)
WELCOME_IMAGE = os.environ.get('WELCOME_IMAGE', 'https://bit.ly/3y8miWu')
RESULTS_IMAGE = os.environ.get('RESULTS_IMAGE', 'https://static.wikia.nocookie.net/ideas/images/e/e4/Movie_night.jpg')
MDISK_API=os.environ.get('MDISK_API', "khxbvkjxnk")
SHORTENER_API=os.environ.get('SHORTENER_API', "62adbdafb4a9ddd880c26b4d41e07b8d9cde02a8")
SHORTENER_WEBSITE=os.environ.get('SHORTENER_WEBSITE', "jnglink.in")
OMDB_API=os.environ.get('OMDB_API', "cc037692")
CUSTOM_CAPTION=os.environ.get('CUSTOM_CAPTION', '{caption}\n @anonymous1904')
LOG_CHANNEL = int(os.environ.get('LOG_CHANNEL', '-1002133196746'))
BROADCAST_AS_COPY = os.environ.get('BROADCAST_AS_COPY', False)
#  Replit Config
REPLIT_USERNAME = os.environ.get("REPLIT_USERNAME", None)
REPLIT_APP_NAME = os.environ.get("REPLIT_APP_NAME", None)
REPLIT = f"https://{REPLIT_APP_NAME.lower()}.{REPLIT_USERNAME}.repl.co" if REPLIT_APP_NAME and REPLIT_USERNAME else False
PING_INTERVAL = int(os.environ.get("PING_INTERVAL", "300"))
USE_OMDB = os.environ.get("USE_OMDB", "True")
PAID = os.environ.get("PAID", "False") == "True"

VALIDITY = (
    [int(i) for i in os.environ.get("VALIDITY").split(" ")]
    if os.environ.get("VALIDITY")
    else []
)

SUBSCRIPTION_REMINDER_MESSAGE = """**Your subscription is gonna end soon. 
    
Renew your subscription to continue this service contact {owner}
Details:
Group ID: `{group_id}` {group_link}
Subscription Date: {subscription_date}
Expiry Date: {expiry_date}
Subscription Peroid Remaining: {time_remaining}
Banned: {banned_status}
**"""

help_message = """Hi there! Welcome to Movie Search Bot 🤖

This bot helps you search for movies 🎬 and share them with your friends! 🤝 

Here's a list of commands you can use: 

• /start – Get started with the bot
• /help – Get help with using the bot 

Group Admin Commands:

• /set_api – Set your own API key 
• /api – Check your API key settings 
• /fsub – Check your force sub settings
• /set_fsub – Set a force sub channel 
• /set_shortener Your Mdisk Shortener API  

To use the bot in a group, make sure you make it an admin. 🤖

Happy searching! 🔍"""
HELP_MESSAGE = os.environ.get("HELP_MESSAGE", help_message)


help_message_admin = """
Bot Admin Commands:

/premium_groups: This command will allow admins to view all of the premium groups they manage. 🔍

/myplan group_id: This command will allow admins to view the subscription plan associated with a specific group. 🔍

/total_groups: This command will allow admins to view the total number of groups they manage. 📊

/premium_reminder: This command will remind admins to renew their subscription plans for all of their groups. ⏰"""
HELP_MESSAGE_ADMIN =os.environ.get("HELP_MESSAGE_ADMIN", help_message_admin)

ABOUT_MESSAGE = os.environ.get("ABOUT_MESSAGE", "About Message")

DEFAULT_PHOTO = os.environ.get("DEFAULT_PHOTO", "https://bit.ly/3y8miWu")

IS_SHORTENER_ENABLED=os.environ.get('IS_SHORTENER_ENABLED', "False")
IS_VERIFY=os.environ.get('IS_VERIFY', "True")
BASE_SITE = SHORTENER_WEBSITE
SHORTLINK_URL = os.environ.get("SHORTLINK_URL", "mdiskshortner.link")
SHORTLINK_API = os.environ.get("SHORTLINK_API", "36f1ae74ba1aa01e5bd73bdd0bc22aa915443501")
VERIFY_EXPIRE = int(os.environ.get('VERIFY_EXPIRE', 86400)) # Add time in seconds

VERIFY_TUTORIAL = os.environ.get("VERIFY_TUTORIAL", "https://t.me/HA_Bots")