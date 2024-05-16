# Use Heroku's Python Buildpack
FROM heroku/python

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy bot code and configuration
COPY AuctionBot/ ./AuctionBot/
COPY Dockerfile .
COPY app.json .

# Start the bot
CMD ["python3", "-m", "AuctionBot.main"]
