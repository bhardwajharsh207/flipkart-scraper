FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y wget unzip xvfb libxi6 libgconf-2-4 libnss3 libxss1 libappindicator1 libindicator7 libgbm1 fonts-liberation libasound2 libatk-bridge2.0-0 libgtk-3-0 libxcomposite1 libxcursor1 libxdamage1 libxrandr2 libu2f-udev && \
    rm -rf /var/lib/apt/lists/*

# Install Chrome
RUN wget -O /tmp/chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get update && \
    apt-get install -y /tmp/chrome.deb && \
    rm /tmp/chrome.deb

# Install Chromedriver
RUN CHROME_VERSION=$(google-chrome --version | awk '{print $3}') && \
    CHROMEDRIVER_VERSION=$(curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE_${CHROME_VERSION%.*}) && \
    wget -O /tmp/chromedriver.zip https://chromedriver.storage.googleapis.com/${CHROMEDRIVER_VERSION}/chromedriver_linux64.zip && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    rm /tmp/chromedriver.zip && \
    chmod +x /usr/local/bin/chromedriver

# Set Chrome and Chromedriver in PATH
ENV PATH="/usr/local/bin:$PATH"
ENV CHROME_BIN="/usr/bin/google-chrome"
ENV CHROMEDRIVER_BIN="/usr/local/bin/chromedriver"

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app code
COPY . .

# Expose port (if using Flask default)
EXPOSE 5000

# Start your app
CMD ["python", "app.py"]
