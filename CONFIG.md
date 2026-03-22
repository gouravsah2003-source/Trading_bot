# Configuration Guide

Complete documentation of all configuration options and settings.

## 📄 .env File Reference

All configuration is managed through the `.env` file. Below is the complete reference.

### API Credentials (REQUIRED)

```env
BYBIT_API_KEY=tyVnYjHAjcnUN62rPv
BYBIT_API_SECRET=O0OOCJ4O67ebqOV2bggp31cRZtxNrD2CMxTk
```

**BYBIT_API_KEY**
- Your Bybit API key (from Account → API Settings)
- **Type:** String
- **Required:** YES
- **Default:** None
- **Example:** `BYBIT_API_KEY=XXXXXXXXXXXXXXXXXXXXXX`
- **⚠️ Important:** Never share this key

**BYBIT_API_SECRET**
- Your Bybit API secret (from Account → API Settings)
- **Type:** String
- **Required:** YES
- **Default:** None
- **Example:** `BYBIT_API_SECRET=XXXXXXXXXXXXXXXXXXXXXX`
- **⚠️ Important:** Never share this secret

---

### Trading Configuration

#### POSITION_SIZE_USDT
```env
POSITION_SIZE_USDT=100
```

- Amount of USDT to use per trade
- **Type:** Number (decimal)
- **Required:** NO
- **Default:** 100
- **Min:** 1 (may vary by symbol)
- **Max:** Your account balance
- **Examples:**
  - `50` = Trade $50 USDT
  - `100` = Trade $100 USDT
  - `500` = Trade $500 USDT
  - `1000` = Trade $1,000 USDT

**Notes:**
- Actual quantity bought is calculated from current price
- Example: At $1.25 price, $100 buys ~80 tokens
- Must have sufficient account balance
- Larger positions = higher PnL but more margin required

#### SYMBOL
```env
SYMBOL=RESOLVUSDT
```

- Trading pair / contract symbol
- **Type:** String
- **Required:** NO
- **Default:** RESOLVUSDT
- **Format:** `SYMBOLUSDT` (USDT perpetual futures)
- **Examples:**
  - `RESOLVUSDT` = RESOLVE futures
  - `BTCUSDT` = Bitcoin futures
  - `ETHUSDT` = Ethereum futures
  - `XRPUSDT` = XRP futures

**Notes:**
- Must be available on Bybit
- Must support linear (USDT) perpetual trading
- Check Bybit website for active trading pairs

#### FUNDING_TIME_HHmm
```env
FUNDING_TIME_HHmm=17:30
```

- Daily funding settlement time
- **Type:** Time string (HH:MM format)
- **Required:** NO
- **Default:** 17:30
- **Format:** 24-hour (00:00 to 23:59)
- **Examples:**
  - `17:30` = 5:30 PM UTC
  - `08:00` = 8:00 AM UTC
  - `00:00` = Midnight UTC

**⚠️ Critical Notes:**
- Bybit typically uses **17:30 UTC** for major pairs
- Some symbols may have different funding times
- Always verify correct time on Bybit website
- Times are in UTC (not your local time zone)

#### ENTRY_DELAY_MS
```env
ENTRY_DELAY_MS=100
```

- Milliseconds to wait after funding before entering
- **Type:** Integer
- **Required:** NO
- **Default:** 100
- **Min:** 1 (dangerous)
- **Max:** 1000 (too slow)
- **Examples:**
  - `50` = 50 milliseconds
  - `100` = 100 milliseconds (0.1 seconds)
  - `200` = 200 milliseconds (0.2 seconds)

**Notes:**
- Funding happens at HH:MM:00.000
- Entry happens at HH:MM:00.{ENTRY_DELAY_MS}
- Example: `17:30:00.000` → wait 100ms → `17:30:00.100`
- Smaller = more precise, but more risky
- Typical: 50-200ms

#### EXIT_DELAY_S
```env
EXIT_DELAY_S=2
```

- How many seconds to hold position before exiting
- **Type:** Integer
- **Required:** NO
- **Default:** 2
- **Min:** 1
- **Max:** 60 (or longer)
- **Examples:**
  - `1` = Hold for 1 second
  - `2` = Hold for 2 seconds
  - `5` = Hold for 5 seconds
  - `10` = Hold for 10 seconds

**Notes:**
- Entry at 17:30:00.100
- Exit at 17:30:00.100 + EXIT_DELAY_S
- Example: 2s → Exit at 17:30:02.100
- Shorter = faster PnL/loss
- Longer = more exposure to price movement

---

## 🔧 Code Configuration (main.py)

Advanced users can modify code constants for fine-tuning:

### Timing Tolerances

```python
TIMING_TOLERANCE_MS = 10  # Line ~32
```

- Maximum acceptable timing error before warning
- **Default:** 10ms (0.01 seconds)
- **Range:** 1-100ms
- Lower = stricter, Higher = more forgiving

### Retry Configuration

```python
MAX_RETRIES = 3  # Line ~35
RETRY_DELAY_MS = 100  # Line ~36
```

- **MAX_RETRIES:** How many times to retry failed orders
- **RETRY_DELAY_MS:** How long to wait between retries
- Default: 3 attempts, 100ms between attempts

### Order Timeout

```python
ORDER_TIMEOUT_S = 5  # Line ~37
```

- Maximum time to wait for order execution
- **Default:** 5 seconds
- Affects order confirmation timing

---

## 📊 Example Configurations

### Conservative (Small Position, Safe Timing)
```env
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
POSITION_SIZE_USDT=50
SYMBOL=RESOLVUSDT
FUNDING_TIME_HHmm=17:30
ENTRY_DELAY_MS=150
EXIT_DELAY_S=3
```

### Aggressive (Large Position, Fast Timing)
```env
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
POSITION_SIZE_USDT=500
SYMBOL=RESOLVUSDT
FUNDING_TIME_HHmm=17:30
ENTRY_DELAY_MS=50
EXIT_DELAY_S=1
```

### Standard (Recommended)
```env
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
POSITION_SIZE_USDT=100
SYMBOL=RESOLVUSDT
FUNDING_TIME_HHmm=17:30
ENTRY_DELAY_MS=100
EXIT_DELAY_S=2
```

### Different Symbol (BTCUSDT)
```env
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
POSITION_SIZE_USDT=200
SYMBOL=BTCUSDT
FUNDING_TIME_HHmm=17:30
ENTRY_DELAY_MS=100
EXIT_DELAY_S=2
```

---

## 🔐 Credentials Setup

### Getting Bybit Testnet Credentials

1. **Create Testnet Account**
   - Visit https://testnet.bybit.com
   - Sign up with email
   - Verify email

2. **Generate API Key**
   - Log in to testnet
   - Go to Account (top right)
   - Select API Manager
   - Click Create New Key
   - **(Optional but recommended)** Set permissions:
     - ✅ Trade
     - ❌ Transfer (disable)
     - ✅ Read (for monitoring)

3. **Copy Credentials**
   - Copy API Key (long string)
   - Copy Secret Key (long string)
   - Click "Save" to confirm

4. **Add to .env**
   ```env
   BYBIT_API_KEY=paste_your_key_here
   BYBIT_API_SECRET=paste_your_secret_here
   ```

### Security Best Practices

- ✅ Use **TESTNET** credentials first
- ✅ Keep `.env` file **private** (in .gitignore)
- ✅ Enable **IP Whitelist** on Bybit
- ✅ Use **unique** API keys per application
- ✅ Never commit `.env` to version control
- ❌ Don't share API key or secret
- ❌ Don't use in production without extensive testing

---

## ⚠️ Common Configuration Mistakes

### ❌ Mistake 1: Leaving Default Credentials
```env
BYBIT_API_KEY=your_testnet_api_key_here  # WRONG!
```
✅ **Fix:**
```env
BYBIT_API_KEY=abc123def456ghi789jkl  # Your actual key
```

### ❌ Mistake 2: Wrong Symbol Format
```env
SYMBOL=RESOLVE  # WRONG - missing USDT
```
✅ **Fix:**
```env
SYMBOL=RESOLVUSDT  # Correct format
```

### ❌ Mistake 3: Using Mainnet Credentials
```env
BYBIT_API_KEY=mainnet_key  # WRONG - uses real money!
```
✅ **Fix:**
```env
BYBIT_API_KEY=testnet_key  # Use testnet first, then mainnet
```

### ❌ Mistake 4: Wrong Time Format
```env
FUNDING_TIME_HHmm=5:30 PM  # WRONG - not 24-hour format
```
✅ **Fix:**
```env
FUNDING_TIME_HHmm=17:30  # Correct 24-hour format
```

### ❌ Mistake 5: Too Aggressive Timing
```env
ENTRY_DELAY_MS=5  # WRONG - too fast, network can't keep up
EXIT_DELAY_S=100  # WRONG - too long, price might crash
```
✅ **Fix:**
```env
ENTRY_DELAY_MS=100  # Realistic network delay
EXIT_DELAY_S=2      # Reasonable hold duration
```

---

## 📈 Performance Tuning

### For Testnet Success

1. **Verify Testnet Balance**
   - Ensure sufficient USDT in account
   - Check balance >= POSITION_SIZE_USDT

2. **Verify Symbol Trading**
   - Confirm RESOLVUSDT (or your symbol) is active
   - Check markets are open

3. **Optimal Timing**
   - Use default values: 100ms entry, 2s exit
   - Test multiple times to verify consistency

4. **Monitor Logs**
   - Check `trading_bot_*.log` file
   - Look for timing accuracy
   - Verify all orders executed

### For Production (Mainnet)

1. **Start Small**
   - Use $50-100 USDT first
   - Run for 3-5 cycles successfully
   - Gradually increase size

2. **Monitor Closely**
   - Watch every trade
   - Check PnL carefully
   - Verify timing accuracy

3. **Network Quality**
   - Ensure stable internet
   - Use dedicated server for bot (not laptop)
   - Monitor latency to exchange

---

## 🧪 Testing Configuration

### Before Running Live

1. **Test Credentials**
   ```bash
   python main.py
   # Should connect successfully and show "✓ Connected to Bybit TESTNET"
   ```

2. **Verify Symbol**
   - Bot will show current price
   - Verify price makes sense
   - Example: RESOLVUSDT around $1.20

3. **Check Quantity Calculation**
   - Bot shows calculated quantity
   - Verify: Position Size / Price ≈ Quantity
   - Example: $100 / $1.25 ≈ 80 tokens

4. **Monitor First Trade**
   - Watch entire execution
   - Check timing accuracy
   - Verify PnL calculation
   - Review log file

---

## 📞 Configuration Help

| Issue | Solution |
|-------|----------|
| "API not configured" | Add credentials to .env |
| Wrong price shown | Verify SYMBOL is correct and trading |
| Orders fail | Check account balance on testnet |
| Large timing errors | Close CPU-heavy apps, restart bot |
| Wrong symbol traded | Verify SYMBOL= in .env (check capitalization) |
| Too slow entry | Increase ENTRY_DELAY_MS |
| Too slow exit | Decrease EXIT_DELAY_S |

---

**Last Updated:** 2026-03-22  
**Version:** 1.0.0
