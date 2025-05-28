import MetaTrader5 as mt5
from loguru import logger # Add logger
# from ..models.data_models import TickData # We'll use this in the route, service returns dict for now

# Global variable to keep track of MT5 connection status
_mt5_initialized = False

def initialize_mt5() -> bool:
    """
    Initializes the MetaTrader 5 terminal connection.
    """
    global _mt5_initialized
    # Attempt to initialize MetaTrader 5
    # For now, we assume MT5 is installed and path is configured if necessary
    # You might need to specify the path to the terminal if it's not found automatically
    # e.g., mt5.initialize(path="C:\\Program Files\\MetaTrader 5\\terminal64.exe")
    if not mt5.initialize():
        print(f"MT5 initialize() failed, error code = {mt5.last_error()}")
        _mt5_initialized = False
        return False

    # Optional: Login to a trading account if needed
    # account = settings.MT5_ACCOUNT
    # password = settings.MT5_PASSWORD
    # server = settings.MT5_SERVER
    # if account and password and server:
    #     if not mt5.login(account, password=password, server=server):
    #         print(f"MT5 login failed for account {account}, error code = {mt5.last_error()}")
    #         mt5.shutdown()
    #         _mt5_initialized = False
    #         return False
    #     else:
    #         print(f"MT5 login successful for account {account}")
    # else:
    #     print("MT5: No login credentials provided, assuming terminal is already logged in or using a demo account.")

    # Check terminal information to confirm connection
    terminal_info = mt5.terminal_info()
    if not terminal_info:
        print(f"MT5 terminal_info() failed, error code = {mt5.last_error()}")
        mt5.shutdown() # Ensure shutdown if terminal info fails
        _mt5_initialized = False
        return False

    print(f"MT5 initialized successfully. Terminal: {terminal_info.name}, Company: {terminal_info.company}")
    _mt5_initialized = True
    return True

def shutdown_mt5():
    """
    Shuts down the MetaTrader 5 terminal connection.
    """
    global _mt5_initialized
    if _mt5_initialized:
        mt5.shutdown()
        print("MT5 connection shut down.")
        _mt5_initialized = False

def is_mt5_connected() -> bool:
    """
    Checks if the MT5 terminal is currently initialized and connected.
    A more robust check involves trying to get terminal_info.
    """
    global _mt5_initialized
    if not _mt5_initialized:
        return False
    
    # A quick check to see if we can still get terminal info
    # This can indicate if the terminal was closed externally
    if mt5.terminal_info():
        return True
    else:
        # If terminal_info fails, our connection is likely lost
        print("MT5 connection lost (terminal_info failed).")
        _mt5_initialized = False # Update status
        return False

# --- Placeholder for future functions ---

def get_current_tick(symbol: str) -> dict | None:
    """
    Fetches the latest tick data for a given symbol.
    Returns a dictionary or None if fetching fails.
    """
    if not is_mt5_connected():
        logger.warning("MT5 not connected. Cannot fetch tick for {symbol}.")
        return None
    
    # Ensure the symbol is available in MarketWatch
    symbol_info = mt5.symbol_info(symbol)
    if symbol_info is None:
        logger.warning(f"Symbol {symbol} not found, error code = {mt5.last_error()}")
        # Attempt to add the symbol to MarketWatch
        if not mt5.symbol_select(symbol, True):
            logger.error(f"Failed to select symbol {symbol} to MarketWatch, error code = {mt5.last_error()}")
            return None
        # Re-check after attempting to select
        symbol_info = mt5.symbol_info(symbol)
        if symbol_info is None:
            logger.error(f"Symbol {symbol} still not found after attempting to select.")
            return None
        logger.info(f"Symbol {symbol} added to MarketWatch.")

    tick = mt5.symbol_info_tick(symbol)
    if tick:
        # Convert named tuple to dictionary
        return tick._asdict()
    else:
        logger.error(f"Failed to get tick for {symbol}, error code = {mt5.last_error()}")
        return None

# We will add functions for historical data and publishing to Redis later.

