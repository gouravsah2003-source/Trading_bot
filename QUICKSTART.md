# Quick Start Guide

## 🏃 Fast Setup (5 minutes)

### 1️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 2️⃣ Get Bybit Testnet Credentials
1. Go to https://testnet.bybit.com
2. Sign up / Log in
3. Account → API Settings → Create New Key
4. Copy Key and Secret

### 3️⃣ Configure .env
Edit the `.env` file:
```env
BYBIT_API_KEY=paste_your_key_here
BYBIT_API_SECRET=paste_your_secret_here
```

## ▶️ Run the Bot

```bash
python main.py
```

## 📅 When Does It Run?

The bot automatically waits for **17:30 UTC** daily, then:
- ⏰ 17:30:00.000 — Funding happens
- ⚡ 17:30:00.100 — Bot enters SHORT
- 🔄 For 2 seconds...
- 📊 17:30:02.100 — Bot exits position

## 💰 Position Size

Default: **$100 USDT** on RESOLVUSDT

To change, edit `.env`:
```env
POSITION_SIZE_USDT=500  # For $500 position
```

## 📊 What You'll See

```
✓ Connected to Bybit TESTNET
Current price: $1.2...
Calculated quantity: 81.22 RESOLVUSDT

⏰ Funding in 00:45.321
...
✓ Funding settlement time reached!
⚡ ENTRY TIME REACHED (offset: 0.45ms)
✓ SHORT position OPENED
⏱️  Holding position for 2 seconds...
✓ EXIT TIME REACHED (offset: -0.23ms)
✓ SHORT position CLOSED

--- PERFORMANCE ---
Profit/Loss: +$0.50
P&L %: +0.50%
Timing Error: 0.23ms
✓ Timing WITHIN tolerance (10ms)
```

## ⚙️ Key Settings

| Setting | Default | What it does |
|---------|---------|-----|
| `POSITION_SIZE_USDT` | 100 | How much USDT to invest per trade |
| `SYMBOL` | RESOLVUSDT | What coin to trade |
| `FUNDING_TIME_HHmm` | 17:30 | When funding happens |
| `ENTRY_DELAY_MS` | 100 | Milliseconds after funding to enter |
| `EXIT_DELAY_S` | 2 | How many seconds to hold |

## 🔐 Security Checklist

- [ ] Using **testnet** API keys (not mainnet)
- [ ] API keys in `.env` file (NOT shared or public)
- [ ] No credentials in code or version control
- [ ] Testnet account has sufficient balance
- [ ] IP whitelist enabled on Bybit (optional but recommended)

## ❌ Troubleshooting

**Bot doesn't start?**
- Check `.env` file has correct API credentials
- Run: `python main.py` from the correct folder

**"API credentials not configured" error?**
- Make sure `.env` file exists and has:
  ```env
  BYBIT_API_KEY=your_actual_key
  BYBIT_API_SECRET=your_actual_secret
  ```

**Orders failing?**
- Check testnet account balance
- Verify RESOLVUSDT is available to trade
- Internet connection working properly

**Timing errors large (>100ms)?**
- Close other applications
- Check internet latency
- Try again later (server load)

## 📚 Next Steps

1. **Run it:** `python main.py` at any time
2. **Monitor:** Watch console output and logs
3. **Check logs:** `trading_bot_*.log` file in same folder
4. **Test adjustments:** Modify `.env` settings and re-run

## 📔 Log Files

Every run creates a log file: `trading_bot_YYYYMMDD_HHMMSS.log`

View latest logs:
```bash
# Windows
type trading_bot_*.log | more

# Or open in text editor
```

## ✅ You're Ready!

The bot is configured and ready to run. Just start it and let it wait for 17:30 UTC!

```bash
python main.py
```

Good luck! 🚀
