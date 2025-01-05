from kafka import KafkaConsumer
import json
import joblib
import pandas as pd
from main import process_dataset, train_model, train_LR_model, load_model
import redis
from datetime import datetime
import os

# Initialize Kafka consumer
consumer = KafkaConsumer(
    'batch-topic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='customer-flagging',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Path to the output file
output_file = "Data/high_risk_data.csv"

def ensure_csv_columns(df, output_file):
    """
    Ensure that the CSV file has the same columns as the DataFrame.
    If the file exists and columns do not match, rewrite the file with the new columns.
    """
    if os.path.exists(output_file):
        existing_df = pd.read_csv(output_file)
        if not set(df.columns).issubset(set(existing_df.columns)):
            # If columns are missing, rewrite the file with the new columns
            print("Column mismatch detected. Rewriting the CSV file with updated columns.")
            df.to_csv(output_file, mode='w', index=False, header=True)

print("Listening for batches...")
for message in consumer:
    batch = message.value
    print("Received batch:", batch)
    df = pd.DataFrame(batch)

    # Process the batch
    df = process_dataset(df)
    
    print("Processed batch:", df)

    # Load models
    model_path = 'Models/RFModel.pkl'
    rf_model = load_model(model_path)

    model_path = 'Models/LRModel.pkl'
    lr_model = load_model(model_path)

    # Predict the batch
    y_rf_pred = rf_model.predict(df.drop(columns=["Risk"]))
    y_lr_pred = lr_model.predict(df.drop(columns=["Risk"]))
    
    weighted_score = (y_rf_pred + y_lr_pred) / 2
    print("Weighted Score:", weighted_score)

    # Identify high-risk customers
    df['weighted_Score'] = weighted_score
    high_risk_data = df[weighted_score < 0.5]

    print(f"Detected {len(high_risk_data)} high risk customers.")

    if not high_risk_data.empty:
        # Add timestamp to high-risk data
        high_risk_data['flagged_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Ensure CSV columns are consistent
        ensure_csv_columns(high_risk_data, output_file)

        # Append to CSV
        try:
            high_risk_data.to_csv(output_file, mode='a', header=not os.path.exists(output_file), index=False)
            print(f"Appended high risk data to '{output_file}'")
        except Exception as e:
            print(f"Error saving high risk data: {e}")

    redis_client.incr('consumer_flag_batch_count')
    print("Finished flagging Customers on batch.\n")
