# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install necessary packages for Selenium and the browser
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    libgtk-3-0 \
    libdbus-glib-1-2 \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft Edge stable for Linux
RUN wget -q https://packages.microsoft.com/keys/microsoft.asc -O- | apt-key add - \
    && echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge.list \
    && apt-get update \
    && apt-get install -y microsoft-edge-stable

# Download and install msedgedriver (Linux version)
# Replace <VERSION> with the version that matches your installed Edge version
RUN wget -O /tmp/edgedriver.zip https://msedgedriver.azureedge.net/134.0.3124.85/edgedriver_linux64.zip \
    && unzip /tmp/edgedriver.zip -d /usr/local/bin/ \
    && chmod +x /usr/local/bin/msedgedriver \
    && rm /tmp/edgedriver.zip

# Set working directory
WORKDIR /app

# Copy and install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app

# Expose the port your Flask app is using (in your case, 50)
EXPOSE 50

# Run the Flask app
CMD ["python", "test.py"]
