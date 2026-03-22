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
TIMING_TOLERANCE_MS = 10  # 10ms tolerance for exit timing

# API Configuration
BYBIT_TESTNET_URL = "https://api-testnet.bybit.com"
BYBIT_MAINNET_URL = "https://api.bybit.com"

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
            # Force UTF-8 encoding on Windows
            import io
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG)
    except Exception:
        pass  # Fall back to default encoding if UTF-8 setup fails
    
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
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize Bybit client.
        
        Args:
            api_key: Bybit API key
            api_secret: Bybit API secret
            testnet: Use testnet (True) or mainnet (False)
        """
        self.testnet = testnet
        url = BYBIT_TESTNET_URL if testnet else BYBIT_MAINNET_URL
        
        try:
            self.client = HTTP(
                testnet=testnet,
                api_key=api_key,
                api_secret=api_secret
            )
            logger.info(f"[OK] Connected to Bybit {'TESTNET' if testnet else 'MAINNET'}")
        except Exception as e:
            logger.error(f"[FAIL] Failed to initialize Bybit client: {e}")
            raise
    
    def get_ticker(self, symbol: str) -> Optional[Dict]:
        """Get real-time ticker data for a symbol."""
        try:
            response = self.client.get_tickers(category="linear", symbol=symbol)
            if response['retCode'] == 0 and response['result']['list']:
                return response['result']['list'][0]
            logger.error(f"Failed to get ticker for {symbol}: {response}")
            return None
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
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
        """
        Place an order with retry logic.
        
        Args:
            symbol: Trading pair (e.g., 'RESOLVUSDT')
            side: 'Buy' or 'Sell'
            order_type: 'Market' or 'Limit'
            qty: Order quantity
            reduce_only: Close position only (no new position)
            retry_count: Current retry attempt
        
        Returns:
            Order response or None if failed
        """
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
                error_msg = response.get('retMsg', 'Unknown error')
                logger.warning(f"Order placement failed: {error_msg}")
                
                # Retry logic
                if retry_count < MAX_RETRIES:
                    logger.info(f"Retrying... ({retry_count + 1}/{MAX_RETRIES})")
                    time.sleep(RETRY_DELAY_MS / 1000.0)
                    return self.place_order(
                        symbol, side, order_type, qty, reduce_only, retry_count + 1
                    )
                return None
                
        except Exception as e:
            logger.error(f"Exception while placing order: {e}")
            if retry_count < MAX_RETRIES:
                time.sleep(RETRY_DELAY_MS / 1000.0)
                return self.place_order(
                    symbol, side, order_type, qty, reduce_only, retry_count + 1
                )
            return None
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """Get current position information."""
        try:
            response = self.client.get_positions(
                category="linear",
                symbol=symbol
            )
            if response['retCode'] == 0 and response['result']['list']:
                return response['result']['list'][0]
            return None
        except Exception as e:
            logger.error(f"Error fetching position: {e}")
            return None

# ============================================================================
# TRADING BOT LOGIC
# ============================================================================

class BybitTradingBot:
    """Main trading bot for Bybit funding arbitrage strategy."""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize the trading bot."""
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
        """Validate API credentials are properly configured."""
        if not BYBIT_API_KEY or BYBIT_API_KEY == 'your_testnet_api_key_here':
            logger.error("[FAIL] API credentials not configured. Please update .env file.")
            return False
        logger.info("[OK] API credentials validated")
        return True
    
    def calculate_entry_quantity(self) -> Optional[float]:
        """Calculate order quantity based on position size and current price."""
        try:
            ticker = self.client.get_ticker(self.symbol)
            if not ticker:
                logger.error("Failed to get ticker for quantity calculation")
                return None
            
            current_price = float(ticker['lastPrice'])
            qty = self.position_size_usdt / current_price
            
            # Round to reasonable precision (based on Bybit specs)
            qty = round(qty, 2)
            
            logger.info(f"Current price: ${current_price:.2f}")
            logger.info(f"Calculated quantity: {qty} {self.symbol}")
            
            self.entry_qty = qty
            return qty
            
        except Exception as e:
            logger.error(f"Error calculating quantity: {e}")
            return None
    
    def wait_for_funding_time(self) -> bool:
        """
        Wait for funding settlement time and provide countdown.
        
        Returns:
            True if funding time reached, False if error
        """
        try:
            # Parse funding time (HH:MM format)
            funding_hour, funding_minute = map(int, FUNDING_TIME_HHMM.split(':'))
            
            while True:
                now = datetime.now()
                funding_today = now.replace(
                    hour=funding_hour,
                    minute=funding_minute,
                    second=0,
                    microsecond=0
                )
                
                # If funding time already passed today, wait for tomorrow
                if now > funding_today:
                    funding_today += timedelta(days=1)
                
                # Calculate time until funding
                time_until_funding = (funding_today - now).total_seconds()
                
                if time_until_funding > 0:
                    # Show countdown every second
                    minutes = int(time_until_funding) // 60
                    seconds = int(time_until_funding) % 60
                    milliseconds = int((time_until_funding % 1) * 1000)
                    
                    if int(time_until_funding) != int(time_until_funding - 1):
                        logger.info(
                            f"[TIME] Funding in {minutes:02d}:{seconds:02d}.{milliseconds:03d}"
                        )
                    
                    time.sleep(0.1)  # Check every 100ms
                else:
                    logger.info("[OK] Funding settlement time reached!")
                    return True
                    
        except Exception as e:
            logger.error(f"Error waiting for funding time: {e}")
            return False
    
    def wait_for_entry_time(self, funding_timestamp: float) -> float:
        """
        Wait until exactly 0.1 seconds after funding.
        
        Args:
            funding_timestamp: Timestamp when funding occurred (perf_counter)
        
        Returns:
            Entry timestamp
        """
        target_entry_time = funding_timestamp + (ENTRY_DELAY_MS / 1000.0)
        
        # Busy wait for precision (within last 10ms)
        while True:
            current_time = time.perf_counter()
            time_until_entry = target_entry_time - current_time
            
            if time_until_entry <= 0:
                entry_timestamp = time.perf_counter()
                delay_ms = (entry_timestamp - target_entry_time) * 1000
                logger.info(f"[ENTRY] ENTRY TIME REACHED (offset: {delay_ms:.2f}ms)")
                return entry_timestamp
            
            # Sleep for shorter duration to maintain precision
            if time_until_entry > 0.01:
                time.sleep(0.001)  # Sleep 1ms if more than 10ms away
            else:
                time.sleep(0.0001)  # Sleep 0.1ms if within 10ms
    
    def execute_entry(self) -> bool:
        """Execute SHORT market order with precise timing."""
        try:
            logger.info(f"\n{'='*70}")
            logger.info("ENTRY PHASE")
            logger.info(f"{'='*70}")
            
            if not self.entry_qty:
                logger.error("Entry quantity not calculated")
                return False
            
            # Record entry signal time
            entry_signal_time = time.perf_counter()
            dt_now = datetime.now()
            
            # Place SHORT order
            order_response = self.client.place_order(
                symbol=self.symbol,
                side="Sell",  # Sell = SHORT
                order_type="Market",
                qty=self.entry_qty,
                reduce_only=False
            )
            
            if not order_response:
                logger.error("[FAIL] Failed to place entry order")
                return False
            
            # Record timing
            self.entry_timestamp = entry_signal_time
            self.order_id = order_response.get('orderId')
            
            # Get filled price
            position = self.client.get_position(self.symbol)
            if position and position['avgPrice']:
                self.entry_price = float(position['avgPrice'])
            
            # Display entry details
            logger.info(f"[OK] SHORT position OPENED")
            logger.info(f"  Order ID: {self.order_id}")
            logger.info(f"  Timestamp: {dt_now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            logger.info(f"  Entry Price: ${self.entry_price:.2f}" if self.entry_price else "")
            logger.info(f"  Quantity: {self.entry_qty}")
            
            return True
            
        except Exception as e:
            logger.error(f"Exception during entry: {e}")
            return False
    
    def wait_for_exit_time(self) -> float:
        """
        Wait exactly 2 seconds from entry, then return exit timestamp.
        
        Returns:
            Exit timestamp
        """
        if not self.entry_timestamp:
            raise ValueError("Entry timestamp not set")
        
        target_exit_time = self.entry_timestamp + EXIT_DELAY_S
        
        logger.info(f"[WAIT] Holding position for {EXIT_DELAY_S} seconds...")
        
        # Busy wait for precision
        while True:
            current_time = time.perf_counter()
            time_until_exit = target_exit_time - current_time
            
            if time_until_exit <= 0:
                exit_timestamp = time.perf_counter()
                delay_ms = (exit_timestamp - target_exit_time) * 1000
                
                # Check if within tolerance
                if abs(delay_ms) <= TIMING_TOLERANCE_MS:
                    logger.info(f"[OK] EXIT TIME REACHED (offset: {delay_ms:.2f}ms)")
                else:
                    logger.warning(
                        f"[WARN] Exit timing exceeded tolerance! (offset: {delay_ms:.2f}ms)"
                    )
                
                return exit_timestamp
            
            # Display progress at 1-second intervals
            if int(time_until_exit) < EXIT_DELAY_S and int(time_until_exit) >= 0:
                remaining = int(time_until_exit) + 1
                if remaining > 0:
                    logger.info(f"  {remaining}s remaining...")
            
            # Precise sleep
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
                logger.error("Entry quantity not available")
                return False
            
            # Record exit signal time
            exit_signal_time = time.perf_counter()
            dt_now = datetime.now()
            
            # Place BUY order to close SHORT
            order_response = self.client.place_order(
                symbol=self.symbol,
                side="Buy",  # Buy = CLOSE SHORT
                order_type="Market",
                qty=self.entry_qty,
                reduce_only=True  # Only reduce existing position
            )
            
            if not order_response:
                logger.error("[FAIL] Failed to place exit order")
                return False
            
            # Record timing
            self.exit_timestamp = exit_signal_time
            
            # Get filled price
            position = self.client.get_position(self.symbol)
            if position and position['avgPrice']:
                self.exit_price = float(position['avgPrice'])
            
            # Display exit details
            logger.info(f"[OK] SHORT position CLOSED")
            logger.info(f"  Order ID: {order_response.get('orderId')}")
            logger.info(f"  Timestamp: {dt_now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]}")
            logger.info(f"  Exit Price: ${self.exit_price:.2f}" if self.exit_price else "")
            
            return True
            
        except Exception as e:
            logger.error(f"Exception during exit: {e}")
            return False
    
    def calculate_pnl(self) -> Optional[Tuple[float, float, float]]:
        """
        Calculate profit/loss from trade.
        
        Returns:
            Tuple of (price_diff, pnl_usdt, hold_duration_s) or None if error
        """
        try:
            if not all([self.entry_price, self.exit_price, self.entry_timestamp, 
                       self.exit_timestamp]):
                logger.error("Missing price or timestamp data for PnL calculation")
                return None
            
            # For SHORT position: profit = entry_price - exit_price
            price_diff = self.entry_price - self.exit_price
            pnl_usdt = price_diff * self.entry_qty
            hold_duration = self.exit_timestamp - self.entry_timestamp
            
            return price_diff, pnl_usdt, hold_duration
            
        except Exception as e:
            logger.error(f"Error calculating PnL: {e}")
            return None
    
    def print_trade_summary(self):
        """Print comprehensive trade summary and statistics."""
        logger.info(f"\n{'='*70}")
        logger.info("TRADE SUMMARY")
        logger.info(f"{'='*70}")
        
        # Basic trade info
        logger.info(f"Symbol: {self.symbol}")
        logger.info(f"Position Size: {self.entry_qty} {self.symbol}")
        logger.info(f"Position Size (USD): ${self.position_size_usdt:.2f}")
        
        # Entry details
        logger.info(f"\n--- ENTRY ---")
        logger.info(f"Entry Price: ${self.entry_price:.2f}" if self.entry_price else "N/A")
        logger.info(f"Entry Time: {self.entry_timestamp:.6f}" if self.entry_timestamp else "N/A")
        
        # Exit details
        logger.info(f"\n--- EXIT ---")
        logger.info(f"Exit Price: ${self.exit_price:.2f}" if self.exit_price else "N/A")
        logger.info(f"Exit Time: {self.exit_timestamp:.6f}" if self.exit_timestamp else "N/A")
        
        # PnL calculation
        pnl_result = self.calculate_pnl()
        if pnl_result:
            price_diff, pnl_usdt, hold_duration = pnl_result
            
            logger.info(f"\n--- PERFORMANCE ---")
            logger.info(f"Price Difference: ${price_diff:.2f}")
            logger.info(f"Profit/Loss: ${pnl_usdt:.2f}")
            logger.info(f"P&L %: {(pnl_usdt / self.position_size_usdt * 100):.4f}%")
            logger.info(f"Hold Duration: {hold_duration:.6f}s (Target: {EXIT_DELAY_S}s)")
            
            # Timing accuracy
            timing_error_ms = abs((hold_duration - EXIT_DELAY_S) * 1000)
            logger.info(f"Timing Error: {timing_error_ms:.2f}ms")
            
            if timing_error_ms <= TIMING_TOLERANCE_MS:
                logger.info(f"[OK] Timing WITHIN tolerance ({TIMING_TOLERANCE_MS}ms)")
            else:
                logger.warning(f"✗ Timing EXCEEDED tolerance ({TIMING_TOLERANCE_MS}ms)")
        
        logger.info(f"\n{'='*70}\n")
    
    def run(self):
        """Execute the complete trading strategy."""
        try:
            logger.info("="*70)
            logger.info("BYBIT FUNDING ARBITRAGE BOT - STARTING")
            logger.info("="*70)
            logger.info(f"Symbol: {self.symbol}")
            logger.info(f"Position Size: ${self.position_size_usdt:.2f}")
            logger.info(f"Funding Time: {FUNDING_TIME_HHMM}")
            logger.info(f"Entry Delay: {ENTRY_DELAY_MS}ms after funding")
            logger.info(f"Exit Time: {EXIT_DELAY_S}s after entry")
            logger.info("="*70 + "\n")
            
            # Validate credentials
            if not self.validate_credentials():
                return False
            
            # Calculate entry quantity
            if not self.calculate_entry_quantity():
                return False
            
            # Wait for funding settlement
            if not self.wait_for_funding_time():
                return False
            
            # Record funding timestamp and wait for entry
            funding_timestamp = time.perf_counter()
            logger.info(f"[DATA] Funding timestamp (perf_counter): {funding_timestamp:.6f}")
            
            self.entry_timestamp = self.wait_for_entry_time(funding_timestamp)
            
            # Execute entry
            if not self.execute_entry():
                return False
            
            # Wait for exit timing
            try:
                self.exit_timestamp = self.wait_for_exit_time()
            except ValueError as e:
                logger.error(f"Error during exit wait: {e}")
                return False
            
            # Execute exit
            if not self.execute_exit():
                return False
            
            # Calculate and display PnL
            self.print_trade_summary()
            
            logger.info("✓ Trade cycle completed successfully!")
            return True
            
        except KeyboardInterrupt:
            logger.warning("\n✗ Bot interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Unexpected error in bot execution: {e}", exc_info=True)
            return False

# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the trading bot."""
    try:
        # Validate environment setup
        if not BYBIT_API_KEY or BYBIT_API_KEY == 'your_testnet_api_key_here':
            logger.error("[FAIL] ERROR: API credentials not configured!")
            logger.error("Please update your .env file with valid Bybit testnet credentials:")
            logger.error("  BYBIT_API_KEY=your_key")
            logger.error("  BYBIT_API_SECRET=your_secret")
            return False
        
        # Initialize and run bot
        bot = BybitTradingBot(BYBIT_API_KEY, BYBIT_API_SECRET)
        success = bot.run()
        
        return success
        
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        return False

if __name__ == "__main__":
    success = main()
    exit_code = 0 if success else 1
    sys.exit(exit_code)
