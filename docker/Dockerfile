# Use a lightweight, minimal Python image
FROM python:3.10-alpine

# Install testing dependencies
RUN pip install --no-cache-dir pytest==8.0.0 pytest-cov==5.0.0

# Set the working directory inside the container
WORKDIR /sandbox

# The container will act exactly like the pytest command line tool
ENTRYPOINT ["python", "-m", "pytest"]