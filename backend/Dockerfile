# Start with a base image containing Python runtime
FROM python:3.11.4-slim-bookworm

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Upgrade pip to the latest available version and Install GNU Compiler Collection (GCC), Postgres client
RUN python -m pip install --upgrade pip && \
    apt-get update && \
    apt-get install -y gcc postgresql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install any needed packages specified in requirements.txt
RUN pip install -r requirements.txt

# Make port 80 and 443 available to the world outside this container
EXPOSE 80 443

# Start NGINX and Gunicorn
RUN chmod +x /app/server/start.sh
RUN chmod +x /app/server/start_secure.sh
