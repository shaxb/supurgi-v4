from fastapi import FastAPI, HTTPException # Add HTTPException
import uvicorn
from loguru import logger
import sys
from contextlib import asynccontextmanager # Import asynccontextmanager
import asyncio
from .services import mt5_service, redis_service

# Configure Loguru for more detailed output during development
logger.remove() # Removes default handler
logger.add(sys.stderr, level="DEBUG") # Add stderr handler with DEBUG level

# Import your MT5 service
from .services import mt5_service, redis_service
from .models.data_models import TickData # Import your Pydantic model

# Lifespan context manager
@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    # Code to run on startup
    logger.info("Application startup: Initializing resources...")
    
    # Initialize MT5
    if not mt5_service.initialize_mt5():
        logger.critical("Failed to initialize MetaTrader 5 connection during startup.")
    else:
        logger.info("MetaTrader 5 initialized successfully during startup.")
    
    # Initialize Redis
    # if not redis_service.initialize_redis():
    #     logger.warning("Failed to initialize Redis connection. Live streaming will be disabled.")
    # else:
    #     logger.info("Redis connection initialized during startup.")
    #     # Start background streaming task
    #     asyncio.create_task(stream_market_data())
    #     logger.info("Background market data streaming started.")
    
    yield  # This is where the application runs

    # Code to run on shutdown
    logger.info("Application shutdown: Cleaning up resources...")
    mt5_service.shutdown_mt5()
    logger.info("MetaTrader 5 connection shut down.")
    redis_service.shutdown_redis()
    logger.info("Redis connection closed.")

app = FastAPI(
    title="Market Data Service",
    description="Provides live and historical market data.",
    version="0.1.0",
    lifespan=lifespan  # Assign the lifespan manager to the FastAPI app
)

# Basic health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """
    Health check endpoint to verify the service is running.
    """
    return {"status": "ok", "mt5_connected": mt5_service.is_mt5_connected()}

@app.get("/tick/{symbol}", response_model=TickData, tags=["Market Data"])
async def get_tick_data(symbol: str):
    """
    Get the latest tick data for a specified symbol.
    """
    logger.debug(f"Request received for tick data: {symbol}")
    tick_data_dict = mt5_service.get_current_tick(symbol) # symbol must the same as in MT5, mt5 use prefix "m" for ex. EURUSDm" 
    
    if tick_data_dict is None:
        logger.warning(f"No tick data found for symbol: {symbol}")
        raise HTTPException(status_code=404, detail=f"Tick data not found for symbol {symbol}")
    # Pydantic will validate the dictionary against the TickData model
    # If fields are missing or types are wrong, it will raise an error
    try:
        tick_data_model = TickData(**tick_data_dict)
    except Exception as e:
        logger.error(f"Error converting tick data to Pydantic model for {symbol}: {e}")
        logger.error(f"Raw tick data was: {tick_data_dict}")
        raise HTTPException(status_code=500, detail=f"Error processing tick data for {symbol}")
        
    return tick_data_model

# Background task for live data streaming
async def stream_market_data():
    """
    Background task that continuously fetches and publishes market data.
    """
    symbols = ["EURUSDm", "GBPUSDm", "USDJPYm"]  # Add your broker's symbol format
    
    while True:
        try:
            if not mt5_service.is_mt5_connected():
                logger.warning("MT5 not connected. Pausing market data streaming.")
                await asyncio.sleep(5)
                continue
                
            if not redis_service.is_redis_connected():
                logger.warning("Redis not connected. Pausing market data streaming.")
                await asyncio.sleep(5)
                continue
            
            for symbol in symbols:
                tick_data = mt5_service.get_current_tick(symbol)
                if tick_data:
                    redis_service.publish_tick_data(symbol, tick_data)
                
            await asyncio.sleep(1)  # Stream every 1 second (adjust as needed)
            
        except Exception as e:
            logger.error(f"Error in market data streaming: {e}")
            await asyncio.sleep(5)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")




