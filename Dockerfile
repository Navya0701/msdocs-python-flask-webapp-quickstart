# syntax=docker/dockerfile:1

FROM python:3.11

# Set working directory inside the container
WORKDIR /code

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the app
COPY . .

# Cloud Run listens on port 8080
EXPOSE 8080

# Start the Flask app using Gunicorn, binding to port 8080
ENTRYPOINT ["gunicorn", "-b", ":8080", "app:app"]
