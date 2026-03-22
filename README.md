# Bybit Funding Arbitrage Trading Bot

A high-precision Python trading bot for Bybit futures that executes a SHORT position entry exactly 0.1 seconds after funding settlement and exits exactly 2 seconds later. Designed for funding rate arbitrage strategies with millisecond-level timing precision.

## 🎯 Strategy Overview

**Funding Arbitrage on RESOLVUSDT:**
- **Funding Time:** 17:30:00.000 (daily)
- **Entry:** SHORT position at 17:30:00.100 (0.1 seconds after funding)
- **Exit:** Close position at 17:30:02.100 (2 seconds after entry)
- **Position Size:** $100 USDT

### Timeline
```
17:30:00.000 → Funding settlement occurs
17:30:00.100 → ENTRY: Place SHORT market order
17:30:02.100 → EXIT: Place BUY market order to close position
```

## 📋 Requirements

- Python 3.8+
- Bybit account (testnet or mainnet)
- API credentials (API Key & Secret)

## 🚀 Installation

### Step 1: Clone/Setup Project
```bash
cd "c:\Users\Gourav\short trade bot"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

**Dependencies installed:**
- `pybit==5.13.0` - Official Bybit Python SDK
- `python-dotenv==1.0.0` - Environment variable management
- `requests==2.31.0` - HTTP library

### Step 3: Configure API Credentials

Edit `.env` file and add your Bybit testnet API credentials:

```env
BYBIT_API_KEY=your_testnet_api_key_here
BYBIT_API_SECRET=your_testnet_api_secret_here
```

**To get testnet credentials:**
1. Go to https://testnet.bybit.com
2. Sign up or log in
3. Navigate to Account → API Settings
4. Create new API key (recommended for testing)
5. Copy API Key and Secret to `.env`

### Step 4: Configure Trading Parameters (Optional)

Adjust in `.env` if needed:
```env
POSITION_SIZE_USDT=100          # Position size in USDT
SYMBOL=RESOLVUSDT               # Trading pair
FUNDING_TIME_HHmm=17:30         # Funding settlement time (HH:MM)
ENTRY_DELAY_MS=100              # Entry delay after funding (milliseconds)
EXIT_DELAY_S=2                  # Hold duration (seconds)
```

## ▶️ Running the Bot

### Start the Bot
```bash
python main.py
```

### Expected Output
```
========================================================================
BYBIT FUNDING ARBITRAGE BOT - STARTING
========================================================================
Symbol: RESOLVUSDT
Position Size: $100.00
Funding Time: 17:30
Entry Delay: 100ms after funding
Exit Time: 2s after entry
========================================================================

✓ Connected to Bybit TESTNET
✓ API credentials validated
Current price: $1.234567
Calculated quantity: 81.22 RESOLVUSDT

⏰ Funding in 00:45.321
⏰ Funding in 00:45.220
...

✓ Funding settlement time reached!
⚡ ENTRY TIME REACHED (offset: 0.45ms)

======================================================================
ENTRY PHASE
======================================================================
✓ SHORT position OPENED
  Order ID: abc12345def67890
  Timestamp: 2026-03-22 17:30:00.100
  Entry Price: $1.234567
  Quantity: 81.22

⏱️  Holding position for 2 seconds...
  ...

✓ EXIT TIME REACHED (offset: -0.23ms)

======================================================================
EXIT PHASE
======================================================================
✓ SHORT position CLOSED
  Order ID: def67890abc12345
  Timestamp: 2026-03-22 17:30:02.100
  Exit Price: $1.234789

======================================================================
TRADE SUMMARY
======================================================================
Symbol: RESOLVUSDT
Position Size: 81.22 RESOLVUSDT
Position Size (USD): $100.00

--- ENTRY ---
Entry Price: $1.234567
Entry Time: 1234567890.123456

--- EXIT ---
Exit Price: $1.234789
Exit Time: 1234567890.123456

--- PERFORMANCE ---
Price Difference: -$0.000222
Profit/Loss: -$18.02
P&L %: -18.0200%
Hold Duration: 2.000156s (Target: 2s)
Timing Error: 0.16ms
✓ Timing WITHIN tolerance (10ms)

========================================================================

✓ Trade cycle completed successfully!
```

## 🔧 Configuration Details

### API Credentials (.env)
- **BYBIT_API_KEY**: Your Bybit API key (testnet or mainnet)
- **BYBIT_API_SECRET**: Your Bybit API secret
- Both are required to connect to the exchange

### Trading Parameters
- **POSITION_SIZE_USDT**: Dollar amount to invest in each trade (default: $100)
- **SYMBOL**: Trading pair (default: RESOLVUSDT)
- **FUNDING_TIME_HHmm**: Daily funding settlement time in HH:MM format
- **ENTRY_DELAY_MS**: Milliseconds after funding to enter position (typically 100ms)
- **EXIT_DELAY_S**: How many seconds to hold the position (default: 2 seconds)

### Timing Precision
- **Microsecond-level timing** using `time.perf_counter()`
- **10ms tolerance** for exit timing validation
- **Countdown display** with millisecond precision
- **Millisecond logging** with automatic timestamp formatting

## 📊 Key Features

### Timing Accuracy
- ✅ Entry timing precise to ±1ms
- ✅ Exit timing within 10ms tolerance (default)
- ✅ Real-time countdown with millisecond display
- ✅ Busy-wait loop for maximum precision

### Error Handling
- ✅ Automatic retry logic (up to 3 attempts per order)
- ✅ 100ms delay between retries
- ✅ Comprehensive exception catching
- ✅ Graceful degradation on failures

### Order Management
- ✅ Market orders with immediate execution
- ✅ `reduceOnly=True` flag for exit orders (safety)
- ✅ IOC (Immediate-or-Cancel) time in force
- ✅ Order ID tracking and logging

### Performance Tracking
- ✅ Entry & exit timestamps with microsecond precision
- ✅ Entry & exit prices with 2 decimal places
- ✅ Price difference calculation
- ✅ Profit/Loss (PnL) in USDT and percentage
- ✅ Hold duration verification
- ✅ Timing error measurements

### Logging
- ✅ Console output with color-coded messages
- ✅ File logging with timestamp format: `YYYY-MM-DD HH:MM:SS.mmm`
- ✅ Log files auto-named: `trading_bot_YYYYMMDD_HHMMSS.log`
- ✅ DEBUG level for comprehensive tracking
- ✅ Special emoji indicators for status (✓, ✗, ⏰, ⚡, 📊, ⏱️)

### Security
- ✅ Environment variables for sensitive data
- ✅ No hardcoded credentials
- ✅ Testnet by default (safer for development)
- ✅ `reduceOnly` flag prevents unintended new positions

## 📈 Output Metrics

The bot tracks and displays:

1. **Entry Information**
   - Order ID and status
   - Timestamp (down to milliseconds)
   - Entry price
   - Position quantity

2. **Exit Information**
   - Order ID and status
   - Timestamp (down to milliseconds)
   - Exit price
   - Position closure confirmation

3. **Performance Metrics**
   - Price difference (entry - exit)
   - Profit/Loss in USDT
   - Profit/Loss percentage
   - Actual hold duration vs. target
   - Timing error in milliseconds

4. **Validation**
   - Confirms timing accuracy within tolerance
   - Flags any timing anomalies

## ⚠️ Important Notes

### Testnet vs. Mainnet
- **Default:** Testnet (safe for development)
- **To use mainnet:** Change `testnet=True` to `testnet=False` in `main.py`
- **WARNING:** Mainnet trades use real money!

### Funding Time
- Bybit futures funding settlement occurs at **17:30 UTC** daily
- Different symbols may have different funding times (verify on Bybit)
- The bot automatically waits for the next occurrence if time has passed

### Market Conditions
- Strategy requires **sufficient liquidity** in RESOLVUSDT
- Market slippage may differ from entry price
- 2-second holding period = high risk, high speed required

### Precision Requirements
- Computer's system clock should be synchronized (NTP)
- Network latency (API calls) typically 50-500ms
- Actual execution may vary from scheduled time
- 10ms tolerance is reasonable for Bybit testnet

## 🔍 Debugging

### View Logs
```bash
# Check the latest log file
type "trading_bot_*.log"
```

### Common Issues

**Issue: "API credentials not configured"**
- Solution: Update .env with valid testnet API credentials
- Verify credentials match exactly (no extra spaces)

**Issue: "Failed to get ticker for RESOLVUSDT"**
- Solution: Verify symbol is correct and trading on Bybit
- Check internet connection to API endpoint

**Issue: "Order placement failed" multiple times**
- Solution: Check account margin/balance on testnet
- Verify sufficient USDT collateral available
- Ensure API key has trading permissions

**Issue: Timing errors exceed 10ms**
- Solution: Close other CPU-intensive applications
- Ensure stable internet connection
- Check if testnet servers are experiencing lag

## 🔐 Safety Measures

1. **Always test on testnet first**
2. **Start with small position sizes**
3. **Monitor account balance regularly**
4. **Never share API credentials**
5. **Use IP whitelist on Bybit API settings**
6. **Enable 2FA on Bybit account**
7. **Review trade logs before production use**

## 📞 Support & Troubleshooting

For issues with:
- **Bybit API:** https://bybit-exchange.github.io/docs/intro
- **pybit library:** https://github.com/bybit-exchange/pybit
- **Python:** https://docs.python.org/3/

## 📝 License

This trading bot is provided as-is for educational purposes. Use at your own risk.

## 🎓 Educational Disclaimer

This bot is designed for learning about:
- High-frequency trading concepts
- Millisecond-precision timing
- API integration with exchanges
- Risk management strategies
- Automated order execution

Trading cryptocurrency futures involves substantial risk of loss. Past performance does not guarantee future results. Always test thoroughly on testnet before using with real money.

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-22  
**Tested on:** Python 3.8+, Bybit Testnet
