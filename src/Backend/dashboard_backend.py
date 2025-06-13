from flask import Flask, jsonify, request
import redis
import pandas as pd
from config import config

# Initialize Flask app and Redis
app = Flask(__name__)
redis_client = redis.StrictRedis(host=config.REDIS_HOST, port=config.REDIS_PORT, decode_responses=True)

@app.route('/metrics', methods=['GET'])
def get_metrics():
    producer_count = int(redis_client.get('producer_batch_count') or 0)
    consumer1_count = int(redis_client.get('consumer_flag_batch_count') or 0)
    consumer2_count = int(redis_client.get('consumer_retrain_batch_count') or 0)
    return jsonify({
        "producer_batches": producer_count,
        "consumer_flag_batches": consumer1_count,
        "consumer_retrain_batches": consumer2_count
    })

@app.route('/flagged-customers', methods=['GET'])
def get_flagged_customers():
    # Read high-risk customer data from CSV
    try:
        data = pd.read_csv(config.HIGH_RISK_DATA_PATH)
        return data.to_dict(orient='records')
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route('/data-drift', methods=['GET'])
def get_data_drift():
    try:
        # Load historic and recent data
        historic_data = pd.read_sql("SELECT * FROM flagged_customers WHERE flagged_timestamp < NOW() - INTERVAL '1 hour'", conn)
        recent_data = pd.read_sql("SELECT * FROM flagged_customers WHERE flagged_timestamp >= NOW() - INTERVAL '1 hour'", conn)

        # Calculate drift statistics (e.g., using KL divergence or other methods)
        # For simplicity, let's assume we calculate a simple count difference
        historic_count = len(historic_data)
        recent_count = len(recent_data)
        drift_statistic = recent_count - historic_count

        return jsonify({
            "historic_count": historic_count,
            "recent_count": recent_count,
            "drift_statistic": drift_statistic
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    app.run(host='0.0.0.0', port=5000)
