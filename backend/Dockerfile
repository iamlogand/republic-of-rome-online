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

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Install postgresql-client
RUN apt-get update && apt-get install -y postgresql-client

# Start Gunicorn with the WSGI application
CMD ["gunicorn", "rorsite.wsgi:application", "--bind", "0.0.0.0:8000"]
