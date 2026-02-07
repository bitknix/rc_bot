"""
Main entry point for RC Bot.
Supports running bot only, scheduler only, or both.
"""
import asyncio
import sys
import os
from bot import RCBot
from scheduler import RCScheduler


async def run_bot_only():
    """Run only the interactive Telegram bot."""
    print("🤖 Starting RC Bot (interactive mode)...")
    print("Users can use /today and other commands manually\n")

    bot = RCBot()
    app = bot.get_application()

    try:
        await app.initialize()
        await app.start()
        await app.updater.start_polling(allowed_updates=None)
        print("✅ Bot started. Press Ctrl+C to stop.\n")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n⛔ Bot stopped")
        await app.stop()
        await app.shutdown()


async def run_scheduler_only():
    """Run only the daily scheduler (no interactive commands)."""
    print("📅 Starting RC Scheduler (automated daily sends)...")
    print("RC will be sent automatically at configured time\n")

    scheduler = RCScheduler()
    try:
        await scheduler.start_scheduler()
    except KeyboardInterrupt:
        print("\n⛔ Scheduler stopped")


async def run_both():
    """Run both bot and scheduler concurrently."""
    print("🚀 Starting RC Bot with Scheduler...")
    print("- Interactive commands enabled (/today, /answer, etc.)")
    print("- Daily RC will auto-send at configured time\n")

    bot = RCBot()
    scheduler = RCScheduler()

    app = bot.get_application()

    try:
        await app.initialize()
        await app.start()

        # Run both concurrently
        await asyncio.gather(
            app.updater.start_polling(allowed_updates=None),
            scheduler.start_scheduler()
        )

        print("✅ Bot and Scheduler started. Press Ctrl+C to stop.\n")
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("\n⛔ Bot and Scheduler stopped")
        await app.stop()
        await app.shutdown()


def main():
    """Parse arguments and run appropriate mode."""
    mode = sys.argv[1] if len(sys.argv) > 1 else "bot"

    if mode == "bot":
        print("=" * 60)
        asyncio.run(run_bot_only())
    elif mode == "scheduler":
        print("=" * 60)
        asyncio.run(run_scheduler_only())
    elif mode == "both":
        print("=" * 60)
        asyncio.run(run_both())
    elif mode == "test":
        # Test RC generation
        from rc_generator import RCGenerator
        print("=" * 60)
        print("🧪 Testing RC Generation...\n")

        gen = RCGenerator()
        rc = gen.generate_daily_rc()

        is_valid, msg = gen.validate_rc(rc)
        print(f"✅ Validation: {msg}\n")

        print(f"Topic: {rc['topic']}")
        print(f"Passage ({len(rc['passage'].split())} words):\n")
        print(rc['passage'][:200] + "...\n")

        for q in rc['questions']:
            print(f"Q{q['number']}: {q['question']}")
            print(f"Answer: {q['correct_answer']}\n")

    else:
        print(f"Unknown mode: {mode}")
        print("\nUsage:")
        print("  python main.py bot       - Run interactive RC bot only")
        print("  python main.py scheduler - Run daily auto-send scheduler only")
        print("  python main.py both      - Run both bot and scheduler")
        print("  python main.py test      - Test RC generation")
        sys.exit(1)


if __name__ == "__main__":
    main()
