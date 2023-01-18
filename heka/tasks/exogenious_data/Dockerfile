# Base image
FROM python:3.8-slim-buster

# Copy requirements to /home in the container
COPY requirements /home/requirements

# Install requirements
RUN pip install -r /home/requirements/requirements.txt

# Copy script to /home
COPY src/get_data.py /home/get_data.py

# Set entrypoint
ENTRYPOINT [ "python", "/home/get_data.py" ]
