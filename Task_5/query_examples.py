import psycopg2
from datetime import datetime, timedelta
import pandas as pd

class PriceQueryService:
    def __init__(self, db_config):
        self.db_config = db_config
    
    def get_connection(self):
        return psycopg2.connect(**self.db_config)
    
    def get_latest_price(self, symbol):
        """Get the latest price for a symbol"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, symbol, price 
            FROM price_data 
            WHERE symbol = %s 
            ORDER BY timestamp DESC 
            LIMIT 1
        """, (symbol.upper(),))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'timestamp': result[0],
                'symbol': result[1],
                'price': float(result[2])
            }
        return None
    
    def get_price_at_time(self, symbol, target_time):
        """Get price closest to a specific time"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT timestamp, symbol, price,
                   ABS(EXTRACT(EPOCH FROM (timestamp - %s))) as time_diff
            FROM price_data 
            WHERE symbol = %s 
            ORDER BY time_diff ASC
            LIMIT 1
        """, (target_time, symbol.upper()))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result:
            return {
                'timestamp': result[0],
                'symbol': result[1],
                'price': float(result[2]),
                'time_difference_seconds': result[3]
            }
        return None
    
    def get_price_range_1min(self, symbol, start_time):
        """Get highest and lowest price in 1-minute interval"""
        end_time = start_time + timedelta(minutes=1)
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                MIN(price) as lowest_price,
                MAX(price) as highest_price,
                COUNT(*) as data_points,
                MIN(timestamp) as first_update,
                MAX(timestamp) as last_update
            FROM price_data 
            WHERE symbol = %s 
                AND timestamp >= %s 
                AND timestamp < %s
        """, (symbol.upper(), start_time, end_time))
        
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] is not None:
            return {
                'symbol': symbol.upper(),
                'interval_start': start_time,
                'interval_end': end_time,
                'lowest_price': float(result[0]),
                'highest_price': float(result[1]),
                'data_points': result[2],
                'first_update': result[3],
                'last_update': result[4]
            }
        return None
    
    def get_statistics_summary(self):
        """Get overall statistics"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                symbol,
                COUNT(*) as total_updates,
                MIN(price) as min_price,
                MAX(price) as max_price,
                AVG(price) as avg_price,
                MIN(timestamp) as first_update,
                MAX(timestamp) as last_update
            FROM price_data 
            GROUP BY symbol
            ORDER BY symbol
        """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        summary = []
        for result in results:
            summary.append({
                'symbol': result[0],
                'total_updates': result[1],
                'min_price': float(result[2]),
                'max_price': float(result[3]),
                'avg_price': float(result[4]),
                'first_update': result[5],
                'last_update': result[6]
            })
        
        return summary

def demo_queries():
    """Demonstrate all query types"""
    # Update with your database credentials
    db_config = {
        'host': 'localhost',
        'database': 'binance_prices',
        'user': 'postgres',
        'password': 'suryan613',
        'port': 5432
    }
    
    query_service = PriceQueryService(db_config)
    
    print("=== Binance Price Query Demonstrations ===\n")
    
    # 1. Latest prices
    print("1. Latest Prices:")
    for symbol in ['BTCUSDT', 'ETHUSDT']:
        latest = query_service.get_latest_price(symbol)
        if latest:
            print(f"   {symbol}: ${latest['price']:,.2f} at {latest['timestamp']}")
        else:
            print(f"   {symbol}: No data available")
    
    print()
    
    # 2. Price at specific time (example: 30 seconds ago)
    print("2. Price 30 seconds ago:")
    target_time = datetime.now() - timedelta(seconds=30)
    for symbol in ['BTCUSDT', 'ETHUSDT']:
        price_data = query_service.get_price_at_time(symbol, target_time)
        if price_data:
            print(f"   {symbol}: ${price_data['price']:,.2f} at {price_data['timestamp']}")
            print(f"   (Time difference: {price_data['time_difference_seconds']:.2f} seconds)")
        else:
            print(f"   {symbol}: No data available")
    
    print()
    
    # 3. Price range in last minute
    print("3. Price Range in Last Minute:")
    one_min_ago = datetime.now() - timedelta(minutes=1)
    for symbol in ['BTCUSDT', 'ETHUSDT']:
        range_data = query_service.get_price_range_1min(symbol, one_min_ago)
        if range_data:
            print(f"   {symbol}:")
            print(f"     Lowest:  ${range_data['lowest_price']:,.2f}")
            print(f"     Highest: ${range_data['highest_price']:,.2f}")
            print(f"     Updates: {range_data['data_points']}")
        else:
            print(f"   {symbol}: No data in the last minute")
    
    print()
    
    # 4. Overall statistics
    print("4. Overall Statistics:")
    stats = query_service.get_statistics_summary()
    for stat in stats:
        print(f"   {stat['symbol']}:")
        print(f"     Total Updates: {stat['total_updates']:,}")
        print(f"     Price Range: ${stat['min_price']:,.2f} - ${stat['max_price']:,.2f}")
        print(f"     Average: ${stat['avg_price']:,.2f}")
        print(f"     Data Period: {stat['first_update']} to {stat['last_update']}")
        print()

if __name__ == "__main__":
    demo_queries()