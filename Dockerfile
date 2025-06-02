
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg wget curl unzip && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Check Chrome version before install (should not be found)
RUN echo "Chrome BEFORE install:" && (google-chrome --version || echo "not installed")

# Add Google Chrome repo and install Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google.list && \
    apt-get update -y && \
    apt-get install -y --no-install-recommends google-chrome-stable && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /var/cache/apt/*

# Check Chrome version after install
RUN echo "Chrome AFTER install:" && google-chrome --version

# Install matching ChromeDriver (for Chrome for Testing)
# Install Chromedriver (for Chrome for Testing)
RUN CHROME_VERSION=$(google-chrome --product-version) && \
    wget -q --continue -P /tmp "https://edgedl.me.gvt1.com/edgedl/chrome/chrome-for-testing/$CHROME_VERSION/linux64/chromedriver-linux64.zip" && \
    unzip /tmp/chromedriver-linux64.zip -d /tmp/ && \
    mv /tmp/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver && \
    chmod +x /usr/local/bin/chromedriver && \
    rm -rf /tmp/chromedriver-linux64 /tmp/chromedriver-linux64.zip


# Check Chromedriver version
RUN echo "Chromedriver version:" && chromedriver --version

# (Optional) Set environment variables for Selenium
ENV CHROME_BIN=/usr/bin/google-chrome
ENV CHROMEDRIVER_BIN=/usr/local/bin/chromedriver

# (Optional) Default command
CMD ["google-chrome", "--version"]

# Copy only the requirements file first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Set environment variables for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production  # Use 'development' for debugging

# Expose the port Flask runs on (default: 5000)
EXPOSE 5002

# Command to run the application using Gunicorn (production)
CMD ["gunicorn", "--bind", "0.0.0.0:5002", "app:app"]


