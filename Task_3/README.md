# Task 3: Kafka + Zookeeper for High-Throughput API Ingestion

## Overview
This task implements a high-throughput event ingestion system using Kafka and Zookeeper. The system can handle thousands of requests per minute with reliable message delivery and processing.

## Architecture

### Components
1. **Flask API** (`app.py`) - REST API with two endpoints
2. **Kafka Consumer** (`consumer.py`) - Processes events from Kafka topic
3. **Kafka + Zookeeper** - Message queue infrastructure
4. **Load Test Script** (`load_test.py`) - Simulates high-throughput requests

### Flow Diagram
```
Client Requests → Flask API → Kafka Topic → Consumer → Logs/Storage
     ↓              ↓            ↓           ↓
Load Test     /register_event   events    Process &
Script        /get_status       topic     Log Events
```

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.9+
- All dependencies in `requirements.txt`

### Environment Setup

1. **Clone and navigate to Task 3 directory**
```bash
cd Task_3
```

2. **Start the complete system**
```bash
docker-compose up --build
```

This will start:
- Zookeeper (port 2181)
- Kafka (port 9092)
- Flask API (port 5001)
- Kafka Consumer

3. **Wait for all services to be ready** (about 30-60 seconds)

### Testing the System

#### Health Check
```bash
curl http://localhost:5001/health
```

#### Manual Event Registration
```bash
curl -X POST http://localhost:5001/register_event \
  -H "Content-Type: application/json" \
  -d '{"test": "data", "message": "hello world"}'
```

#### Check Event Status
```bash
curl http://localhost:5001/get_status/EVENT_ID
```

#### Run Load Test
```bash
python load_test.py
```

## API Endpoints

### POST /register_event
- **Purpose**: Register a new event
- **Input**: JSON payload
- **Output**: Event ID and status
- **Example**:
```json
{
  "event_id": "uuid-string",
  "status": "pending",
  "message": "Event registered successfully"
}
```

### GET /get_status/{event_id}
- **Purpose**: Get event processing status
- **Input**: Event ID in URL
- **Output**: Event status
- **Example**:
```json
{
  "event_id": "uuid-string",
  "status": "pending"
}
```

### GET /health
- **Purpose**: Health check endpoint
- **Output**: System health status

## Load Testing

The `load_test.py` script simulates high-throughput scenarios:
- **Total Requests**: 1,000
- **Concurrent Threads**: 10
- **Requests per Thread**: 100
- **Target Rate**: ~1,000 requests/minute

### Running Load Test
```bash
python load_test.py
```

## Monitoring and Logs

### Consumer Logs
- Location: `logs/consumer.log`
- Contains: Event processing logs, errors, connection status

### Processed Events
- Location: `logs/processed_events.txt`
- Contains: Timestamps and event IDs of processed events

### Docker Logs
```bash
# View API logs
docker-compose logs api

# View consumer logs
docker-compose logs consumer

# View Kafka logs
docker-compose logs kafka
```

## Key Features

### Reliability
- **Message Durability**: Kafka ensures messages persist even if consumers are down
- **Retry Logic**: Both producer and consumer have retry mechanisms
- **Error Handling**: Comprehensive error handling throughout the system

### Scalability
- **Horizontal Scaling**: Multiple consumer instances can process events
- **Load Balancing**: Kafka distributes messages across consumer group members
- **Backpressure Handling**: System handles high request volumes gracefully

### Monitoring
- **Health Checks**: API health endpoint for monitoring
- **Logging**: Structured logging for debugging and monitoring
- **Status Tracking**: Event status tracking for request lifecycle

## Troubleshooting

### Common Issues

1. **Kafka Connection Failed**
   - Wait longer for Kafka to start (can take 30-60 seconds)
   - Check if ports 9092 and 2181 are available

2. **Consumer Not Processing**
   - Check consumer logs: `docker-compose logs consumer`
   - Verify Kafka topic exists: `docker exec kafka kafka-topics.sh --list --zookeeper zookeeper:2181`

3. **Load Test Failures**
   - Ensure API is healthy: `curl http://localhost:5001/health`
   - Check API logs for errors: `docker-compose logs api`

### Cleanup
```bash
# Stop all services
docker-compose down

# Remove volumes (optional)
docker-compose down -v
```

## Technology Stack
- **Flask**: Web framework for REST API
- **Kafka**: Distributed streaming platform
- **Zookeeper**: Kafka coordination service
- **Docker**: Containerization
- **Python**: Programming language

## Performance Characteristics
- **Throughput**: Handles 1,000+ requests/minute
- **Latency**: Sub-second event processing
- **Reliability**: At-least-once delivery guarantee
- **Scalability**: Can scale consumers horizontally