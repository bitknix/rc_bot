# 📚 GMAT/CAT/SBI-IBPS RC Bot - Daily Reading Comprehension Practice

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Telegram](https://img.shields.io/badge/Telegram-Active-blue.svg)](https://telegram.org/)

A sophisticated Telegram bot that delivers **daily reading comprehension practice with multiple difficulty levels** (GMAT 700+, CAT Advanced, SBI/IBPS PO) featuring AI-generated or curated passages, inference-heavy questions, detailed explanations, user analytics, streak tracking, and quiz mode.

## ✨ Features

- **🔥 Multiple Difficulty Levels**:
  - **GMAT 700+**: Ultra-dense abstract prose with implicit author stance (420-520 words)
  - **CAT Advanced**: Dense academic content with moderate complexity (380-480 words)
  - **SBI/IBPS PO**: Clear business/HR focused passages (250-350 words)

- **📚 Daily Practice**: One challenging passage per day at your chosen level
- **4 Expert Questions**: Primary purpose, inference, tone/attitude, logical implication
- **Detailed Explanations**: Why each answer works and why others fail
- **🎯 Quiz Mode**: Practice 3 passages in one session
- **🔥 Streak Tracking**: Track your daily practice streak
- **📊 Personal Stats**: View your progress (total RCs, favorite difficulty level, days active)
- **👥 Admin Analytics Dashboard**: View overall user engagement metrics
- **Rotating Topics**: Philosophy, Economics, Politics, Cognitive Science, Sociology, History
- **Live AI Generation**: Uses HuggingFace OpenAI API (or pre-crafted fallback)
- **No Cost**: Completely free using HuggingFace free tier
- **Easy Deployment**: GitHub Actions for scheduling, Railway/Render for hosting

## 🎯 Difficulty Levels

### 🔥 GMAT 700+ (Hardest)
- Ultra-dense abstract prose with complex nested sentences
- 420-520 word passages
- Implicit author stance and ambiguous transitions
- Requires deep logical inference
- Best for: GMAT preparation, advanced learners

### 🟡 CAT Advanced (Medium)
- Dense academic content with complex ideas
- 380-480 word passages
- Somewhat implicit author perspective
- Balanced comprehension and inference
- Best for: CAT preparation, intermediate learners

### 🟢 SBI/IBPS PO (Easiest)
- Clear, well-structured prose with explicit meaning
- 250-350 word passages
- Business/HR/management focused topics
- Practical concepts with clear examples
- Best for: Banking exams, beginners, quick practice

## 📱 Commands

| Command | Description |
|---------|-------------|
| `/start` | Welcome message and feature overview |
| `/today` | Get today's RC passage at your selected difficulty |
| `/answer` | View answers with detailed explanations |
| `/difficulty` | Choose your difficulty level (GMAT/CAT/SBI-IBPS) |
| `/quiz` | Practice 3 passages in one session |
| `/streak` | View your practice streak and total RCs |
| `/mystats` | Personal statistics (total RCs, days active, difficulty preferences) |
| `/adminstats` | **[ADMIN ONLY]** View overall analytics dashboard |
| `/feedback` | Send feedback to improve the bot |
| `/help` | Show all available commands |

## 🚀 Quick Start (5 minutes)

```bash
# Open Telegram, search @BotFather
# Send: /newbot
# Choose name (e.g., "RC Daily Bot")
# Choose username (e.g., "rc_daily_bot")
# Copy the token (40+ character string)
```

### 2. Clone Repository

```bash
git clone https://github.com/yourusername/rc_bot.git
cd rc_bot
```

### 3. Setup Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate
# OR (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure

```bash
# Copy example config
cp .env.example .env

# Edit .env with your tokens:
# TELEGRAM_TOKEN=your_bot_token_from_botfather
# HF_API_TOKEN=your_huggingface_token (optional)
```

### 5. Test Locally

```bash
# Generate sample RC
python main.py test

# Start bot (interactive mode)
python main.py bot

# In Telegram:
/today      # Get today's RC
/answer     # See explanations
```

## 📦 Installation

### Requirements
- Python 3.10+
- HuggingFace account (free)
- Telegram bot token (free from @BotFather)

### Setup Steps

1. **Install Python**: https://www.python.org/downloads/

2. **Get HuggingFace Token**:
   ```
   Go to: https://huggingface.co/settings/tokens
   Click "New token"
   Select: Access type = Read
   Copy the token
   ```

3. **Clone and Install**:
   ```bash
   git clone https://github.com/yourusername/rc_bot.git
   cd rc_bot
   python -m venv venv
   source venv/bin/activate  # or venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

4. **Configure**:
   ```bash
   cp .env.example .env
   # Edit .env with your tokens
   ```

5. **Run**:
   ```bash
   python main.py bot
   ```

## 🌐 Free Hosting Options

### Option 1: GitHub Actions (Recommended for Scheduling)

Automatically send RC every day without a running server.

**Setup:**

1. Create `.github/workflows/daily-rc.yml`:

```yaml
name: Daily RC Send

on:
  schedule:
    - cron: '0 8 * * *'  # 8 AM UTC daily

jobs:
  send-rc:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      - run: pip install -r requirements.txt
      - run: python send_rc.py
        env:
          TELEGRAM_TOKEN: ${{ secrets.TELEGRAM_TOKEN }}
          HF_API_TOKEN: ${{ secrets.HF_API_TOKEN }}
          TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
```

2. Add secrets to GitHub:
   - Go to: Settings → Secrets and variables → Actions
   - Add: `TELEGRAM_TOKEN`, `HF_API_TOKEN`, `TELEGRAM_CHAT_ID`

3. Create `send_rc.py`:

```python
#!/usr/bin/env python
import asyncio
from scheduler import RCScheduler

async def main():
    scheduler = RCScheduler()
    await scheduler.send_now()

if __name__ == "__main__":
    asyncio.run(main())
```

### Option 2: Railway (Free Tier)

Host the bot continuously on Railway's free tier.

**Setup:**

1. Go to: https://railway.app
2. Click "New Project" → "Deploy from GitHub"
3. Select your repository
4. Add environment variables:
   - `TELEGRAM_TOKEN`
   - `HF_API_TOKEN`
   - `TELEGRAM_CHAT_ID` (optional)
5. Create `Procfile`:

```
worker: python main.py both
```

6. Push to GitHub:

```bash
git add .
git commit -m "Add Railway configuration"
git push origin main
```

Railway will auto-deploy!

### Option 3: Render (Free Tier)

Similar to Railway, free tier allows 1 project.

**Setup:**

1. Go to: https://render.com
2. Click "New+" → "Web Service"
3. Connect GitHub repository
4. Set build command: `pip install -r requirements.txt`
5. Set start command: `python main.py both`
6. Add environment variables
7. Deploy!

## 📁 Project Structure

```
rc_bot/
├── config.py              # Configuration (tokens, topics, etc.)
├── rc_generator.py        # RC passage & question generation
├── bot.py                 # Telegram bot commands
├── scheduler.py           # Daily scheduling logic
├── send_rc.py            # Script for GitHub Actions
├── main.py               # Entry point
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── .gitignore            # Git ignore rules
├── Procfile              # For Heroku/Railway/Render
├── README.md             # This file
└── data/                 # Generated content (git-ignored)
    ├── passages_log.json
    ├── feedback.jsonl
    └── send_log.json
```

## 🔧 Configuration

### .env File

```bash
# Telegram Bot Token (required)
TELEGRAM_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11

# HuggingFace API Token (optional - uses fallback if not set)
HF_API_TOKEN=hf_xxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Chat ID for scheduled sending (optional)
TELEGRAM_CHAT_ID=123456789

# Scheduling
DAILY_SEND_TIME=08:00
TIMEZONE=UTC

# Debug mode
DEBUG_MODE=False
```

### Environment Variables

All configuration via environment variables (no code changes needed):

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_TOKEN` | Bot authentication | ✅ Yes |
| `HF_API_TOKEN` | HuggingFace API access | ❌ No (uses fallback) |
| `TELEGRAM_CHAT_ID` | For scheduled sends | ❌ No |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | ❌ No |
| `DAILY_SEND_TIME` | Send time (HH:MM UTC) | ❌ No (08:00 default) |
| `TIMEZONE` | Timezone for sends | ❌ No (UTC default) |
| `DEBUG_MODE` | Enable debug logging | ❌ No |

### Getting Admin User ID

To set yourself as an admin:
1. Start the bot and send `/start`
2. Check the bot's console output (if running locally)
3. Look for your user ID
4. Add to `.env`: `ADMIN_USER_IDS=your_user_id`
5. Now you can use `/adminstats` command

## 🎓 Passage Quality

Passages are tailored to your chosen difficulty level:

### GMAT 700+ Level
- 420-520 word passages
- Dense academic prose with complex structures
- Implicit author stance
- Ambiguous transitions requiring inference
- Logical tensions between ideas

### CAT Advanced Level
- 380-480 word passages
- Moderately complex academic content
- Somewhat implicit author perspective
- Balanced structure with clear paragraphs
- Mix of direct and implicit meanings

### SBI/IBPS PO Level
- 250-350 word passages
- Clear, business/HR focused topics
- Explicit meanings and direct language
- Practical examples and case studies
- Easy to moderate comprehension level

### Question Types

1. **Primary Purpose** - Identify author's main goal
2. **Inference** - Understand implicit meaning
3. **Tone/Attitude** - Recognize author's stance
4. **Logical Implication** - Reason about consequences

## 📊 User Analytics & Statistics

### Personal Statistics (`/mystats`)
- Total RC passages attempted
- Current practice streak (days)
- Days you've been active
- Difficulty level preferences
- Progress over time

### Admin Dashboard (`/adminstats`)
**[Requires Admin Access]**
- Total registered users
- Daily active users
- Total practice interactions
- Top 5 most active users by RC count
- Generated timestamp

### Data Tracking
The bot automatically tracks:
- User ID and name
- First seen and last seen timestamps
- Total RC attempts
- Difficulty preferences
- Streak and practice dates
- All activity logged in `data/analytics.jsonl`

## 🤝 Contributing

Contributions welcome! To contribute:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes
4. Add tests if applicable
5. Commit: `git commit -m "Add your feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see LICENSE file for details.

## 🙏 Acknowledgments

- HuggingFace for free inference API
- Telegram for bot platform
- Railway/Render for free hosting

## 🐛 Issues & Support

Found a bug? Have a suggestion?

1. Check [existing issues](../../issues)
2. Create a [new issue](../../issues/new)
3. Include:
   - Description of the problem
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS

## 📚 Resources

- [Telegram Bot API](https://core.telegram.org/bots/api)
- [HuggingFace Documentation](https://huggingface.co/docs)
- [Railway Docs](https://docs.railway.app/)
- [Render Docs](https://render.com/docs)

## 🚀 Deployment Checklist

Before pushing to production:

- [ ] `.env.example` has all required variables
- [ ] `.gitignore` excludes sensitive files
- [ ] `requirements.txt` has all dependencies
- [ ] Bot works locally with `python main.py bot`
- [ ] RC generation test passes
- [ ] GitHub secrets configured
- [ ] Procfile or workflow file created

## 💡 Tips

**For best results:**

1. **Read twice**: Read passage twice before answering
2. **Eliminate first**: Remove obviously wrong options
3. **Watch tone**: Pay attention to author's subtle stance
4. **Logical flow**: Understand connections between paragraphs
5. **Use context**: Don't rely on external knowledge

## 📞 Contact

Questions or feedback? Open an issue or reach out!

---

**Made with ❤️ for GMAT/CAT aspirants**

_Last updated: 2025-02-07_
