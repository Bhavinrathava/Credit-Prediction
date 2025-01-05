Here’s a **README.md** file for your project:

---

# **Kafka-Based Real-Time Data Processing with Flask, Streamlit, and Docker**

This project implements a real-time data processing pipeline using **Kafka**, **Redis**, **Flask**, **Streamlit**, and **Docker**. The pipeline processes streaming data to flag high-risk customers, retrain machine learning models, and provide a live dashboard for monitoring the metrics and flagged customers.

---

## **Project Structure**

```
/app
├── docker-compose.yml           # Orchestrates all services
├── consumer.Dockerfile          # Dockerfile for both consumers
├── producer.Dockerfile          # Dockerfile for Kafka producer
├── flask.Dockerfile             # Dockerfile for Flask backend
├── streamlit.Dockerfile         # Dockerfile for Streamlit dashboard
├── requirements.txt             # Python dependencies for all services
├── producer.py                  # Kafka producer script
├── retrain_consumer.py          # Kafka consumer for model retraining
├── flagging_consumer.py         # Kafka consumer for high-risk flagging
├── flask_backend/
│   └── app.py                   # Flask backend for metrics and flagged data
├── streamlit_frontend/
│   └── dashboard.py             # Streamlit frontend for the live dashboard
├── Models/                      # Directory for shared models
│   ├── RFModel.pkl
│   └── LRModel.pkl
└── Data/                        # Directory for shared data
    └── high_risk_data.csv
```

---

## **Components**

1. **Kafka Producer**:
   - Reads data from a CSV file (`german_credit_data.csv`) and streams it to Kafka in batches.
   - Tracks the number of batches sent using Redis.

2. **Flagging Consumer**:
   - Processes streamed data from Kafka to identify high-risk customers.
   - Saves flagged customers to a shared CSV file (`high_risk_data.csv`).
   - Updates Redis with the number of processed batches.

3. **Retraining Consumer**:
   - Processes streamed data to retrain machine learning models (`RFModel.pkl` and `LRModel.pkl`).
   - Updates Redis with the number of processed batches.

4. **Flask Backend**:
   - Provides APIs to retrieve:
     - Metrics from Redis (`/metrics`).
     - Flagged customers from the shared CSV file (`/flagged-customers`).

5. **Streamlit Dashboard**:
   - Displays real-time metrics and a bar chart of flagged customers over time.
   - Updates automatically every 5 seconds.

6. **Docker Compose**:
   - Orchestrates all services, including Kafka, Redis, Flask, and Streamlit.

---

## **Prerequisites**

- **Docker**: Install [Docker](https://www.docker.com/get-started).
- **Docker Compose**: Comes bundled with Docker Desktop or install it separately.

---

## **Setup Instructions**

### 1. Clone the Repository
```bash
git clone <repository_url>
cd app
```

### 2. Build and Start Services
```bash
docker-compose up --build
```

### 3. Access Services
- **Streamlit Dashboard**: [http://localhost:8501](http://localhost:8501)
- **Flask Backend**: [http://localhost:5000](http://localhost:5000)
  - `/metrics`: Real-time metrics.
  - `/flagged-customers`: Flagged customer data.

---

## **File Details**

- **`producer.py`**: Kafka producer script for sending batched data to Kafka.
- **`flagging_consumer.py`**: Consumer script for flagging high-risk customers.
- **`retrain_consumer.py`**: Consumer script for retraining machine learning models.
- **`flask_backend/app.py`**: Flask backend for metrics and flagged customer data.
- **`streamlit_frontend/dashboard.py`**: Streamlit app for visualizing metrics and flagged customers.

---

## **Shared Resources**

- **Models (`Models/`)**:
  - Contains machine learning models (`RFModel.pkl` and `LRModel.pkl`) shared between consumers.

- **Data (`Data/`)**:
  - Stores flagged customer data (`high_risk_data.csv`).

---

## **Usage**

### Monitor Real-Time Metrics
1. Run the Streamlit dashboard.
2. View:
   - **Number of batches sent by the producer**.
   - **Number of batches processed by each consumer**.
   - **Bar chart of flagged customers over time**.

---

## **Environment Variables**

You can override the default configuration (e.g., Kafka or Redis hosts) using environment variables in `docker-compose.yml`:

- `REDIS_HOST`: Redis host (default: `localhost`).
- `KAFKA_HOST`: Kafka host (default: `localhost`).

---

## **Stopping Services**

To stop all services:
```bash
docker-compose down
```

---

## **Future Enhancements**

- Add a database (e.g., PostgreSQL) to replace the shared CSV file for better scalability.
- Improve the model retraining pipeline with asynchronous processing.
- Extend the dashboard to include additional metrics and visualization options.

---

## **Contributing**

Contributions are welcome! Feel free to open issues or submit pull requests.

---

## **License**

This project is licensed under the MIT License. See the `LICENSE` file for details.

--- 

Let me know if you need further refinements!