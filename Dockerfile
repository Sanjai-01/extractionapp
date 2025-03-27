FROM python:3.12-bullseye

# Install required dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    unzip \
    xvfb \
    libnss3 \
    libxss1 \
    libappindicator3-1 \
    fonts-liberation \
    libasound2 \
    libgbm1 \
    libgtk-3-0 \
    libu2f-udev \
    gnupg \
    libglib2.0-0 \
    libgconf-2-4 \
    libfontconfig1 \
    libx11-xcb1 \
    && rm -rf /var/lib/apt/lists/*

# Install Microsoft Edge version 134.0.3124.85
RUN curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | gpg --dearmor > /usr/share/keyrings/microsoft.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft.gpg] https://packages.microsoft.com/repos/edge stable main" \
    > /etc/apt/sources.list.d/microsoft-edge.list && \
    apt-get update && \
    apt-get install -y microsoft-edge-stable=134.0.3124.85-1

# Copy msedgedriver.exe from the local machine to the container
COPY msedgedriver.exe /usr/local/bin/msedgedriver
RUN chmod 755 /usr/local/bin/msedgedriver

# Verify the driver is copied correctly
RUN ls -l /usr/local/bin

# Set the working directory inside the container
WORKDIR /app

# Copy application files from the local machine to the container
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose the port that the Flask app will run on
EXPOSE 5000

# Command to run the Flask app
CMD ["python", "test.py"]