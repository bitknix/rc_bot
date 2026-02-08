"""
Configuration and constants for RC Bot.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "your_bot_token_here")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", None)  # Optional: for admin notifications

# Hugging Face (FREE tier)
HF_API_TOKEN = os.getenv("HF_API_TOKEN") or os.getenv("HF_TOKEN")  # Support both env var names
# Recommended free models with good instruction-following:
HF_MODEL = os.getenv("HF_MODEL", "mistralai/Mistral-7B-Instruct-v0.2")
# Alternatives (if above doesn't work):
# - "NousResearch/Nous-Hermes-2-Mistral-7B-DPO"
# - "meta-llama/Llama-2-7b-chat-hf" (requires access request)
# - "HuggingFaceH4/zephyr-7b-beta"

# RC Generation Parameters
RC_PASSGE_WORD_COUNT = (420, 520)  # Min, Max
RC_NUM_QUESTIONS = 4
RC_OPTIONS_PER_QUESTION = 4

# Topics rotation
RC_TOPICS = [
    "Philosophy",
    "Political theory",
    "Behavioral economics",
    "Sociology",
    "Cognitive science",
    "History of ideas",
    "Philosophy of science",
    "Epistemology",
    "Ethics and morality",
    "Economics and markets",
    "Cultural anthropology",
    "Intellectual history"
]

# Difficulty levels
DIFFICULTY_LEVELS = {
    "gmat": {
        "name": "GMAT 700+",
        "word_range": (420, 520),
        "description": "Ultra-dense abstract prose with complex nested sentences"
    },
    "cat": {
        "name": "CAT Advanced",
        "word_range": (380, 480),
        "description": "Dense academic content with implicit author stance"
    },
    "sbi": {
        "name": "SBI/IBPS PO",
        "word_range": (250, 350),
        "description": "Moderate difficulty with clear structure and business/HR topics"
    }
}

# Default difficulty
DEFAULT_DIFFICULTY = "gmat"

# Scheduling
DAILY_SEND_TIME = "08:00"  # 8 AM in the user's timezone (HH:MM format in UTC)
TIMEZONE = "UTC"

# Admin access
admin_ids_str = os.getenv("ADMIN_USER_IDS", "").strip()
if admin_ids_str:
    try:
        ADMIN_USER_IDS = [int(uid.strip()) for uid in admin_ids_str.split(",") if uid.strip()]
    except ValueError:
        ADMIN_USER_IDS = []
        print("[WARN] Invalid ADMIN_USER_IDS format. Expected: comma-separated numbers")
else:
    ADMIN_USER_IDS = []

print(f"[INFO] Admin users loaded: {ADMIN_USER_IDS}")

# Logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
