FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies for ffmpeg and audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --progress-bar=off -r requirements.txt

# Copy application code
COPY app.py .
COPY scripts/ l/scripts/

# Expose Gradio port
EXPOSE 7860

# Run the application with uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
