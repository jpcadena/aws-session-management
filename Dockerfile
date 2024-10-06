# syntax=docker/dockerfile:1

# Comments are provided throughout this file to help you get started.
# If you need more help, visit the Dockerfile reference guide at
# https://docs.docker.com/engine/reference/builder/

# Stage 1: Build Stage
# Use a Python image and specify a non-root user.
ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION} AS base
ARG UID=10001

# Create a non-privileged user and set permissions
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser && \
    mkdir -p /aws-session-management && \
    mkdir -p /home/appuser && \
    chown -R appuser:appuser /aws-session-management /home/appuser

# Set recommended Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Use the non-privileged user
USER appuser

# Set working directory and permissions
WORKDIR /aws-session-management

LABEL description="This text illustrates \
    that label-values can span multiple lines."
LABEL maintainer="jpcadena@espol.edu.ec"

# Stage for installing dependencies
FROM base AS builder
ARG UID=10001

# Switch back to root to install dependencies
USER root

# Upgrade pip and install Poetry
RUN python -m pip install --upgrade pip && \
    pip install poetry==1.5.1

# Copy only the necessary files for installing dependencies
COPY pyproject.toml poetry.lock* /tmp/
WORKDIR /tmp

# Remove python-magic-bin and export other dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Production Stage
FROM base AS production

# Switch back to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update -y && \
    apt-get install -qy --no-install-recommends \
    # List your system dependencies here, for example:
    build-essential \
    libpq-dev \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy over requirements and install Python packages
COPY --from=builder /tmp/requirements.txt /aws-session-management/
RUN pip install --no-cache-dir -r /aws-session-management/requirements.txt

# Copy source code
COPY . /aws-session-management

# Revert to non-privileged user
USER appuser

# Expose port
EXPOSE 8080

# Run the application
# syntax=docker/dockerfile:1

ARG PYTHON_VERSION=3.12.7
FROM python:${PYTHON_VERSION} AS base_stage

# Create a non-privileged user and set permissions
RUN adduser --disabled-password --gecos "" appuser && mkdir -p /aws-session-management && chown -R appuser:appuser /aws-session-management

# Set recommended Python environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Use the non-privileged user
USER appuser

# Set working directory and permissions
WORKDIR /aws-session-management

# Install dependencies
FROM base_stage AS builder_stage

# Install Poetry
RUN python -m pip install --upgrade pip && pip install poetry==1.5.1

# Ensure that the local bin directory is in the PATH
ENV PATH="/home/appuser/.local/bin:$PATH"

# Copy only the necessary files for installing dependencies
COPY pyproject.toml poetry.lock* /tmp/
WORKDIR /tmp

# Remove python-magic-bin and export other dependencies to requirements.txt
RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# Production Stage
FROM base_stage AS production_stage

# Switch back to root to install system dependencies
USER root

# Install system dependencies
RUN apt-get update -y && apt-get install -qy --no-install-recommends && rm -rf /var/lib/apt/lists/*

# Copy over requirements and install Python packages
COPY --from=builder_stage /tmp/requirements.txt /aws-session-management/
RUN pip install --no-cache-dir -r /aws-session-management/requirements.txt

# Copy source code
COPY . /aws-session-management

# Revert to non-privileged user
USER appuser

# Expose port
EXPOSE 8080

# Run the application with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--proxy-headers"]
