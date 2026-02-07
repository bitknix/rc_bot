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

# Difficulty level
DIFFICULTY_LEVEL = "GMAT 700+ / CAT advanced"

# Scheduling
DAILY_SEND_TIME = "08:00"  # 8 AM in the user's timezone (HH:MM format in UTC)
TIMEZONE = "UTC"

# Logging
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
