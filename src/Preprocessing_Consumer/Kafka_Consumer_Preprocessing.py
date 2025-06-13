from kafka import KafkaConsumer, KafkaProducer
import json
import pandas as pd
from main import process_dataset
import redis
from config import config

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'batch-topic',
    bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    group_id='data-preprocessing',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

# Initialize Kafka producer for sending processed data
producer = KafkaProducer(
    bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

print("Listening for batches...")
for message in consumer:
    batch = message.value
    print("Received batch:", batch)
    df = pd.DataFrame(batch)

    # Process the batch
    df = process_dataset(df)
    
    print("Processed batch:", df)

    # Send processed data to retrain topic
    producer.send('retrain-topic', value=df.to_dict(orient='records'))
    redis_client.incr('consumer_preprocess_batch_count')
    print("Finished preprocessing and sent to retrain topic.\n")
