# Use the official Python image as the base image
FROM python:3.10-slim

# Set environment variables to prevent writing .pyc files and to ensure unbuffered output
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y build-essential libpq-dev nano

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Install gunicorn
RUN pip install --no-cache-dir gunicorn

# Copy the Django project files
COPY . /app/

RUN python manage.py collectstatic --noinput

RUN apt-get update && apt-get install -y nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose the port your Django app will run on
EXPOSE 8000

# Run the application using Gunicorn
CMD service nginx start && gunicorn sellout.wsgi:application --bind 0.0.0.0:8000 --threads 10
