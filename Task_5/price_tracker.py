import asyncio
import websockets
import json
import psycopg2
from datetime import datetime
import logging
from decimal import Decimal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class BinancePriceTracker:
    def __init__(self, db_config):
        self.db_config = db_config
        self.symbols = ['btcusdt', 'ethusdt']
        self.websocket_url = "wss://stream.binance.com:9443/ws/"
        
    def init_database(self):
        """Initialize PostgreSQL database and create table"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            # Create table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS price_data (
                    id SERIAL PRIMARY KEY,
                    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
                    symbol VARCHAR(20) NOT NULL,
                    price DECIMAL(20, 8) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                );
            """)
            
            # Create indexes for better query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_symbol_timestamp 
                ON price_data(symbol, timestamp);
            """)
            
            conn.commit()
            cursor.close()
            conn.close()
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error(f"Database initialization error: {e}")
            raise
    
    def store_price_data(self, symbol, price, timestamp):
        """Store price data in PostgreSQL"""
        try:
            conn = psycopg2.connect(**self.db_config)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO price_data (timestamp, symbol, price)
                VALUES (%s, %s, %s)
            """, (timestamp, symbol.upper(), Decimal(str(price))))
            
            conn.commit()
            cursor.close()
            conn.close()
            
        except Exception as e:
            logger.error(f"Error storing data: {e}")
    
    async def handle_message(self, message):
        """Handle incoming WebSocket message"""
        try:
            data = json.loads(message)
            
            if 'c' in data:  # 'c' is current price in ticker stream
                symbol = data['s']
                price = float(data['c'])
                # Use event time from Binance
                timestamp = datetime.fromtimestamp(data['E'] / 1000)
                
                logger.info(f"{symbol}: ${price} at {timestamp}")
                
                # Store in database
                self.store_price_data(symbol, price, timestamp)
                
        except Exception as e:
            logger.error(f"Error handling message: {e}")
    
    async def start_websocket(self):
        """Start WebSocket connection to Binance"""
        # Create stream URL for multiple symbols
        streams = [f"{symbol}@ticker" for symbol in self.symbols]
        stream_url = f"{self.websocket_url}{'/'.join(streams)}"
        
        logger.info(f"Connecting to: {stream_url}")
        
        try:
            async with websockets.connect(stream_url) as websocket:
                logger.info("Connected to Binance WebSocket")
                
                async for message in websocket:
                    await self.handle_message(message)
                    
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            # Reconnect after 5 seconds
            await asyncio.sleep(5)
            await self.start_websocket()

def main():
    # Database configuration - update with your credentials
    db_config = {
        'host': 'localhost',
        'database': 'binance_prices',
        'user': 'postgres',
        'password': 'suryan613',
        'port': 5432
    }
    
    # Initialize tracker
    tracker = BinancePriceTracker(db_config)
    tracker.init_database()
    
    # Start WebSocket connection
    try:
        asyncio.run(tracker.start_websocket())
    except KeyboardInterrupt:
        logger.info("Shutting down...")

if __name__ == "__main__":
    main()