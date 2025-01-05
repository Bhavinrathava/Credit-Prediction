import streamlit as st
import requests
import pandas as pd
import time

# Backend URL for metrics
METRICS_API_URL = "http://localhost:5000/metrics"
FLAGGED_CUSTOMERS_API_URL = "http://localhost:5000/flagged-customers"  # New API for flagged customers data

# Set up Streamlit app layout
st.title("Kafka Metrics Dashboard")
st.markdown("Real-time metrics from the Kafka Producer and Consumers.")

# Create placeholders for metrics
producer_batches = st.empty()
consumer1_batches = st.empty()
consumer2_batches = st.empty()

# Graph container for flagged customers
st.markdown("### Flagged Customers Over Time")
flagged_customers_chart = st.empty()

# Fetch metrics from Flask API
def fetch_metrics():
    try:
        response = requests.get(METRICS_API_URL)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Failed to fetch metrics: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching metrics: {e}")
        return None

# Fetch flagged customers data
def fetch_flagged_customers():
    try:
        response = requests.get(FLAGGED_CUSTOMERS_API_URL)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        else:
            st.error(f"Failed to fetch flagged customers data: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Error fetching flagged customers data: {e}")
        return None

# Main loop for live metrics and graph updates
st.markdown("### Live Metrics")
history = pd.DataFrame(columns=["Time", "Producer", "Consumer Flag", "Consumer Retrain"])

while True:
    # Fetch and update live metrics
    metrics = fetch_metrics()
    if metrics:
        current_time = time.strftime("%H:%M:%S")
        new_row = pd.DataFrame([{
            "Time": current_time,
            "Producer": int(metrics.get("producer_batches", 0)),
            "Consumer 1": int(metrics.get("consumer1_batches", 0)),
            "Consumer 2": int(metrics.get("consumer2_batches", 0))
        }])

        # Concatenate the new row to the history DataFrame
        history = pd.concat([history, new_row], ignore_index=True)

        producer_batches.metric("Producer Batches Sent", metrics.get("producer_batches", 0))
        consumer1_batches.metric("Flag Batches Processed", metrics.get("consumer_flag_batches", 0))
        consumer2_batches.metric("Retrain Batches Processed", metrics.get("consumer_retrain_batches", 0))

    # Fetch flagged customers and update graph
    # Update flagged customers chart
    flagged_customers = fetch_flagged_customers()
    if flagged_customers is not None and not flagged_customers.empty:
        flagged_customers['flagged_timestamp'] = pd.to_datetime(flagged_customers['flagged_timestamp'])
        # Aggregate counts by minute
        flagged_customers_count = (
            flagged_customers.groupby(flagged_customers['flagged_timestamp'].dt.floor('min'))
            .size()
            .reset_index(name="count")
        )
        flagged_customers_count.rename(columns={"flagged_timestamp": "Time"}, inplace=True)

        # Display bar chart
        flagged_customers_chart.bar_chart(
            flagged_customers_count.set_index("Time")["count"]
        )


    time.sleep(5)  # Update every 5 seconds
