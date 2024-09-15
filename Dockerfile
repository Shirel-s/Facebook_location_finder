# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY  . /app

# Install the required dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Make the port 5000 available to the outside world
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=development

# Run the application
CMD ["flask", "run", "--host=0.0.0.0"]