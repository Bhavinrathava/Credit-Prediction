# Configuration file for the project

# Redis configuration
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# Kafka configuration
KAFKA_BOOTSTRAP_SERVERS = 'localhost:9092'
KAFKA_BATCH_TOPIC = 'batch-topic'

# API URLs
METRICS_API_URL = "http://localhost:5000/metrics"
FLAGGED_CUSTOMERS_API_URL = "http://localhost:5000/flagged-customers"

# Data paths
GERMAN_CREDIT_DATA_PATH = "Data/german_credit_data.csv"
HIGH_RISK_DATA_PATH = "Data/high_risk_data.csv"

# Model paths
RF_MODEL_PATH = 'Models/RFModel.pkl'
LR_MODEL_PATH = 'Models/LRModel.pkl'
