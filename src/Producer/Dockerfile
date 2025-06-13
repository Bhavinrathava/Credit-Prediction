# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY producer.py .
COPY Data/german_credit_data.csv ./Data/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose ports (if needed for debugging or monitoring)
EXPOSE 9092

# Command to run the Kafka producer script
CMD ["python", "producer.py"]
