#!/usr/bin/env python
"""
Script to send RC via GitHub Actions scheduled job.
Used by: .github/workflows/daily-rc.yml
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from scheduler import RCScheduler


async def main():
    """Send RC to configured chat."""
    print("[INFO] Starting scheduled RC send...")

    scheduler = RCScheduler()
    await scheduler.send_now()

    print("[INFO] Scheduled send completed!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[INFO] Cancelled")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
