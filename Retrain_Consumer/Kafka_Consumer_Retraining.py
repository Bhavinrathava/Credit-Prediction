from kafka import KafkaConsumer
import json
import joblib
import pandas as pd
from main import process_dataset, train_model, train_LR_model, load_model
import redis
from datetime import datetime

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'batch-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='model-retraining',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)


print("Listening for batches...")
for message in consumer:
    batch = message.value
    print("Received batch:", batch)
    df = pd.DataFrame(batch)

    # Process the batch
    df = process_dataset(df)
    
    print("Processed batch:", df)


    

    # load Model 
    model_path = 'Models/RFModel.pkl'

    try:
        best_DT_model, accuracy = train_model(df, model_path)
        print("Best Decision Tree Model:", best_DT_model)
    except:
        print("Error in training Decision Tree Model")
        best_DT_model = None

    # load Model 
    model_path = 'Models/LRModel.pkl'

    try:
        best_LR_model, accuracy = train_LR_model(df, model_path)
        print("Best Logistic Regression Model:", best_LR_model)
    except:
        print("Error in training Logistic Regression Model")
        best_LR_model = None
    
    redis_client.incr('consumer_retrain_batch_count')
    print("Finished Retraining on batch.\n")
