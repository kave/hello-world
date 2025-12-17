#syntax=docker/dockerfile:1

FROM dhi.io/python:3.13-alpine3.22

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt /app/

# Install Python dependencies
RUN ["pip", "install", "--no-cache-dir", "-r", "/app/requirements.txt"]

# Copy application code
COPY . .

# Set logo path as build argument and environment variable
ARG LOGO_PATH=../static/img/logo.png
ENV LOGO_PATH=${LOGO_PATH}

# Use non-root user by default in DHI
USER nonroot

CMD ["python", "-u", "main.py"]