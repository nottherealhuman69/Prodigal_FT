from kafka import KafkaConsumer
import json
import os
import time
import logging
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/consumer.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = os.environ.get('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
KAFKA_TOPIC = 'events'

def process_event(event_data):
    """Process the event - simulate some work"""
    try:
        event_id = event_data.get('event_id')
        logger.info(f"Processing event: {event_id}")
        
        # Simulate processing time
        time.sleep(0.1)
        
        # Log the processed event
        logger.info(f"Event {event_id} processed successfully")
        
        # Write to file for demonstration
        with open('logs/processed_events.txt', 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Processed: {event_id}\n")
        
        return True
        
    except Exception as e:
        logger.error(f"Error processing event: {e}")
        return False

def main():
    # Create logs directory
    os.makedirs('logs', exist_ok=True)
    
    # Wait and retry connection to Kafka
    max_retries = 10
    for attempt in range(max_retries):
        try:
            logger.info(f"Attempting to connect to Kafka (attempt {attempt + 1})")
            
            # Initialize Kafka consumer
            consumer = KafkaConsumer(
                KAFKA_TOPIC,
                bootstrap_servers=[KAFKA_BOOTSTRAP_SERVERS],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                group_id='event-processors',
                auto_offset_reset='earliest',
                enable_auto_commit=True
            )
            
            logger.info("Successfully connected to Kafka")
            logger.info("Consumer started, waiting for messages...")
            break
            
        except Exception as e:
            logger.warning(f"Failed to connect to Kafka: {e}")
            if attempt < max_retries - 1:
                time.sleep(10)
            else:
                logger.error("Failed to connect to Kafka after all retries")
                return
    
    try:
        for message in consumer:
            event_data = message.value
            logger.info(f"Received message: {event_data}")
            
            # Process the event
            success = process_event(event_data)
            
            if success:
                logger.info("Event processed successfully")
            else:
                logger.error("Event processing failed")
                
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    except Exception as e:
        logger.error(f"Consumer error: {e}")
    finally:
        consumer.close()

if __name__ == '__main__':
    main()