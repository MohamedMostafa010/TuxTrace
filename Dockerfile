# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /usr/src/app

# Install necessary packages including sudo and user management tools
RUN apt-get update && apt-get install -y \
    bash \
    curl \
    vim \
    procps \
    libreadline-dev \
    sudo \
    passwd \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application
COPY . .

# Make the script executable
RUN chmod +x TuxTrace.py

# Set proper terminal environment
ENV TERM=xterm-256color
ENV PYTHONUNBUFFERED=1

# Run as root by default (since we're in a container anyway)
USER root

# Use a shell as entrypoint for better terminal handling
ENTRYPOINT ["/bin/bash", "-c"]
CMD ["./TuxTrace.py"]