# Usage Examples & Scenarios

Real-world examples and common usage scenarios for the Bybit trading bot.

## 🎯 Basic Usage Scenario

### Scenario: First Time Setup & Trade

You just received this bot and want to try it on Bybit testnet.

**Time Required:** ~30 minutes

### Step 1: Get Testnet Credentials (5 min)
```
1. Go to https://testnet.bybit.com
2. Sign up with your email
3. Go to Account → API Manager
4. Create New Key
5. Copy the API Key and Secret
```

### Step 2: Configure Bot (2 min)
```bash
# Edit .env file with your editor
# Add your credentials:

BYBIT_API_KEY=abc123def456ghi789
BYBIT_API_SECRET=xyz789abc456def123
```

### Step 3: Add Account Balance (0 min)
- Bybit testnet gives you $10,000 USDT automatically
- No real money needed!

### Step 4: Install Dependencies (5 min)
```bash
pip install -r requirements.txt
```

### Step 5: First Run (20 min)
```bash
python main.py
```

**What Happens:**
```
✓ Connected to Bybit TESTNET
Current price: $1.2345
Calculated quantity: 81.22 RESOLVUSDT
⏰ Funding in 00:45.321
... waiting ...
✓ Funding settlement time reached!
⚡ ENTRY TIME REACHED (offset: 0.45ms)
✓ SHORT position OPENED
⏱️  Holding position for 2 seconds...
✓ EXIT TIME REACHED (offset: -0.23ms)
✓ SHORT position CLOSED

Profit/Loss: +$0.50
✓ Trade cycle completed successfully!
```

---

## 📊 Example Configurations

### Example 1: Conservative Strategy

**Setup:** Small position, careful timing

```env
# .env file
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
POSITION_SIZE_USDT=50          # Only $50 per trade
SYMBOL=RESOLVUSDT
FUNDING_TIME_HHmm=17:30
ENTRY_DELAY_MS=150             # More cautious entry
EXIT_DELAY_S=3                 # Longer hold = less risky
```

**When to use:**
- Learning the bot
- Small account
- Testing new strategies
- Being careful with money

**Expected Results:**
- Smaller PnL (±$0.10-$0.50)
- Safer execution
- Slower timing might miss some moves

---

### Example 2: Aggressive Strategy

**Setup:** Large position, fast timing

```env
# .env file
BYBIT_API_KEY=your_key
BYBIT_API_SECRET=your_secret
POSITION_SIZE_USDT=500         # $500 per trade
SYMBOL=RESOLVUSDT
FUNDING_TIME_HHmm=17:30
ENTRY_DELAY_MS=50              # Fast entry
EXIT_DELAY_S=1                 # Quick exit for quick PnL
```

**When to use:**
- Experienced trader
- Large account
- Capturing quick moves
- High risk tolerance

**Expected Results:**
- Larger PnL (±$1-$5)
- More volatile
- Requires excellent network

---

### Example 3: Multi-Pair Strategy (Sequential)

**Idea:** Trade different pairs at different times

```bash
# File: trade_multiple.sh (or .bat on Windows)

# First pair at 17:30
python main.py

# Second pair at 20:00
# (Edit .env and change SYMBOL to BTCUSDT)
# python main.py

# Third pair at 20:30
# (Edit .env and change SYMBOL to ETHUSDT)
# python main.py
```

**Configuration alternation:**
```env
# Trade 1: RESOLVUSDT at 17:30
SYMBOL=RESOLVUSDT
FUNDING_TIME_HHmm=17:30

# Trade 2: BTCUSDT at 20:00 (need different .env or edit before run)
SYMBOL=BTCUSDT
FUNDING_TIME_HHmm=20:00
```

---

## 🎮 Interactive Usage Examples

### Example 1: Manual Testing Before 17:30

**Goal:** Test bot without waiting for real funding time

**Steps:**
```bash
# Edit .env to test in 5 minutes
FUNDING_TIME_HHmm=14:30        # Set to 5 min from now (at 14:25)
POSITION_SIZE_USDT=50          # Use smaller position for testing
```

**Run:**
```bash
python main.py
```

**Result:**
- Bot runs immediately (no waiting)
- Quick test of order execution
- Verify timing accuracy
- Check logs

---

### Example 2: Testing Different Position Sizes

**Goal:** Find optimal position size for your account

**Test Progression:**
```bash
# Test 1: Micro position
POSITION_SIZE_USDT=10
# python main.py → Check if it works

# Test 2: Small position
POSITION_SIZE_USDT=50
# python main.py → Works? Try larger

# Test 3: Medium position
POSITION_SIZE_USDT=100
# python main.py → Good? Move to production

# Test 4: Large position (production)
POSITION_SIZE_USDT=500
# python main.py → Live trading
```

**Monitor Each:**
- Order fills at expected price
- PnL calculation is accurate
- Timing is consistent

---

### Example 3: Testing Different Symbols

**Goal:** Find best symbol for arbitrage

**Available Pairs:**
- RESOLVUSDT (recommended)
- BTCUSDT (high volume, tight spread)
- ETHUSDT (popular, liquid)
- XRPUSDT (moderate volatility)

**Test Each:**
```bash
# Test 1: RESOLVUSDT (current)
SYMBOL=RESOLVUSDT
# python main.py

# Test 2: BTCUSDT
SYMBOL=BTCUSDT
# python main.py → Compare PnL and timing

# Test 3: ETHUSDT
SYMBOL=ETHUSDT
# python main.py → Which performs best?
```

**Compare Results:**
- Timing accuracy
- Spread (entry-exit price)
- Slippage
- PnL consistency

---

## 📈 Daily Trading Schedule

### 24/7 Automated Trading

**Bybit Funding Times (UTC):**
- 17:30 - RESOLVUSDT
- 20:00 - BTCUSDT (typically)
- 20:30 - ETHUSDT (typically)

**Setup for continuous trading:**

**Option A: Manual Approach**
```bash
# 17:29 - Terminal 1
python main.py              # RESOLVUSDT at 17:30

# 19:59 - Terminal 2 (different .env)
python main.py              # BTCUSDT at 20:00
```

**Option B: Scheduling with Windows Task Scheduler**
```
Create task for: python main.py
Trigger: Every day at 17:25
(Bot waits until 17:30)
```

---

## 🔧 Troubleshooting Scenarios

### Scenario 1: "Order Failed to Place"

**Situation:**
Bot shows: ✗ Order placement failed

**Diagnosis:**
```bash
# Check account balance
# Bybit testnet → Account → Assets
# Verify USDT balance > POSITION_SIZE_USDT + margin

# Check symbol is trading
# Verify SYMBOL=RESOLVUSDT is correct
# Check Bybit Markets → Linear → RESOLVUSDT
```

**Fix:**
```env
# If balance low, reduce position size
POSITION_SIZE_USDT=50

# Or request testnet deposit
# (Bybit testnet resets daily)
```

---

### Scenario 2: "Timing Error Exceeds 50ms"

**Situation:**
```
Hold Duration: 2.087654s
Timing Error: 87.65ms
✗ Timing EXCEEDED tolerance
```

**Diagnosis:**
- Slow internet connection
- High CPU usage
- API server lag
- Network congestion

**Fixes:**
```bash
# Option 1: Close unnecessary applications
tasklist
taskkill /IM chrome.exe /F  # Close browser

# Option 2: Try different network
# Switch WiFi to Ethernet

# Option 3: Try again later
# (Server load varies)

# Option 4: Extend tolerance in code
# TIMING_TOLERANCE_MS = 20  # More forgiving
```

---

### Scenario 3: "Price Difference Looks Wrong"

**Situation:**
```
Entry Price: $1.2345
Exit Price: $1.2340
Price Diff: $0.0005  # Why so small?

Profit: $0.04
```

**Explanation:**
- Very short 2-second hold means small price moves
- $0.0005 x 81.22 = $0.04 profit
- This is NORMAL and EXPECTED!

**Verify:**
- Entry/Exit price difference: $0.0001 - $0.001 typical
- 2-second PnL: $0.01 - $0.50 typical
- PnL %: 0.1% - 0.5% typical

---

## 💡 Advanced Scenarios

### Scenario 1: Paper Trading Long-Term

**Goal:** Run bot for a week on testnet to collect data

**Setup:**
```bash
# Run every day at 17:30
# Monitor results in log files
```

**Collect Metrics:**
```
Day 1: PnL +$0.23, Timing +0.5ms, ✓
Day 2: PnL -$0.11, Timing -1.2ms, ✓
Day 3: PnL +$0.45, Timing +2.1ms, ✓
...
Week 1 Average: +$0.12/day, Accuracy: 99.8%
```

**Use Results:**
- Understand realistic PnL
- Measure consistency
- Decide if profitable for mainnet

---

### Scenario 2: A/B Testing Strategies

**Goal:** Compare two different configurations

```bash
# Configuration A (1 week)
ENTRY_DELAY_MS=100
EXIT_DELAY_S=2
# Run 7 trades, collect data

# Configuration B (1 week)
ENTRY_DELAY_MS=50
EXIT_DELAY_S=1
# Run 7 trades, collect data

# Compare results
# Which has better average PnL?
# Which has better timing accuracy?
```

---

### Scenario 3: Volume & Liquidity Testing

**Goal:** Find maximum position size the bot can handle

**Test progression:**
```
Size 1: $100   → ✓ Fills instantly
Size 2: $500   → ✓ Fills instantly
Size 3: $1000  → ✓ Fills instantly
Size 4: $5000  → ✗ Partial fill (not enough liquidity)
```

**Conclusion:** Max safe position ≈ $1000

**Action:** Cap position to $1000 for production

---

## 📊 Performance Monitoring

### Track These Metrics

**Daily Report Template:**
```
Date: 2026-03-22
Symbol: RESOLVUSDT
Position Size: $100

Trade 1:
- Entry: 17:30:00.145 (offset: +0.45ms)
- Exit: 17:30:02.098 (offset: -2.10ms)
- Entry Price: $1.2345
- Exit Price: $1.2340
- PnL: +$0.04
- Timing Error: 2.10ms ✓

Weekly Summary:
- Trades: 7
- Wins: 5
- Losses: 2
- Total PnL: +$0.28
- Avg Timing Error: 1.23ms
- Best Trade: +$0.50
- Worst Trade: -$0.15
```

---

## 🚀 Moving to Mainnet

### Pre-Mainnet Checklist

```
✓ Passed 10+ trades on testnet
✓ Timing consistently ±5ms
✓ Understanding PnL patterns
✓ No unhandled errors
✓ Logging all trades
✓ Mainnet API key generated
✓ Small mainnet account funded ($200 USDT)
✓ Reviewed all documentation
```

### Mainnet First Trade

```env
# Update .env with mainnet key
BYBIT_API_KEY=mainnet_key
BYBIT_API_SECRET=mainnet_secret

# Start with tiny position
POSITION_SIZE_USDT=25

# Watch very carefully
# Check account balance before/after
# Review timing and PnL
```

**After First Mainnet Trade:**
- Review log carefully
- Verify PnL calculation
- Check actual account balance
- Confirm no unexpected fees

---

## 📞 Quick Reference

### Common Commands

```bash
# Run bot
python main.py

# View latest log
type *.log | more

# Check dependencies
pip list | findstr pybit

# View config
type .env

# List log files
dir *.log
```

### Quick Edits

```bash
# Reduce position size
# Edit .env: POSITION_SIZE_USDT=50

# Change funding time
# Edit .env: FUNDING_TIME_HHmm=20:00

# Different symbol
# Edit .env: SYMBOL=BTCUSDT
```

---

**Version:** 1.0.0  
**Last Updated:** 2026-03-22
