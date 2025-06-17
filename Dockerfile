# Use Python 3.11.9 base image
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy all files
COPY . .

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Start the bot
CMD ["python", "arbi_bot.py"]
