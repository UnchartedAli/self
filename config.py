import os
from dotenv import load_dotenv

load_dotenv()

# اجباری
API_ID = int(os.getenv("API_ID", "0"))
API_HASH = os.getenv("API_HASH", "")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

# اختیاری
SESSION_NAME = os.getenv("SESSION_NAME", "reze_session")
DB_NAME = os.getenv("DB_NAME", "reze.db")
NOTIFY_DELETIONS = os.getenv("NOTIFY_DELETIONS", "true").lower() == "true"
SAVE_MEDIA_MESSAGES = os.getenv("SAVE_MEDIA_MESSAGES", "true").lower() == "true"
MAX_SEARCH_RESULTS = int(os.getenv("MAX_SEARCH_RESULTS", "15"))
MAX_MESSAGE_DISPLAY_LENGTH = int(os.getenv("MAX_MESSAGE_DISPLAY_LENGTH", "120"))

# پیشوند دستورات
CMD_PREFIX = "."