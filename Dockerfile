FROM python:3.10-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends gnupg wget curl unzip && \
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
