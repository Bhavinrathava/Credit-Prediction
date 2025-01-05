# Use a lightweight Python image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY retrain_consumer.py .
COPY main.py .
COPY Models/ ./Models/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose any necessary ports (not needed for this consumer)
# No ports exposed since the consumer interacts with Kafka and Redis internally

# Command to run the Kafka consumer script
CMD ["python", "retrain_consumer.py"]
