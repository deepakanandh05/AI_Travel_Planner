# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Make port available to the world outside this container
# Render will set PORT environment variable dynamically
EXPOSE 8000

# Define environment variable (can be overridden by Render)
ENV PORT=8000

# Run app.py when the container launches
# Use $PORT to read from environment variable
CMD uvicorn main:app --host 0.0.0.0 --port $PORT
