# 🚀 DEPLOYMENT GUIDE - Free Hosting for RC Bot

Choose your hosting option below. All are **completely FREE**.

---

## Option 1: Railway ⭐ (RECOMMENDED)

Railway is the easiest - it auto-deploys from GitHub and gives you **5 GB per month free** (more than enough).

### Step-by-Step Railway Setup

**1. Push Code to GitHub**

```bash
git add .
git commit -m "Initial commit: RC bot"
git push origin main
```

**2. Create Railway Account**

- Go to: https://railway.app
- Click "Sign up"
- Sign in with GitHub (easiest)
- Authorize Railway access

**3. Create New Project**

- Click "New Project"
- Select "Deploy from GitHub repo"
- Search for your `rc_bot` repository
- Click "Import"

**4. Add Environment Variables**

In Railway dashboard:

1. Go to Variables
2. Click "Raw Editor"
3. Add:

```
TELEGRAM_TOKEN=your_bot_token_here
HF_API_TOKEN=your_hf_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
DAILY_SEND_TIME=08:00
TIMEZONE=UTC
```

**5. Deploy**

- Railway auto-detects `Procfile`
- Deployment starts automatically
- Wait for "Active" status (2-3 minutes)

**6. Verify Bot Works**

In Telegram:
- Go to your bot
- Type `/today`
- Should see RC!

---

## Option 2: GitHub Actions (FREE SCHEDULING)

Use GitHub Actions to schedule RC sending (no server needed).

### GitHub Actions Setup

**1. Add GitHub Secrets**

Go to: **Settings → Secrets and variables → Actions**

Click "New repository secret" and add:
- `TELEGRAM_TOKEN` = your_bot_token
- `HF_API_TOKEN` = your_hf_token
- `TELEGRAM_CHAT_ID` = your_chat_id

**2. Workflow File Already Created**

The file `.github/workflows/daily-rc.yml` is ready! It:
- Runs every day at 8 AM UTC
- Sends RC to your chat automatically
- Requires no server

**3. Enable Actions**

- Go to: **Actions** tab
- If disabled, click "Enable Actions"
- Done!

**4. Test Manually**

To test before automated runs:
1. Go to **Actions** tab
2. Click "Daily RC Send"
3. Click "Run workflow" → "Run workflow"
4. Should send RC to your chat in ~2 minutes

### ⚠️ Important Notes

- **Chat ID required**: You must set `TELEGRAM_CHAT_ID` for this to work
- **Get your chat ID**:
  1. Run bot locally: `python main.py bot`
  2. Send any message to bot in Telegram
  3. Terminal output shows your user ID
  4. Use that as `TELEGRAM_CHAT_ID`

---

## Option 3: Render (Alternative to Railway)

Free tier supports 1 project. Similar setup to Railway.

### Render Setup

**1. Create Account**

- Go to: https://render.com
- Sign up with GitHub

**2. Create Service**

- Click "New +" → "Web Service"
- Connect GitHub repository
- Select your `rc_bot` repo

**3. Configure**

| Field | Value |
|-------|-------|
| Name | rc-bot |
| Environment | Python 3 |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `python main.py both` |
| Plan | Free |

**4. Add Environment Variables**

Click "Environment" and add:
- `TELEGRAM_TOKEN`
- `HF_API_TOKEN`
- `TELEGRAM_CHAT_ID`
- `TIMEZONE=UTC`
- `DAILY_SEND_TIME=08:00`

**5. Deploy**

- Click "Create Web Service"
- Renders automatically
- Wait for "Live" status

---

## Option 4: Heroku (PAID NOW - Not Recommended)

Heroku shut down free tier. Skip this.

---

## 🔄 Combined Setup (BEST)

Use **Railway for 24/7 bot** + **GitHub Actions for daily scheduling**:

### Why This?

- **Railway bot**: Always online for `/today`, `/answer`, etc.
- **GitHub Actions**: Automated daily sends at 8 AM
- **Cost**: $0 (both free tiers)
- **Reliability**: Redundant, if one fails, other works

### Setup

1. Deploy to Railway (see Option 1)
2. Set up GitHub Actions (see Option 2)
3. In Railway:
   - Set `DAILY_SEND_TIME` to something Railway won't hit
   - Or in `.env`: `DAILY_SEND_TIME=23:00` (11 PM)
4. GitHub Actions sends at 8 AM
5. Railway bot available 24/7 for user commands

---

## 📋 Checklist Before Deployment

### Code

- [ ] `.gitignore` includes `.env`
- [ ] `requirements.txt` has all dependencies
- [ ] `Procfile` exists and correct
- [ ] `.github/workflows/daily-rc.yml` exists
- [ ] `send_rc.py` exists
- [ ] No hardcoded tokens in code

### Tokens

- [ ] Telegram token from @BotFather
- [ ] HuggingFace token from https://huggingface.co/settings/tokens
- [ ] Chat ID (optional, only for automated scheduling)

### GitHub

- [ ] Repository is **public** (to allow Actions)
- [ ] GitHub Actions are **enabled**
- [ ] Secrets added: `TELEGRAM_TOKEN`, `HF_API_TOKEN`, `TELEGRAM_CHAT_ID`

### Hosting

- [ ] Railway: Deployed and "Active"
  OR
- [ ] GitHub Actions: Running (check Actions tab)

---

## 🧪 Testing Deployed Bot

**Test 1: Manual Command in Telegram**

```
/today      → Should get RC immediately
/answer     → Should get answers
```

**Test 2: GitHub Actions**

1. Go to **Actions** tab
2. Click "Daily RC Send"
3. Click "Run workflow"
4. Should send RC in 2-3 minutes

**Test 3: Scheduled Sending**

Wait until 8 AM UTC next day. Should receive RC automatically.

---

## 🐛 Troubleshooting

### Bot Not Responding in Telegram

**Check:**
1. Is `TELEGRAM_TOKEN` correct?
2. Is bot running? (Check Railway dashboard)
3. Did you @mention the bot? (Not needed, just send directly)
4. Is bot online in Railway?

**Fix:**
```bash
# Test locally first
python main.py bot

# Check token
echo $TELEGRAM_TOKEN  # Should print token
```

### No Automatic Sends (GitHub Actions)

**Check:**
1. Is `TELEGRAM_CHAT_ID` set?
2. Is it the correct ID? (Run locally to verify)
3. Are Actions enabled? (Check Settings → Actions)
4. Did you add secrets? (Check Settings → Secrets)

**Fix:**
1. Go to Actions tab
2. Click "Daily RC Send"
3. Click "Run workflow" manually to test

### Railway Build Failing

**Check:**
1. Do all imports work? `python -c "from rc_generator import RCGenerator"`
2. Are all dependencies in `requirements.txt`?
3. Is `Procfile` correct?

**Fix:**
```bash
# Test locally
python -m pip install -r requirements.txt
python main.py bot
```

---

## 💰 Cost Comparison

| Option | Monthly Cost | Pros | Cons |
|--------|-------------|------|------|
| **Railway** | $0 (5 GB free) | Auto-deploy, easy updates | Sleeping after 1 month inactive |
| **GitHub Actions** | $0 (unlimited) | Reliable scheduling | Need Chat ID setup |
| **Render** | $0 (paid after 1 mo) | Simple setup | Limited to 1 project free |
| **Local Machine** | $0 | Full control | Must keep PC on 24/7 |

---

## 🔄 Updates & Maintenance

### Deploying Updates

**Railway Auto-Updates**
- Push to GitHub: `git push origin main`
- Railway redeploys automatically
- ✅ No downtime

**GitHub Actions Auto-Updates**
- Pulls latest code from `main` branch
- ✅ No manual step needed

### Logs

**Railway Logs**
1. Dashboard → Logs tab
2. See real-time output

**GitHub Actions Logs**
1. Actions tab → Latest run
2. Click to see full logs

---

## 🎯 Next Steps

1. **Choose hosting** (Railway recommended)
2. **Add secrets** to GitHub and/or hosting platform
3. **Test locally**: `python main.py bot`
4. **Deploy**: Push to GitHub
5. **Verify**: Test `/today` in Telegram
6. **Schedule** (optional): Enable GitHub Actions for daily sends

---

**Questions?** Check logs, verify tokens, test locally first!
