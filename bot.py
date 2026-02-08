"""
Telegram bot implementation for RC practice.
"""
import json
import os
from datetime import datetime, timedelta
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
from config import TELEGRAM_TOKEN, DEBUG_MODE, ADMIN_USER_IDS, DIFFICULTY_LEVELS, DEFAULT_DIFFICULTY

# Global RC state
current_rc = None
rc_generator = RCGenerator()


class UserAnalytics:
    """Manages user analytics and statistics."""

    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.users_file = f"{data_dir}/users.json"
        self.analytics_file = f"{data_dir}/analytics.jsonl"
        self._ensure_data_dir()
        self._load_users()

    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _load_users(self):
        """Load users database."""
        if not os.path.exists(self.users_file):
            self.users = {}
        else:
            try:
                with open(self.users_file, "r") as f:
                    self.users = json.load(f)
            except:
                self.users = {}

    def _save_users(self):
        """Save users database."""
        with open(self.users_file, "w") as f:
            json.dump(self.users, f, indent=2)

    def track_user(self, user_id: int, user_name: str, difficulty: str = None):
        """Track user and log activity."""
        user_id_str = str(user_id)

        if user_id_str not in self.users:
            self.users[user_id_str] = {
                "user_id": user_id,
                "user_name": user_name,
                "first_seen": datetime.now().isoformat(),
                "last_seen": datetime.now().isoformat(),
                "total_rcs": 0,
                "difficulty_preferences": {},
                "streak": 0,
                "last_activity_date": None
            }

        user = self.users[user_id_str]
        user["last_seen"] = datetime.now().isoformat()
        user["total_rcs"] += 1

        # Track difficulty preference
        if difficulty:
            if difficulty not in user["difficulty_preferences"]:
                user["difficulty_preferences"][difficulty] = 0
            user["difficulty_preferences"][difficulty] += 1

        # Track streak
        today = datetime.now().date().isoformat()
        if user["last_activity_date"] != today:
            if user["last_activity_date"]:
                yesterday = (datetime.now().date() - timedelta(days=1)).isoformat()
                if user["last_activity_date"] == yesterday:
                    user["streak"] += 1
                else:
                    user["streak"] = 1
            else:
                user["streak"] = 1
            user["last_activity_date"] = today

        self._save_users()

        # Log analytics
        with open(self.analytics_file, "a") as f:
            f.write(json.dumps({
                "timestamp": datetime.now().isoformat(),
                "user_id": user_id,
                "user_name": user_name,
                "action": "view_rc",
                "difficulty": difficulty or DEFAULT_DIFFICULTY
            }) + "\n")

    def get_user_stats(self, user_id: int) -> Optional[Dict]:
        """Get user statistics."""
        user_id_str = str(user_id)
        return self.users.get(user_id_str)

    def get_all_users_count(self) -> int:
        """Get total count of users."""
        return len(self.users)

    def get_daily_active_users(self) -> int:
        """Get count of users active today."""
        today = datetime.now().date().isoformat()
        count = 0
        for user in self.users.values():
            if user.get("last_activity_date") == today:
                count += 1
        return count

    def get_total_interactions(self) -> int:
        """Get total number of RC interactions."""
        total = 0
        for user in self.users.values():
            total += user.get("total_rcs", 0)
        return total

    def get_top_users(self, limit=5) -> list:
        """Get top users by RC attempts."""
        sorted_users = sorted(
            self.users.values(),
            key=lambda x: x.get("total_rcs", 0),
            reverse=True
        )
        return sorted_users[:limit]

    def get_stats_summary(self) -> Dict:
        """Get overall analytics summary."""
        return {
            "total_users": self.get_all_users_count(),
            "daily_active": self.get_daily_active_users(),
            "total_interactions": self.get_total_interactions(),
            "top_users": self.get_top_users()
        }


class RCBot:
    """Telegram bot for daily RC practice."""

    def __init__(self):
        self.token = TELEGRAM_TOKEN
        self.generator = RCGenerator()
        self.analytics = UserAnalytics()
        self.current_rc = None
        self.today_date = None
        self.user_difficulty = {}
        self.data_dir = "data"
        self._ensure_data_dir()

    def _ensure_data_dir(self):
        """Ensure data directory exists."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _is_admin(self, user_id: int) -> bool:
        """Check if user is admin."""
        return user_id in ADMIN_USER_IDS

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command."""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.full_name

        # Track user
        self.analytics.track_user(user_id, user_name)

        welcome_text = """
✨ *GMAT/CAT/SBI-IBPS RC Practice Bot* ✨

Welcome to your elite reading comprehension training platform! Choose your difficulty level and practice daily.

📋 *What You Get:*
• Multiple difficulty levels: GMAT 700+, CAT Advanced, SBI/IBPS PO
• One challenging passage daily
• 4 inference-heavy questions
• Detailed explanations for all answers
• Rotating topics: Philosophy, Economics, Politics, and more

🎯 *Commands:*
/today - Get today's RC passage
/answer - View answers and explanations
/difficulty - Choose your difficulty level
/streak - View your practice streak
/mystats - Your personal statistics
/quiz - Practice multiple passages
/help - Show all commands
"""
        await update.message.reply_text(welcome_text, parse_mode="Markdown")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command."""
        help_text = """
📚 *RC Bot Commands:*

*Practice:*
/today - Get today's RC passage
/answer - View answers with detailed explanations
/difficulty - Select difficulty level
/quiz - Practice 3 passages in a row

*Statistics:*
/streak - View your practice streak
/mystats - Your personal statistics

*Others:*
/feedback - Send feedback
/help - This message

💡 *Difficulty Levels:*
🔥 *GMAT 700+* - Ultra-dense abstract prose, implicit author stance
🟡 *CAT Advanced* - Dense academic content, moderate complexity
🟢 *SBI/IBPS PO* - Clear structure, business/HR focused

Happy practicing! 🎯
        """
        await update.message.reply_text(help_text, parse_mode="Markdown")

    async def set_difficulty(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /difficulty command - let user choose difficulty level."""
        user_id = update.message.from_user.id

        keyboard = [
            [InlineKeyboardButton("🔥 GMAT 700+", callback_data="diff_gmat")],
            [InlineKeyboardButton("🟡 CAT Advanced", callback_data="diff_cat")],
            [InlineKeyboardButton("🟢 SBI/IBPS PO", callback_data="diff_sbi")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        current_diff = self.user_difficulty.get(user_id, DEFAULT_DIFFICULTY)
        current_name = DIFFICULTY_LEVELS[current_diff]["name"]

        await update.message.reply_text(
            f"📊 Current difficulty: *{current_name}*\n\nSelect your preferred difficulty level:",
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

    async def difficulty_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle difficulty selection callback."""
        query = update.callback_query
        user_id = query.from_user.id
        difficulty_map = {
            "diff_gmat": "gmat",
            "diff_cat": "cat",
            "diff_sbi": "sbi"
        }

        difficulty = difficulty_map.get(query.data, DEFAULT_DIFFICULTY)
        self.user_difficulty[user_id] = difficulty
        diff_name = DIFFICULTY_LEVELS[difficulty]["name"]

        await query.answer()
        await query.edit_message_text(
            text=f"✅ Difficulty set to: *{diff_name}*\n\nUse /today to get your RC passage!",
            parse_mode="Markdown"
        )

    async def answer_button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle answer button clicks."""
        query = update.callback_query
        data = query.data  # Format: "ans_<question_number>_<answer>"

        try:
            parts = data.split("_")
            question_num = int(parts[1])
            user_answer = parts[2]

            if not self.current_rc:
                await query.answer("Please use /today first to get RC")
                return

            questions = self.current_rc["questions"]
            # Find question
            question = next((q for q in questions if q['number'] == question_num), None)

            if not question:
                await query.answer("Question not found", show_alert=True)
                return

            correct_answer = question['correct_answer']
            is_correct = user_answer == correct_answer

            if is_correct:
                response = f"✅ Correct! {user_answer} is the right answer!"
                await query.answer(response, show_alert=False)
            else:
                response = f"❌ Wrong! Your answer: {user_answer}\n✅ Correct answer: {correct_answer}"
                await query.answer(response, show_alert=True)

        except Exception as e:
            await query.answer(f"Error: {str(e)}", show_alert=True)

    async def today(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /today command - send today's RC."""
        try:
            user_id = update.message.from_user.id
            user_name = update.message.from_user.full_name
            difficulty = self.user_difficulty.get(user_id, DEFAULT_DIFFICULTY)

            # Track user activity
            self.analytics.track_user(user_id, user_name, difficulty)

            # Check if already sent today
            today = datetime.now().date().isoformat()
            rc_file = f"{self.data_dir}/today_rc_{difficulty}.json"

            if os.path.exists(rc_file):
                with open(rc_file, "r") as f:
                    data = json.load(f)
                    if data.get("date", "").startswith(today):
                        self.current_rc = data
                        await self._send_rc(update, difficulty)
                        return

            # Generate new RC for today
            self.current_rc = self.generator.generate_daily_rc(difficulty)

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

            await self._send_rc(update, difficulty)

        except Exception as e:
            error_msg = f"❌ Error generating RC: {str(e)}"
            if DEBUG_MODE:
                print(error_msg)
            await update.message.reply_text(error_msg)

    async def _send_rc(self, update: Update, difficulty: str) -> None:
        """Format and send the RC passage and questions."""
        if not self.current_rc:
            await update.message.reply_text("No RC loaded. Use /today first.")
            return

        passage = self.current_rc["passage"]
        topic = self.current_rc["topic"]
        questions = self.current_rc["questions"]
        difficulty_name = DIFFICULTY_LEVELS[difficulty]["name"]

        # Format passage message
        passage_msg = f"""
🎯 *Today's RC Challenge*

📌 *Topic:* {topic}
🔥 *Level:* {difficulty_name}

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
        """Handle /answer command - show answers and explanations with clickable buttons."""
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

        # Each question's answer with buttons
        for q in questions:
            # Question header
            question_header = f"""
*Q{q['number']}. {q['type'].upper()}*

{q['question']}

*Options:*
            """
            await update.message.reply_text(question_header, parse_mode="Markdown")

            # Show all options
            for i, opt in enumerate(q['options']):
                await update.message.reply_text(opt, parse_mode="Markdown")

            # Create answer buttons (2x2 layout)
            answer_keys = ['A', 'B', 'C', 'D']
            keyboard = []

            for i in range(0, 4, 2):
                row = []
                for j in range(2):
                    if i + j < len(answer_keys):
                        key = answer_keys[i + j]
                        is_correct = "✅ " if key == q['correct_answer'] else ""
                        button_text = f"{is_correct}{key}"
                        row.append(InlineKeyboardButton(button_text, callback_data=f"ans_{q['number']}_{key}"))
                if row:
                    keyboard.append(row)

            reply_markup = InlineKeyboardMarkup(keyboard)

            # Send with buttons
            buttons_msg = "*Click your answer below:*"
            await update.message.reply_text(buttons_msg, reply_markup=reply_markup, parse_mode="Markdown")

            # Show explanation
            explanation_msg = f"""
✅ *Correct Answer: {q['correct_answer']}*

*Why this is correct:*
{q['explanation']['correct']}

*Why other options are wrong:*
{q['correct_answer']} ≠ A: {q['explanation']['A'] if q['correct_answer'] != 'A' else q['explanation']['B']}

{q['correct_answer']} ≠ B: {q['explanation']['B'] if q['correct_answer'] != 'B' else q['explanation']['C']}

{q['correct_answer']} ≠ C: {q['explanation']['C'] if q['correct_answer'] != 'C' else q['explanation']['D']}

{q['correct_answer']} ≠ D: {q['explanation']['D'] if q['correct_answer'] != 'D' else q['explanation']['A']}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
            """
            await update.message.reply_text(explanation_msg, parse_mode="Markdown")

        # Summary message
        summary = """
*🎓 How to Review:*
1. Click the buttons to check your answers
2. Read the explanations for questions you missed
3. Understand WHY the answer is correct, not just WHAT it is
4. Notice patterns in your mistakes

Come back tomorrow for a new challenge! 🚀
        """
        await update.message.reply_text(summary, parse_mode="Markdown")

    async def streak_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /streak command."""
        user_id = update.message.from_user.id
        stats = self.analytics.get_user_stats(user_id)

        if stats:
            streak = stats.get("streak", 0)
            last_activity = stats.get("last_activity_date", "Never")
            total_rcs = stats.get("total_rcs", 0)

            streak_msg = f"""
🔥 *Your Practice Streak*

🎯 Current Streak: *{streak} days*
📊 Total RCs Completed: *{total_rcs}*
📅 Last Activity: {last_activity}

Keep going! Every day of practice builds your skills! 💪
            """
        else:
            streak_msg = """
🔥 *Your Practice Streak*

You haven't started practicing yet!
Use /today to begin your first challenge! 🚀
            """

        await update.message.reply_text(streak_msg, parse_mode="Markdown")

    async def mystats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /mystats command."""
        user_id = update.message.from_user.id
        stats = self.analytics.get_user_stats(user_id)

        if stats:
            streak = stats.get("streak", 0)
            total_rcs = stats.get("total_rcs", 0)
            first_seen = stats.get("first_seen", "Unknown")
            difficulty_prefs = stats.get("difficulty_preferences", {})

            # Calculate days active
            first_date = datetime.fromisoformat(first_seen).date()
            days_active = (datetime.now().date() - first_date).days + 1

            # Format difficulty preferences
            diff_text = ""
            for diff_key, count in difficulty_prefs.items():
                diff_name = DIFFICULTY_LEVELS.get(diff_key, {}).get("name", diff_key)
                diff_text += f"• {diff_name}: {count}\n"

            stats_msg = f"""
📊 *Your Personal Statistics*

🎯 Total RCs Attempted: *{total_rcs}*
🔥 Current Streak: *{streak} days*
📅 Days Active: *{days_active} days*

📈 *Difficulty Preferences:*
{diff_text if diff_text else "No data yet"}

Keep practicing to improve! 🚀
            """
        else:
            stats_msg = """
📊 *Your Personal Statistics*

You haven't started practicing yet!
Use /today to begin your first challenge! 🚀
            """

        await update.message.reply_text(stats_msg, parse_mode="Markdown")

    async def quiz_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /quiz command - practice 3 RCs in a row."""
        user_id = update.message.from_user.id
        user_name = update.message.from_user.full_name
        difficulty = self.user_difficulty.get(user_id, DEFAULT_DIFFICULTY)

        quiz_msg = """
🎯 *Quiz Mode: 3 RCs in a Row*

This will present 3 different RCs with questions.
Test your reading comprehension skills!

Generating RCs...
        """
        await update.message.reply_text(quiz_msg, parse_mode="Markdown")

        # Generate 3 RCs
        for i in range(3):
            try:
                # Track user
                self.analytics.track_user(user_id, user_name, difficulty)

                # Generate RC
                rc_data = self.generator.generate_daily_rc(difficulty)
                is_valid, message = self.generator.validate_rc(rc_data)

                if not is_valid:
                    await update.message.reply_text(f"⚠️ Error generating RC {i+1}: {message}")
                    continue

                passage = rc_data["passage"]
                topic = rc_data["topic"]
                questions = rc_data["questions"]
                difficulty_name = DIFFICULTY_LEVELS[difficulty]["name"]

                # Send passage
                passage_msg = f"""
🎯 *RC {i+1}/3*

📌 *Topic:* {topic}
🔥 *Level:* {difficulty_name}

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
                for j, q in enumerate(questions, 1):
                    question_msg = f"""
*Q{j}. {q['type'].upper()}*

{q['question']}

{chr(10).join(q['options'])}
                    """
                    await update.message.reply_text(question_msg, parse_mode="Markdown")

            except Exception as e:
                await update.message.reply_text(f"❌ Error generating RC {i+1}: {str(e)}")

        # Completion message
        completion_msg = """
✅ *Quiz Complete!*

Use /answer to check answers for today's main RC.
Use /mystats to see your progress.

Great job completing the quiz! 🎉
        """
        await update.message.reply_text(completion_msg, parse_mode="Markdown")

    async def admin_stats(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /adminstats command - admin only."""
        user_id = update.message.from_user.id

        if not self._is_admin(user_id):
            await update.message.reply_text("❌ You don't have admin access.")
            return

        stats = self.analytics.get_stats_summary()

        # Format top users
        top_users_text = ""
        for i, user in enumerate(stats["top_users"], 1):
            top_users_text += f"{i}. {user.get('user_name', 'Unknown')} - {user.get('total_rcs', 0)} RCs\n"

        admin_msg = f"""
📊 *ADMIN ANALYTICS DASHBOARD*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Overall Metrics:*
👥 Total Users: *{stats['total_users']}*
🔥 Daily Active Users: *{stats['daily_active']}*
📈 Total Interactions: *{stats['total_interactions']}*

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
*Top 5 Most Active Users:*
{top_users_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        await update.message.reply_text(admin_msg, parse_mode="Markdown")

    async def verify_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /verify_admin command - debug admin access."""
        user_id = update.message.from_user.id
        is_admin = self._is_admin(user_id)

        admin_ids_list = ", ".join(map(str, ADMIN_USER_IDS)) if ADMIN_USER_IDS else "None configured"

        verify_msg = f"""
🔐 *Admin Verification*

Your User ID: *{user_id}*
Admin IDs Configured: {admin_ids_list}
Your Status: {'✅ ADMIN' if is_admin else '❌ NOT ADMIN'}

If you should be admin:
1. Make sure `.env` has: `ADMIN_USER_IDS={user_id}`
2. Restart the bot
3. Run this command again
        """
        await update.message.reply_text(verify_msg, parse_mode="Markdown")

    async def feedback_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /feedback command."""
        feedback_msg = """
💬 *Send Feedback*

You can provide feedback about:
✅ Passage difficulty
✅ Question quality
✅ Explanation clarity
✅ Bot functionality
✅ Feature suggestions

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
        app.add_handler(CommandHandler("difficulty", self.set_difficulty))
        app.add_handler(CommandHandler("streak", self.streak_command))
        app.add_handler(CommandHandler("mystats", self.mystats_command))
        app.add_handler(CommandHandler("quiz", self.quiz_command))
        app.add_handler(CommandHandler("adminstats", self.admin_stats))
        app.add_handler(CommandHandler("verify_admin", self.verify_admin))
        app.add_handler(CommandHandler("feedback", self.feedback_command))

        # Callback handlers
        app.add_handler(CallbackQueryHandler(self.difficulty_callback, pattern="^diff_"))
        app.add_handler(CallbackQueryHandler(self.answer_button_callback, pattern="^ans_"))

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
    print(f"Admin users: {ADMIN_USER_IDS if ADMIN_USER_IDS else 'None configured'}")

    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
