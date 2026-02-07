"""
Scheduler for daily RC sending via Telegram.
"""
import asyncio
import json
from datetime import datetime, time
from zoneinfo import ZoneInfo
from telegram import Bot
from telegram.error import TelegramError
from rc_generator import RCGenerator
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, DAILY_SEND_TIME, TIMEZONE


class RCScheduler:
    """Handles scheduled daily RC sending."""

    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.chat_id = TELEGRAM_CHAT_ID
        self.send_time = datetime.strptime(DAILY_SEND_TIME, "%H:%M").time()
        self.timezone = ZoneInfo(TIMEZONE)
        self.generator = RCGenerator()
        self.bot = Bot(token=self.token)
        self.data_dir = "data"

    async def start_scheduler(self):
        """Start the daily scheduler."""
        print(f"🕐 Scheduler started. Daily RC will send at {DAILY_SEND_TIME} {TIMEZONE}")

        while True:
            await self._check_and_send()
            # Check every minute
            await asyncio.sleep(60)

    async def _check_and_send(self):
        """Check if it's time to send and send if needed."""
        now = datetime.now(self.timezone).time()
        today = datetime.now(self.timezone).date().isoformat()

        # Check if it's the send time (within 1 minute)
        if abs(now.hour * 60 + now.minute - (self.send_time.hour * 60 + self.send_time.minute)) <= 1:
            # Check if already sent today
            send_log_file = f"{self.data_dir}/send_log.json"
            already_sent = False

            if os.path.exists(send_log_file):
                with open(send_log_file, "r") as f:
                    try:
                        send_log = json.load(f)
                        if send_log.get("last_send_date") == today:
                            already_sent = True
                    except:
                        pass

            if not already_sent:
                await self._send_daily_rc()

    async def _send_daily_rc(self):
        """Generate and send today's RC."""
        if not self.chat_id:
            print("⚠️ TELEGRAM_CHAT_ID not set. Skipping scheduled send.")
            return

        try:
            print(f"📤 Sending daily RC to chat {self.chat_id}...")

            # Generate RC
            rc = self.generator.generate_daily_rc()
            is_valid, message = self.generator.validate_rc(rc)

            if not is_valid:
                print(f"❌ RC validation failed: {message}")
                return

            # Send passage
            passage = rc["passage"]
            topic = rc["topic"]
            passage_text = f"""
🎯 *Today's RC Challenge*

📌 *Topic:* {topic}
🔥 *Level:* GMAT 700+ / CAT Advanced

━━━━━━━━━━━━━━━━━━━━━
*PASSAGE* ({len(passage.split())} words)
━━━━━━━━━━━━━━━━━━━━━

{passage}

━━━━━━━━━━━━━━━━━━━━━
*QUESTIONS*
━━━━━━━━━━━━━━━━━━━━━

Try to answer before using /answer for solutions!
            """
            await self.bot.send_message(
                chat_id=self.chat_id,
                text=passage_text,
                parse_mode="Markdown"
            )

            # Send each question
            for q in rc["questions"]:
                question_text = f"""
*Q{q['number']}. {q['type'].upper()}*

{q['question']}

{chr(10).join(q['options'])}

💭 *Take your time!*
                """
                await self.bot.send_message(
                    chat_id=self.chat_id,
                    text=question_text,
                    parse_mode="Markdown"
                )

            # Save to log
            today = datetime.now().date().isoformat()
            send_log = {
                "last_send_date": today,
                "topic": topic,
                "timestamp": datetime.now().isoformat()
            }

            send_log_file = f"{self.data_dir}/send_log.json"
            with open(send_log_file, "w") as f:
                json.dump(send_log, f, indent=2)

            print(f"✅ RC sent successfully at {datetime.now().isoformat()}")

        except TelegramError as e:
            print(f"❌ Telegram error: {e}")
        except Exception as e:
            print(f"❌ Error sending RC: {e}")

    async def send_now(self):
        """Manually trigger RC send (for testing)."""
        await self._send_daily_rc()


async def main():
    """Run the scheduler."""
    scheduler = RCScheduler()
    await scheduler.start_scheduler()


if __name__ == "__main__":
    import os
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--send-now":
        # Manual send for testing
        print("📤 Sending RC now...")
        scheduler = RCScheduler()
        asyncio.run(scheduler.send_now())
    else:
        # Normal scheduler
        asyncio.run(main())
