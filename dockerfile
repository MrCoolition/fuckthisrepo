FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    zlib1g-dev \
    libjpeg-dev \
    libpng-dev \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the rest of your application code
COPY . .

# Expose port (if necessary)
EXPOSE 8501

# Run the application
CMD ["streamlit", "run", "PledgeBot.py"]
