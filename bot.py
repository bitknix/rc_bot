"""
Telegram bot implementation for RC practice.
"""
import json
import os
from datetime import datetime
from typing import Optional, Dict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
    MessageHandler
)
from rc_generator import RCGenerator
from config import TELEGRAM_TOKEN, DEBUG_MODE

# Global RC state
current_rc = None
rc_generator = RCGenerator()


class RCBot:
    """Telegram bot for daily RC practice."""

    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.generator = RCGenerator()
        self.current_rc = None
        self.today_date = None
        self.data_dir = "data"
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        welcome_text = """
✨ *GMAT/CAT 700+ Reading Comprehension Bot* ✨

Welcome to your daily RC challenge! This bot provides high-difficulty reading comprehension practice comparable to GMAT 700+ levels.

📋 *What You Get:*
• One challenging passage daily (420-520 words)
• 4 inference-heavy questions
• Detailed explanations for all answers
• Rotating topics: Philosophy, Economics, Politics, Cognitive Science, Sociology, History of Ideas

🎯 *Commands:*
/today - Get today's RC passage and questions
/answer - View answers and detailed explanations
/help - Show this message again
/stats - Your practice statistics

🔥 *Difficulty Level:* GMAT 700+ / CAT Advanced
• Abstract, dense prose
• Implicit author stance
• Requires logical inference
• Tricky options (2+ may seem correct)

Start with /today to begin!
        """
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = """
📚 *RC Bot Commands:*

/today - Get today's RC passage and all 4 questions
/answer - View answers with detailed explanations
/hint - Get a hint for the last question (coming soon)
/stats - View your practice progress
/feedback - Send feedback about the RC
/help - This message

💡 *Pro Tips:*
1. Read the passage twice before answering
2. Eliminate obviously wrong options first
3. Pay attention to author's tone and stance
4. Look for logical flow between paragraphs
5. Don't choose answers based on external knowledge—use only passage info

Happy practicing! 🎯
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /today command - send today's RC."""
        try:
            # Check if already sent today
            today = datetime.now().date().isoformat()
            rc_file = f"{self.data_dir}/today_rc.json"

            if os.path.exists(rc_file):
                with open(rc_file, "r") as f:
                    data = json.load(f)
                    if data.get("date", "").startswith(today):
                        self.current_rc = data
                        await self._send_rc(update)
                        return

            # Generate new RC for today
            self.current_rc = self.generator.generate_daily_rc()

            # Validate
            is_valid, message = self.generator.validate_rc(self.current_rc)
            if not is_valid:
                await update.message.reply_text(
                    f"⚠️ RC generation failed: {message}\nPlease try again."
                )
                return

            # Save for today
            self.current_rc["date"] = datetime.now().isoformat()
            with open(rc_file, "w") as f:
                json.dump(self.current_rc, f, indent=2)

            await self._send_rc(update)

        except Exception as e:
            error_msg = f"❌ Error generating RC: {str(e)}"
            if DEBUG_MODE:
                print(error_msg)
            await update.message.reply_text(error_msg)

    async def _send_rc(self, update: Update) -> None:
        """Format and send the RC passage and questions."""
        if not self.current_rc:
            await update.message.reply_text("No RC loaded. Use /today first.")
            return

        passage = self.current_rc["passage"]
        topic = self.current_rc["topic"]
        questions = self.current_rc["questions"]

        # Format passage message
        passage_msg = f"""
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
        """
        await update.message.reply_text(passage_msg, parse_mode="Markdown")

        # Send each question
        for i, q in enumerate(questions, 1):
            question_msg = f"""
*Q{i}. {q['type'].upper()}*

{q['question']}

{chr(10).join(q['options'])}

💭 *Take your time. Use /answer to see correct answer.*
            """
            await update.message.reply_text(question_msg, parse_mode="Markdown")

    async def show_answers(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /answer command - show answers and explanations."""
        if not self.current_rc:
            await update.message.reply_text("No RC loaded. Use /today first to generate today's RC.")
            return

        questions = self.current_rc["questions"]
        topic = self.current_rc["topic"]

        # Header
        header = f"""
✅ *ANSWERS & EXPLANATIONS*

📌 *Topic:* {topic}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """
        await update.message.reply_text(header, parse_mode="Markdown")

        # Each question's answer
        for q in questions:
            answer_msg = f"""
*Q{q['number']}. {q['type'].upper()}*

{q['question']}

*Correct Answer:* {q['correct_answer']}

*Why this is correct:*
{q['explanation']['correct']}

*Why other options fail:*
{q['correct_answer']} is not: {q['explanation']['A'] if q['correct_answer'] != 'A' else q['explanation']['B']}
{q['correct_answer']} is not: {q['explanation']['B'] if q['correct_answer'] != 'B' else q['explanation']['C']}
{q['correct_answer']} is not: {q['explanation']['C'] if q['correct_answer'] != 'C' else q['explanation']['D']}
{q['correct_answer']} is not: {q['explanation']['D'] if q['correct_answer'] != 'D' else q['explanation']['A']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            await update.message.reply_text(answer_msg, parse_mode="Markdown")

        # Summary message
        summary = """
*🎓 How to Review:*
1. Compare your answers with the correct ones
2. Read the explanations for questions you missed
3. Understand WHY the answer is correct, not just WHAT it is
4. Notice patterns in your mistakes

Come back tomorrow for a new challenge! 🚀
        """
        await update.message.reply_text(summary, parse_mode="Markdown")

    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /stats command."""
        stats_msg = """
📊 *Your Practice Stats* (Coming Soon)

Currently tracking:
🔹 Total RCs attempted
🔹 Average accuracy
🔹 Topics completed
🔹 Most challenging question type
🔹 Improvement over time

We'll have detailed analytics in the next update! 📈
        """
        await update.message.reply_text(stats_msg, parse_mode="Markdown")

    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /feedback command."""
        feedback_msg = """
💬 *Send Feedback*

You can provide feedback about:
✅ Passage difficulty
✅ Question quality
✅ Explanation clarity
✅ Bot functionality
✅ Topic suggestions

Reply directly after this message with your feedback!

Your input helps us improve the bot. Thank you! 🙏
        """
        await update.message.reply_text(feedback_msg, parse_mode="Markdown")

    async def handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle feedback messages."""
        feedback_text = update.message.text
        timestamp = datetime.now().isoformat()
        user_id = update.message.from_user.id
        user_name = update.message.from_user.full_name

        # Save feedback
        feedback_log = f"{self.data_dir}/feedback.jsonl"
        with open(feedback_log, "a") as f:
            f.write(json.dumps({
                "timestamp": timestamp,
                "user_id": user_id,
                "user_name": user_name,
                "feedback": feedback_text
            }) + "\n")

        await update.message.reply_text(
            "✅ Thank you for your feedback! We'll review it to improve the bot."
        )

    def get_application(self) -> Application:
        """Create and configure the Telegram bot application."""
        app = Application.builder().token(self.token).build()

        # Command handlers
        app.add_handler(CommandHandler("start", self.start))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("today", self.today))
        app.add_handler(CommandHandler("answer", self.show_answers))
        app.add_handler(CommandHandler("stats", self.stats_command))
        app.add_handler(CommandHandler("feedback", self.feedback_command))

        # Fallback handler for other messages
        app.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_feedback)
        )

        return app


def main():
    """Start the bot."""
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "your_bot_token_here":
        print("❌ Error: TELEGRAM_TOKEN not set in .env file")
        print("Get a bot token from @BotFather on Telegram")
        return

    bot = RCBot()
    app = bot.get_application()

    print("🤖 RC Bot starting...")
    print("Press Ctrl+C to stop")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
