# Dockerfile for Ethical Riemann Hypothesis
# Multi-stage build for production deployment

FROM python:3.10-slim as base

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose ports
# 8888 for Jupyter, 8501 for Streamlit, 7860 for Gradio
EXPOSE 8888 8501 7860

# Default command (can be overridden)
CMD ["python", "-m", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]

