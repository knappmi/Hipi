FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app.py .

# Expose API port
EXPOSE 8000

# Run the plugin
CMD ["python", "app.py"]



