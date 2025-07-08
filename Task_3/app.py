from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json
import os
import time
import uuid
from datetime import datetime

app = Flask(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = 'events'

# Initialize Kafka producer with retry logic
def get_kafka_producer():
    max_retries = 5
    for attempt in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                request_timeout_ms=10000,
                max_block_ms=10000
            )
            print(f"Connected to Kafka at {KAFKA_BOOTSTRAP_SERVERS}")
            return producer
        except Exception as e:
            print(f"Attempt {attempt + 1}: Failed to connect to Kafka: {e}")
            if attempt < max_retries - 1:
                time.sleep(5)
    raise Exception("Failed to connect to Kafka after all retries")

# Global producer instance
producer = None

# In-memory storage for status
event_status = {}

@app.route('/register_event', methods=['POST'])
def register_event():
    global producer
    try:
        # Initialize producer if not done
        if producer is None:
            producer = get_kafka_producer()
            
        data = request.get_json()
        
        # Generate unique event ID
        event_id = str(uuid.uuid4())
        
        # Create event message
        event_message = {
            'event_id': event_id,
            'timestamp': datetime.now().isoformat(),
            'data': data,
            'status': 'pending'
        }
        
        # Send to Kafka
        producer.send(KAFKA_TOPIC, value=event_message)
        producer.flush()
        
        # Store initial status
        event_status[event_id] = 'pending'
        
        return jsonify({
            'message': 'Event registered successfully',
            'event_id': event_id,
            'status': 'pending'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/get_status/<event_id>', methods=['GET'])
def get_status(event_id):
    try:
        status = event_status.get(event_id, 'not_found')
        return jsonify({
            'event_id': event_id,
            'status': status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    app.run(host='0.0.0.0', port=5000, debug=True)