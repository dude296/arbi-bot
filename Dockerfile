# Use Python 3.11.9 base image
FROM python:3.11.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y gcc build-essential && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Start the bot
CMD ["python", "arbi_bot.py"]
