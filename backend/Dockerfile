# Start with a base image containing Python runtime
FROM python:3.8-slim-buster

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container to /app
WORKDIR /app

# Add the current directory contents into the container at /app
ADD . /app

# Upgrade pip to the latest available version
RUN python -m pip install --upgrade pip

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Collect static files
RUN python manage.py collectstatic --no-input

# Make port 80 and 443 available to the world outside this container
EXPOSE 80 443

# Install postgresql-client
RUN apt-get update && apt-get install -y postgresql-client

# Install AWS CLI
RUN apt-get update && \
    apt-get install -y curl unzip && \
    curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && \
    unzip awscliv2.zip && \
    ./aws/install

# Start NGINX and Gunicorn
RUN chmod +x /app/server/start.sh
RUN chmod +x /app/server/start_secure.sh
CMD ["/app/server/start_secure.sh"]
