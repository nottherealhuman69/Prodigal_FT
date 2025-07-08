# Task 5: Binance WebSocket Price Precision Capture

## Overview
This project captures live cryptocurrency price updates from Binance WebSocket API for BTC/USDT and ETH/USDT pairs, stores them in PostgreSQL with high precision, and provides various query capabilities.

## Architecture

### System Components
```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Binance       │    │  Price Tracker   │    │   PostgreSQL    │
│   WebSocket     │───▶│  (WebSocket      │───▶│   Database      │
│   Stream        │    │   Client)        │    │                 │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │  Query Service   │
                       │  (Data Analysis) │
                       └──────────────────┘
```

### Data Flow
1. **WebSocket Connection**: Connects to Binance WebSocket stream for real-time ticker data
2. **Data Processing**: Processes incoming JSON messages and extracts price information
3. **Database Storage**: Stores timestamp, symbol, and price with high precision (DECIMAL 20,8)
4. **Query Interface**: Provides various query methods for data analysis

## Database Schema

```sql
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    symbol VARCHAR(20) NOT NULL,
    price DECIMAL(20, 8) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_symbol_timestamp ON price_data(symbol, timestamp);
```

## Features

### Real-time Data Capture
- Connects to Binance WebSocket API
- Handles BTC/USDT and ETH/USDT streams
- Processes multiple updates per second
- Automatic reconnection on connection loss

### Query Capabilities
1. **Latest Price**: Get the most recent price for any symbol
2. **Price at Specific Time**: Find price closest to a target timestamp
3. **Price Range**: Get highest/lowest prices within a 1-minute interval
4. **Statistics Summary**: Overall statistics including min/max/average prices

## Prerequisites

### Required Software
- Python 3.8+
- PostgreSQL 12+
- Git

### Python Dependencies
```bash
pip install asyncio websockets psycopg2-binary pandas
```

### Database Setup
1. Install PostgreSQL
2. Create database and user:
```sql
CREATE DATABASE binance_prices;
CREATE USER postgres WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE binance_prices TO postgres;
```

## Installation & Setup

### Step 1: Clone and Navigate
```bash
git clone <repository-url>
cd Task_5
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Database
Edit the database configuration in both files:
```python
db_config = {
    'host': 'localhost',
    'database': 'binance_prices',
    'user': 'postgres',
    'password': 'your_password',
    'port': 5432
}
```

### Step 4: Initialize Database
The database table will be created automatically when running the price tracker.

## Usage

### Running the Price Tracker
```bash
python price_tracker.py
```

This will:
- Initialize the database table
- Connect to Binance WebSocket
- Start capturing real-time price data
- Log all price updates to console
- Store data in PostgreSQL

### Running Query Examples
```bash
python query_examples.py
```

This will demonstrate:
- Latest prices for BTC/USDT and ETH/USDT
- Price lookup 30 seconds ago
- Price range analysis for the last minute
- Overall statistics summary

## Query Examples Output

```
=== Binance Price Query Demonstrations ===

1. Latest Prices:
   BTCUSDT: $43,250.50 at 2024-01-15 10:30:45
   ETHUSDT: $2,680.75 at 2024-01-15 10:30:46

2. Price 30 seconds ago:
   BTCUSDT: $43,248.20 at 2024-01-15 10:30:15
   (Time difference: 2.30 seconds)

3. Price Range in Last Minute:
   BTCUSDT:
     Lowest:  $43,245.10
     Highest: $43,252.80
     Updates: 45

4. Overall Statistics:
   BTCUSDT:
     Total Updates: 2,450
     Price Range: $43,200.00 - $43,300.00
     Average: $43,250.25
```

## Docker Setup (Optional)

### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "price_tracker.py"]
```

### Docker Compose
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: binance_prices
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: your_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  price-tracker:
    build: .
    depends_on:
      - postgres
    environment:
      - DB_HOST=postgres
    restart: unless-stopped

volumes:
  postgres_data:
```

### Run with Docker
```bash
docker-compose up -d
```

## Technical Implementation Details

### WebSocket Connection
- Uses `websockets` library for async connection
- Connects to `wss://stream.binance.com:9443/ws/`
- Subscribes to ticker streams for multiple symbols
- Handles connection drops with automatic reconnection

### Data Precision
- Uses `DECIMAL(20, 8)` for price storage
- Maintains 8 decimal places for cryptocurrency precision
- Handles Binance's millisecond timestamps accurately

### Error Handling
- Database connection retry logic
- WebSocket reconnection on failures
- Comprehensive logging for debugging
- Graceful shutdown on interruption

## Performance Considerations

### Database Optimization
- Indexed on (symbol, timestamp) for fast queries
- Uses prepared statements for efficient inserts
- Connection pooling for high-throughput scenarios

### Memory Management
- Efficient JSON parsing
- Minimal memory footprint for long-running processes
- Proper resource cleanup

## Troubleshooting

### Common Issues
1. **Database Connection**: Verify PostgreSQL is running and credentials are correct
2. **WebSocket Connection**: Check internet connectivity and firewall settings
3. **Missing Data**: Ensure the price tracker runs continuously for data collection

### Logs
Monitor console output for:
- Connection status messages
- Price update confirmations
- Error messages and reconnection attempts

## Future Enhancements

### Potential Improvements
- Add more cryptocurrency pairs
- Implement data retention policies
- Add real-time alerting for price changes
- Create REST API for query operations
- Add data visualization dashboard

### Scalability Options
- Use connection pooling for database
- Implement message queuing for high-throughput
- Add horizontal scaling with multiple instances
- Use time-series database like InfluxDB for better performance

## Files Description

- `price_tracker.py`: Main WebSocket client for real-time data capture
- `query_examples.py`: Demonstration of various query operations
- `requirements.txt`: Python dependencies
- `README.md`: This documentation file
- `demo_script.md`: 5-minute demo walkthrough script