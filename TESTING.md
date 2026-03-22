# Testing & Validation Guide

Complete guide for testing the bot before production use.

## ✅ Pre-Flight Checklist

Before running the bot, verify these items:

### 1. Environment Setup
- [ ] Python 3.8+ installed (`python --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] `.env` file exists in project folder
- [ ] `.env` contains valid credentials

### 2. Bybit Account
- [ ] Testnet account created (https://testnet.bybit.com)
- [ ] API key generated and copied
- [ ] API secret generated and copied
- [ ] Account has minimum balance (~$200 USDT for $100 trades)

### 3. Configuration
- [ ] `BYBIT_API_KEY` set in `.env`
- [ ] `BYBIT_API_SECRET` set in `.env`
- [ ] `SYMBOL` is valid (RESOLVUSDT recommended)
- [ ] `FUNDING_TIME_HHmm` verified correct (usually 17:30)

### 4. System
- [ ] Internet connection stable
- [ ] System clock synchronized (NTP)
- [ ] Sufficient disk space for logs

---

## 🧪 Step-by-Step Testing

### Test 1: Python & Dependencies

**Goal:** Verify Python and libraries are installed correctly

**Steps:**
```bash
# Check Python version
python --version
# Should show: Python 3.8.0 or newer

# Check dependencies
pip list | findstr pybit
# Should show: pybit X.X.X

pip list | findstr python-dotenv
# Should show: python-dotenv X.X.X
```

**Expected:** All libraries show version numbers  
**If Failed:** Run `pip install -r requirements.txt` again

---

### Test 2: .env File Configuration

**Goal:** Verify .env file is readable and contains API credentials

**Steps:**
```bash
# View .env file
type .env

# Should show:
# BYBIT_API_KEY=your_key_here
# BYBIT_API_SECRET=your_secret_here
# ... other settings ...
```

**Expected:** File shows all settings  
**If Failed:** Check .env file exists in current folder

---

### Test 3: API Connectivity

**Goal:** Verify bot can connect to Bybit API

**Steps:**
```bash
# Start bot
python main.py

# Watch output for first line
```

**Expected Output:**
```
[2026-03-22 HH:MM:SS.xxx] [INFO] ✓ Connected to Bybit TESTNET
[2026-03-22 HH:MM:SS.xxx] [INFO] ✓ API credentials validated
[2026-03-22 HH:MM:SS.xxx] [INFO] Current price: $X.XX
[2026-03-22 HH:MM:SS.xxx] [INFO] Calculated quantity: X.XX RESOLVUSDT
```

**If Failed:**
- ✅ Check internet connection
- ✅ Verify API key/secret in .env
- ✅ Confirm testnet account has balance
- ✅ Check that SYMBOL is tradeable

---

### Test 4: Ticker Data

**Goal:** Verify bot receives real-time price data

**From Test 3 output, verify:**
```
Current price: $1.234567
Calculated quantity: 81.22 RESOLVUSDT
```

**Expected:**
- Price is number with decimals
- Quantity is reasonable (> 0.01)
- Price matches Bybit testnet website

**If Failed:**
- Check SYMBOL is correct (RESOLVUSDT)
- Verify symbol is trading on testnet
- Check internet connection

---

### Test 5: Real Trade Execution (Testnet)

**Goal:** Execute actual trade and verify timing/PnL

**Prerequisites:**
- Testnet account has > $100 USDT balance
- All previous tests passed

**Steps:**
1. Note current time
2. Run: `python main.py`
3. Wait for it to connect
4. Let it run until funding time (17:30 UTC)
5. **OR** Modify FUNDING_TIME to be 2 minutes from now (for testing)

**Example - Testing at Custom Time:**

Edit `.env` temporarily:
```env
FUNDING_TIME_HHmm=14:30  # Change to 2 minutes from now
```

Then run bot:
```bash
python main.py
```

**Expected Sequence:**
```
[14:28:XX.XXX] [INFO] ⏰ Funding in 02:XX.XXX
[14:28:XX.XXX] [INFO] ⏰ Funding in 01:XX.XXX
[14:29:XX.XXX] [INFO] ✓ Funding settlement time reached!
[14:30:00.XXX] [INFO] ⚡ ENTRY TIME REACHED (offset: 0.45ms)
[14:30:00.XXX] [INFO] ✓ SHORT position OPENED
[14:30:00.XXX] [INFO] ⏱️  Holding position for 2 seconds...
[14:30:01.XXX] [INFO]   2s remaining...
[14:30:01.XXX] [INFO]   1s remaining...
[14:30:02.XXX] [INFO] ✓ EXIT TIME REACHED (offset: -0.23ms)
[14:30:02.XXX] [INFO] ✓ SHORT position CLOSED

======================================================================
TRADE SUMMARY
======================================================================
Profit/Loss: $X.XX
P&L %: X.XX%
Hold Duration: 2.00XXXX (Target: 2s)
Timing Error: X.XXms
✓ Timing WITHIN tolerance (10ms)
```

**What to Verify:**
- ✅ Entry timestamp shows 0.1s after funding
- ✅ Exit timestamp shows ~2s after entry
- ✅ PnL calculated (positive or negative)
- ✅ Timing error ≤ 10ms
- ✅ No error messages

---

### Test 6: Log File Review

**Goal:** Verify all actions logged correctly

**Steps:**
```bash
# Find latest log file
dir trading_bot_*.log

# View log file
type trading_bot_YYYYMMDD_HHMMSS.log | more
```

**Expected:** Log contains:
- ✅ Connection confirmation
- ✅ Entry order details
- ✅ Exit order details
- ✅ All timestamps with milliseconds
- ✅ PnL calculations
- ✅ No error stack traces

---

## 📊 Validation Metrics

After each test, check these numbers:

### Timing Validation
```
Target Entry: 17:30:00.100
Actual Entry: 17:30:00.145 (offset: 0.45ms) ✓

Target Hold: 2.000s
Actual Hold: 2.000123s (error: 0.123ms) ✓

Target Exit: 17:30:02.100
Actual Exit: 17:30:02.099 (offset: -0.10ms) ✓
```

**Success Criteria:**
- Entry offset: ±5ms acceptable
- Exit offset: ±10ms acceptable (default tolerance)
- Hold duration: ±50ms acceptable

### Price Validation
```
Entry Price: $1.2345
Exit Price: $1.2347

Price Diff: $0.0002
PnL: $0.00 (based on quantity)
PnL %: 0.02%
```

**Realistic Values:**
- Price difference: ±$0.10 (varies by volatility)
- Small profit/loss is normal (due to slippage)

---

## 🚀 Stress Testing

### Test 7: Multiple Consecutive Runs

**Goal:** Verify bot works reliably over multiple cycles

**Steps:**
```bash
# Modify FUNDING_TIME to test every 5 minutes
# FUNDING_TIME_HHmm=17:30 → 17:35 (in 5 mins)

# Run Test 5 three times in a row
python main.py  # Run 1
python main.py  # Run 2
python main.py  # Run 3
```

**Expected:**
- All three runs complete successfully
- Similar timing accuracy each run
- No increasing errors

**Success Criteria:**
- 3/3 trades executed
- Timing consistent (±10ms variance)
- No crashes or errors

---

### Test 8: Network Latency Tolerance

**Goal:** Verify bot handles latency well

**Steps:**
```bash
# Open another terminal, monitor latency
ping api-testnet.bybit.com

# Run bot while monitoring
python main.py
```

**Expected:**
- Bot works even with 100-200ms latency
- Timing error increases with latency (normal)
- But still within tolerance

**If Timing Error > 50ms:**
- Close unnecessary applications
- Try a different network
- Check Bybit API status page

---

## 🔍 Error Detection

### What to Watch For

| Error | What it means | Fix |
|-------|--------------|-----|
| "API credentials not configured" | No API key in .env | Add credentials to .env |
| "Failed to get ticker" | Can't reach API | Check internet connection |
| "Order placement failed" | Order didn't execute | Check account balance |
| "Timing error: 50ms" | Slow network | Close other apps, reduce position |
| "KeyError: 'avgPrice'" | Order didn't fill | Increase timeout or retry |

---

## ✅ Final Sign-Off Checklist

Before running on mainnet, confirm:

- [ ] Test 1 passed (Python & dependencies)
- [ ] Test 2 passed (.env configuration)
- [ ] Test 3 passed (API connectivity)
- [ ] Test 4 passed (ticker data)
- [ ] Test 5 passed (real trade execution)
- [ ] Test 6 passed (log file review)
- [ ] Test 7 passed (multiple runs)
- [ ] Test 8 passed (network tolerance)
- [ ] Timing error consistently ≤ 10ms
- [ ] All trades executed successfully
- [ ] No unhandled exceptions

---

## 🔄 Regression Testing

After any changes to code:

1. **Run basic tests** (Tests 1-4)
2. **Run one live trade** (Test 5)
3. **Review logs** (Test 6)
4. **Verify timing** is still accurate

---

## 📈 Monitoring for Production

Once approved for mainnet:

1. **Daily monitoring**
   - Check post-trade logs
   - Verify PnL is reasonable
   - Confirm timing accuracy

2. **Weekly review**
   - Trend in PnL
   - Network latency trends
   - Any failed trades

3. **Monthly report**
   - Total PnL
   - Win rate
   - Average timing error
   - Consistency metrics

---

## 💾 Backup & Recovery

### Before Going Live

```bash
# Backup current working bot
copy main.py main.py.backup
copy .env .env.backup

# If issues arise, restore:
copy main.py.backup main.py
copy .env.backup .env
```

### Disaster Recovery

If bot crashes:
1. Stop the bot (Ctrl+C)
2. Check latest log file for error
3. Fix issue
4. Restart bot
5. Monitor first trade carefully

---

## 📞 Support Debugging

If tests fail, collect this info:

1. Python version: `python --version`
2. Pybit version: `pip show pybit`
3. Error message (from console)
4. Full log file (latest trading_bot_*.log)
5. Your .env file (credentials redacted)

---

**Ready to Trade?**

Once all tests pass, you're ready to:
1. Update API credentials to mainnet (optional)
2. Adjust POSITION_SIZE_USDT to real amount
3. Start the bot for production trading

Good luck! 🚀

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-22
