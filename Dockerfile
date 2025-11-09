# syntax=docker/dockerfile:1

FROM python:3.11

# Set working directory inside the container
WORKDIR /code

# Copy and install dependencies
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# ✅ Cloud Run expects the container to listen on port 8080
EXPOSE 8080

# ✅ Start Flask app via Gunicorn on port 8080
ENTRYPOINT ["gunicorn", "-b", ":8080", "app:app"]
