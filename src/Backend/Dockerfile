# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory inside the container
WORKDIR /app

# Copy the necessary files into the container
COPY app.py .
COPY Data/high_risk_data.csv ./Data/
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port the Flask app runs on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "app.py"]
