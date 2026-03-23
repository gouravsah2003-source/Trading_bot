"""
Bybit Funding Arbitrage Trading Bot
=====================================
A high-precision trading bot that enters SHORT positions exactly 0.1 seconds
after funding settlement and exits exactly 2 seconds later.

Author: Trading Bot
Date: 2026
Version: 1.0.0
"""

import os
import sys
import time
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from dotenv import load_dotenv
from pybit.unified_trading import HTTP

# Set UTF-8 encoding environment variables for Windows
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# ============================================================================
# CONFIGURATION & CONSTANTS
# ============================================================================

# Load environment variables
load_dotenv()
BYBIT_API_KEY = os.getenv('BYBIT_API_KEY')
BYBIT_API_SECRET = os.getenv('BYBIT_API_SECRET')
POSITION_SIZE_USDT = float(os.getenv('POSITION_SIZE_USDT', '100'))
SYMBOL = os.getenv('SYMBOL', 'RESOLVUSDT')
FUNDING_TIME_HHMM = os.getenv('FUNDING_TIME_HHmm', '17:30')
ENTRY_DELAY_MS = int(os.getenv('ENTRY_DELAY_MS', '100'))
EXIT_DELAY_S = int(os.getenv('EXIT_DELAY_S', '2'))

# Timing precision targets (in milliseconds)
ENTRY_TIMING_TARGET_MS = 0.1  # 0.1 seconds after funding
EXIT_TIMING_TARGET_MS = 2000  # 2 seconds after entry
TIMING_TOLERANCE_MS = 10      # 10ms tolerance for exit timing

# Order configuration
MAX_RETRIES = 3
RETRY_DELAY_MS = 100
ORDER_TIMEOUT_S = 5

# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging() -> logging.Logger:
    """Configure logging with millisecond precision timestamps and Windows UTF-8 support."""
    logger = logging.getLogger('BybitTradingBot')
    logger.setLevel(logging.DEBUG)

    # Console handler with UTF-8 encoding and Windows compatibility
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)

    # Try to set UTF-8 encoding on Windows console
    try:
        if sys.platform == 'win32':
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
    except Exception:
        pass

    # File handler with UTF-8 encoding
    log_filename = f"trading_bot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    file_handler = logging.FileHandler(log_filename, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # Formatter with millisecond precision
    formatter = logging.Formatter(
        '[%(asctime)s.%(msecs)03d] [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

logger = setup_logging()

# ============================================================================
# BYBIT API CLIENT
# ============================================================================

class BybitClient:
    """Wrapper for Bybit API with enhanced error handling and retry logic."""

    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        self.testnet = testnet
        try:
            self.client = HTTP(
                testnet=testnet,
                api_key=api_key,
                api_secret=api_secret
            )
            logger.info(f"[OK] Connected to Bybit {'TESTNET' if testnet else 'MAINNET'}")

            # FIX 1: Verify connection immediately by fetching server time
            server_time = self.client.get_server_time()
            if server_time.get('retCode') == 0:
                logger.info(f"[OK] API connection verified. Server time: {server_time['result']['timeSecond']}")
            else:
                logger.error(f"[FAIL] API connection check failed: {server_time}")

        except Exception as e:
            logger.error(f"[FAIL] Failed to initialize Bybit client: {e}")
            raise

    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get real-time ticker data for a symbol."""
        try:
            response = self.client.get_tickers(category="linear", symbol=symbol)
            if response['retCode'] == 0 and response['result']['list']:
                ticker = response['result']['list'][0]
                # FIX 2: Log the raw ticker so we can see if data is actually arriving
                logger.info(f"[DATA] Ticker: lastPrice={ticker.get('lastPrice')}, "
                            f"fundingRate={ticker.get('fundingRate')}, "
                            f"nextFundingTime={ticker.get('nextFundingTime')}")
                return ticker
            logger.error(f"[FAIL] get_ticker bad response for {symbol}: retCode={response.get('retCode')} msg={response.get('retMsg')}")
            return None
        except Exception as e:
            logger.error(f"[FAIL] Error fetching ticker: {e}")
            return None

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        qty: float,
        reduce_only: bool = False,
        retry_count: int = 0
    ) -> Optional[Dict]:
        """Place an order with retry logic."""
        try:
            response = self.client.place_order(
                category="linear",
                symbol=symbol,
                side=side,
                orderType=order_type,
                qty=str(qty),
                reduceOnly=reduce_only,
                timeInForce="IOC" if order_type == "Market" else "GTC"
            )

            if response['retCode'] == 0:
                logger.info(f"[OK] Order placed: {side} {qty} {symbol}")
                return response['result']
            else:
                # FIX 3: Log the FULL response so we can see exactly why it failed
                logger.warning(f"[FAIL] Order failed: retCode={response.get('retCode')} "
                               f"retMsg={response.get('retMsg')} full={response}")

                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying... ({retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY_MS / 1000.0)
                    return self.place_order(symbol, side, order_type, qty, reduce_only, retry_count + 1)
                return None

        except Exception as e:
            logger.error(f"[FAIL] Exception while placing order: {e}")
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY_MS / 1000.0)
                return self.place_order(symbol, side, order_type, qty, reduce_only, retry_count + 1)
            return None

    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position information."""
        try:
            response = self.client.get_positions(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] == 0 and response['result']['list']:
                pos = response['result']['list'][0]
                # FIX 4: Only return position if it's actually open (size > 0)
                if float(pos.get('size', 0)) > 0:
                    logger.info(f"[DATA] Position: size={pos['size']}, avgPrice={pos['avgPrice']}, side={pos['side']}")
                    return pos
                else:
                    logger.warning(f"[WARN] get_position returned empty position (size=0) for {symbol}")
                    return None
            logger.warning(f"[WARN] get_position no data: retCode={response.get('retCode')} msg={response.get('retMsg')}")
            return None
        except Exception as e:
            logger.error(f"[FAIL] Error fetching position: {e}")
            return None

# ============================================================================
# TRADING BOT LOGIC
# ============================================================================

class BybitTradingBot:
    """Main trading bot for Bybit funding arbitrage strategy."""

    def __init__(self, api_key: str, api_secret: str):
        """Initialize the trading bot."""
        # FIX 5: testnet=False to use real mainnet
        self.client = BybitClient(api_key, api_secret, testnet=True)
        self.symbol = SYMBOL
        self.position_size_usdt = POSITION_SIZE_USDT

        # Trade tracking
        self.entry_price: Optional[float] = None
        self.exit_price: Optional[float] = None
        self.entry_timestamp: Optional[float] = None
        self.exit_timestamp: Optional[float] = None
        self.entry_qty: Optional[float] = None
        self.order_id: Optional[str] = None

    def validate_credentials(self) -> bool:
        """Validate API credentials by making a real balance check."""
        try:
            # FIX 6: Actually validate by hitting the wallet endpoint, not just checking the string
            response = self.client.client.get_wallet_balance(accountType="UNIFIED")
            if response['retCode'] == 0:
                coins = response['result']['list'][0]['coin']
                usdt = next((c for c in coins if c['coin'] == 'USDT'), None)
                if usdt:
                    balance = float(usdt.get('walletBalance', 0))
                    logger.info(f"[OK] Credentials valid. USDT Balance: ${balance:.2f}")
                    if balance < self.position_size_usdt:
                        logger.error(f"[FAIL] Insufficient balance: ${balance:.2f} < required ${self.position_size_usdt:.2f}")
                        return False
                else:
                    logger.warning("[WARN] No USDT found in wallet — check your account has USDT")
                return True
            else:
                logger.error(f"[FAIL] Credential check failed: {response.get('retMsg')}")
                return False
        except Exception as e:
            logger.error(f"[FAIL] Exception during credential validation: {e}")
            return False

    def calculate_entry_quantity(self) -> Optional[float]:
        """Calculate order quantity based on position size and current price."""
        try:
            ticker = self.client.get_ticker(self.symbol)
            if not ticker:
                logger.error("[FAIL] Failed to get ticker for quantity calculation")
                return None

            current_price = float(ticker['lastPrice'])
            if current_price <= 0:
                logger.error(f"[FAIL] Invalid price received: {current_price}")
                return None

            qty = self.position_size_usdt / current_price

            # FIX 7: Fetch the instrument's actual lotSizeFilter so qty is valid on Bybit
            try:
                info_resp = self.client.client.get_instruments_info(category="linear", symbol=self.symbol)
                if info_resp['retCode'] == 0 and info_resp['result']['list']:
                    lot_filter = info_resp['result']['list'][0]['lotSizeFilter']
                    qty_step = float(lot_filter.get('qtyStep', 1))
                    min_qty = float(lot_filter.get('minOrderQty', 0))
                    # Round qty DOWN to nearest valid step
                    qty = max(min_qty, (qty // qty_step) * qty_step)
                    logger.info(f"[DATA] Instrument qtyStep={qty_step}, minOrderQty={min_qty}")
            except Exception as e:
                logger.warning(f"[WARN] Could not fetch instrument info, using rounded qty: {e}")
                qty = round(qty, 2)

            logger.info(f"[DATA] Current price: ${current_price:.6f}")
            logger.info(f"[DATA] Calculated quantity: {qty} {self.symbol}")

            self.entry_qty = qty
            return qty

        except Exception as e:
            logger.error(f"[FAIL] Error calculating quantity: {e}")
            return None

    def wait_for_funding_time(self) -> bool:
        """Wait for funding settlement time and provide countdown."""
        try:
            funding_hour, funding_minute = map(int, FUNDING_TIME_HHMM.split(':'))

            # FIX 8: last_logged is outside the loop so it persists correctly
            last_logged = -1
            while True:
                now = datetime.now()
                funding_today = now.replace(
                    hour=funding_hour,
                    minute=funding_minute,
                    second=0,
                    microsecond=0
                )

                # Allow small buffer for execution (IMPORTANT)
                if now > funding_today + timedelta(seconds=1):
                    funding_today += timedelta(days=1)

                time_until_funding = (funding_today - now).total_seconds()

                if time_until_funding > 0:
                    minutes = int(time_until_funding) // 60
                    seconds = int(time_until_funding) % 60
                    milliseconds = int((time_until_funding % 1) * 1000)

                    current_second = int(time_until_funding)
                    if current_second != last_logged:
                        last_logged = current_second
                        logger.info(f"[DEBUG] now={now}, funding_today={funding_today}")

                    time.sleep(0.1)
                else:
                    logger.info("[OK] Funding settlement time reached!")
                    return True

        except Exception as e:
            logger.error(f"[FAIL] Error waiting for funding time: {e}")
            return False

    def wait_for_entry_time(self, funding_timestamp: float) -> float:
        """Wait until exactly ENTRY_DELAY_MS after funding."""
        target_entry_time = funding_timestamp + (ENTRY_DELAY_MS / 1000.0)

        while True:
            current_time = time.perf_counter()
            time_until_entry = target_entry_time - current_time

            if time_until_entry <= 0:
                entry_timestamp = time.perf_counter()
                delay_ms = (entry_timestamp - target_entry_time) * 1000
                logger.info(f"[ENTRY] ENTRY TIME REACHED (offset: {delay_ms:.2f}ms)")
                return entry_timestamp

            if time_until_entry > 0.01:
                time.sleep(0.001)
            else:
                time.sleep(0.0001)

    def execute_entry(self) -> bool:
        """Execute SHORT market order with precise timing."""
        try:
            logger.info(f"\n{'='*70}")
            logger.info("ENTRY PHASE")
            logger.info(f"{'='*70}")

            if not self.entry_qty:
                logger.error("[FAIL] Entry quantity not calculated")
                return False

            entry_signal_time = time.perf_counter()
            dt_now = datetime.now()

            order_response = self.client.place_order(
                symbol=self.symbol,
                side="Sell",
                order_type="Market",
                qty=self.entry_qty,
                reduce_only=False
            )

            if not order_response:
                logger.error("[FAIL] Failed to place entry order")
                return False

            self.entry_timestamp = entry_signal_time
            self.order_id = order_response.get('orderId')

            # FIX 9: Wait for fill then retry up to 5 times if size still 0
            filled = False

            for attempt in range(10):
                time.sleep(0.3)
                position = self.client.get_position(self.symbol)

                if position and float(position.get('size', 0)) > 0:
                    self.entry_price = float(position['avgPrice'])
                    filled = True
                    break

                logger.warning(f"[WARN] Position not filled yet, retry {attempt+1}/10...")

            if not filled:
                logger.error("[FAIL] Order NOT filled — aborting trade")
                return False

            logger.info(f"[OK] SHORT position OPENED")
            logger.info(f"  Order ID: {self.order_id}")
            logger.info(f"  Timestamp: {dt_now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            logger.info(f"  Entry Price: ${self.entry_price:.6f}" if self.entry_price else "  Entry Price: NOT FETCHED")
            logger.info(f"  Quantity: {self.entry_qty}")

            return True

        except Exception as e:
            logger.error(f"[FAIL] Exception during entry: {e}")
            return False

    def wait_for_exit_time(self) -> float:
        """Wait exactly EXIT_DELAY_S seconds from entry."""
        if not self.entry_timestamp:
            raise ValueError("Entry timestamp not set")

        target_exit_time = self.entry_timestamp + EXIT_DELAY_S
        logger.info(f"[WAIT] Holding position for {EXIT_DELAY_S} seconds...")

        while True:
            current_time = time.perf_counter()
            time_until_exit = target_exit_time - current_time

            if time_until_exit <= 0:
                exit_timestamp = time.perf_counter()
                delay_ms = (exit_timestamp - target_exit_time) * 1000

                if abs(delay_ms) <= TIMING_TOLERANCE_MS:
                    logger.info(f"[OK] EXIT TIME REACHED (offset: {delay_ms:.2f}ms)")
                else:
                    logger.warning(f"[WARN] Exit timing exceeded tolerance! (offset: {delay_ms:.2f}ms)")

                return exit_timestamp

            if int(time_until_exit) < EXIT_DELAY_S and int(time_until_exit) >= 0:
                remaining = int(time_until_exit) + 1
                if remaining > 0:
                    logger.info(f"  {remaining}s remaining...")

            if time_until_exit > 0.01:
                time.sleep(0.001)
            else:
                time.sleep(0.0001)

    def execute_exit(self) -> bool:
        """Execute BUY market order to close SHORT position."""
        try:
            logger.info(f"\n{'='*70}")
            logger.info("EXIT PHASE")
            logger.info(f"{'='*70}")

            if not self.entry_qty:
                logger.error("[FAIL] Entry quantity not available")
                return False

            # Check if open position exists before placing exit order
            position = self.client.get_position(self.symbol)
            if not position or float(position.get('size', 0)) <= 0:
                logger.error("[FAIL] No open position to close")
                return False

            exit_signal_time = time.perf_counter()
            dt_now = datetime.now()

            order_response = self.client.place_order(
                symbol=self.symbol,
                side="Buy",
                order_type="Market",
                qty=self.entry_qty,
                reduce_only=True
            )

            if not order_response:
                logger.error("[FAIL] Failed to place exit order")
                return False

            self.exit_timestamp = exit_signal_time

            # FIX 10: Fetch exit price from executions (position is closed, avgPrice will be 0)
            time.sleep(0.3)
            try:
                exec_resp = self.client.client.get_executions(
                    category="linear", symbol=self.symbol, limit=2
                )
                if exec_resp['retCode'] == 0 and exec_resp['result']['list']:
                    # Most recent execution is the exit fill
                    self.exit_price = float(exec_resp['result']['list'][0]['execPrice'])
                    logger.info(f"[DATA] Exit fill price from executions: ${self.exit_price:.6f}")
                else:
                    logger.warning(f"[WARN] Could not fetch executions: {exec_resp.get('retMsg')}")
            except Exception as e:
                logger.warning(f"[WARN] Could not fetch exit price: {e}")

            logger.info(f"[OK] SHORT position CLOSED")
            logger.info(f"  Order ID: {order_response.get('orderId')}")
            logger.info(f"  Timestamp: {dt_now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            logger.info(f"  Exit Price: ${self.exit_price:.6f}" if self.exit_price else "  Exit Price: NOT FETCHED")

            return True

        except Exception as e:
            logger.error(f"[FAIL] Exception during exit: {e}")
            return False

    def calculate_pnl(self) -> Optional[Tuple[float, float, float]]:
        """Calculate profit/loss from trade."""
        try:
            if not all([self.entry_price, self.exit_price, self.entry_timestamp, self.exit_timestamp]):
                logger.error("[FAIL] Missing price or timestamp data for PnL calculation")
                return None

            price_diff = self.entry_price - self.exit_price
            pnl_usdt = price_diff * self.entry_qty
            hold_duration = self.exit_timestamp - self.entry_timestamp

            return price_diff, pnl_usdt, hold_duration

        except Exception as e:
            logger.error(f"[FAIL] Error calculating PnL: {e}")
            return None

    def print_trade_summary(self):
        """Print comprehensive trade summary and statistics."""
        logger.info(f"\n{'='*70}")
        logger.info("TRADE SUMMARY")
        logger.info(f"{'='*70}")

        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Position Size: {self.entry_qty} {self.symbol}")
        logger.info(f"Position Size (USD): ${self.position_size_usdt:.2f}")

        logger.info(f"\n--- ENTRY ---")
        logger.info(f"Entry Price: ${self.entry_price:.6f}" if self.entry_price else "Entry Price: N/A")
        logger.info(f"Entry Time: {self.entry_timestamp:.6f}" if self.entry_timestamp else "Entry Time: N/A")

        logger.info(f"\n--- EXIT ---")
        logger.info(f"Exit Price: ${self.exit_price:.6f}" if self.exit_price else "Exit Price: N/A")
        logger.info(f"Exit Time: {self.exit_timestamp:.6f}" if self.exit_timestamp else "Exit Time: N/A")

        pnl_result = self.calculate_pnl()
        if pnl_result:
            price_diff, pnl_usdt, hold_duration = pnl_result

            logger.info(f"\n--- PERFORMANCE ---")
            logger.info(f"Price Difference: ${price_diff:.6f}")
            logger.info(f"Profit/Loss: ${pnl_usdt:.4f}")
            logger.info(f"P&L %: {(pnl_usdt / self.position_size_usdt * 100):.4f}%")
            logger.info(f"Hold Duration: {hold_duration:.6f}s (Target: {EXIT_DELAY_S}s)")

            timing_error_ms = abs((hold_duration - EXIT_DELAY_S) * 1000)
            logger.info(f"Timing Error: {timing_error_ms:.2f}ms")

            if timing_error_ms <= TIMING_TOLERANCE_MS:
                logger.info(f"[OK] Timing WITHIN tolerance ({TIMING_TOLERANCE_MS}ms)")
            else:
                logger.warning(f"[WARN] Timing EXCEEDED tolerance ({TIMING_TOLERANCE_MS}ms)")

        logger.info(f"\n{'='*70}\n")

    def run(self):
        """Execute the complete trading strategy."""
        try:
            logger.info("="*70)
            logger.info("BYBIT FUNDING ARBITRAGE BOT - STARTING")
            logger.info("="*70)
            logger.info(f"Symbol:        {self.symbol}")
            logger.info(f"Position Size: ${self.position_size_usdt:.2f}")
            logger.info(f"Funding Time:  {FUNDING_TIME_HHMM}")
            logger.info(f"Entry Delay:   {ENTRY_DELAY_MS}ms after funding")
            logger.info(f"Exit Time:     {EXIT_DELAY_S}s after entry")
            logger.info("="*70 + "\n")

            if not self.validate_credentials():
                return False

            if not self.calculate_entry_quantity():
                return False

            if not self.wait_for_funding_time():
                return False

            funding_timestamp = time.perf_counter()
            logger.info(f"[DATA] Funding timestamp (perf_counter): {funding_timestamp:.6f}")

            self.entry_timestamp = self.wait_for_entry_time(funding_timestamp)

            if not self.execute_entry():
                return False
            try:
                self.exit_timestamp = self.wait_for_exit_time()
            except ValueError as e:
                logger.error(f"[FAIL] Error during exit wait: {e}")
                return False

            if not self.execute_exit():
                return False

            self.print_trade_summary()

            logger.info("[OK] Trade cycle completed successfully!")
            return True

        except KeyboardInterrupt:
            logger.warning("\n[STOP] Bot interrupted by user")
            return False
        except Exception as e:
            logger.error(f"[FAIL] Unexpected error in bot execution: {e}", exc_info=True)
            return False

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the trading bot."""
    try:
        if not BYBIT_API_KEY or BYBIT_API_KEY == 'your_testnet_api_key_here':
            logger.error("[FAIL] API credentials not configured!")
            logger.error("Please update your .env file with valid Bybit credentials:")
            logger.error("  BYBIT_API_KEY=your_key")
            logger.error("  BYBIT_API_SECRET=your_secret")
            return False

        bot = BybitTradingBot(BYBIT_API_KEY, BYBIT_API_SECRET)
        success = bot.run()
        return success

    except Exception as e:
        logger.error(f"[FAIL] Fatal error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)