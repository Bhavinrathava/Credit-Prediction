from kafka import KafkaConsumer
import json
import joblib
import pandas as pd
from main import process_dataset, train_model, train_LR_model, load_model
import redis
from datetime import datetime
import psycopg2
from config import config

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'retrain-topic',
    bootstrap_servers=config.KAFKA_BOOTSTRAP_SERVERS,
    auto_offset_reset='earliest',
    group_id='model-retraining',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)


# Database connection
conn = psycopg2.connect(
    dbname="credit_db",
    user="user",
    password="password",
    host="db"
)
cur = conn.cursor()

# Create table if not exists
cur.execute("""
CREATE TABLE IF NOT EXISTS retrain_data (
    id SERIAL PRIMARY KEY,
    data JSONB,
    retrain_timestamp TIMESTAMP
)
""")
conn.commit()

for message in consumer:
    batch = message.value
    print("Received batch:", batch)
    df = pd.DataFrame(batch)

    # Insert data into database
    cur.execute("""
    INSERT INTO retrain_data (data, retrain_timestamp)
    VALUES (%s, %s)
    """, (json.dumps(batch), datetime.now()))
    conn.commit()
    print("Inserted retrain data into database")

    model_path = config.RF_MODEL_PATH

    try:
        best_DT_model, accuracy = train_model(df, model_path)
        print("Best Decision Tree Model:", best_DT_model)
    except:
        print("Error in training Decision Tree Model")
        best_DT_model = None

    # load Model 
    model_path = config.LR_MODEL_PATH

    try:
        best_LR_model, accuracy = train_LR_model(df, model_path)
        print("Best Logistic Regression Model:", best_LR_model)
    except:
        print("Error in training Logistic Regression Model")
        best_LR_model = None
    
    redis_client.incr('consumer_retrain_batch_count')
    print("Finished Retraining on batch.\n")
