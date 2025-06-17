# Use official Python 3.11.9 base image (slim variant)
FROM python:3.11.9-slim

# Install system dependencies required to build Python packages (e.g. pycosat)
RUN apt-get update && \
    apt-get install -y gcc build-essential && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory inside the container
WORKDIR /app

# Copy all files from the project directory into the container
COPY . .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Set default command to run your bot
CMD ["python", "arbi_bot.py"]
