# Base image
FROM python:3.8-slim-buster

# Copy requirements to /home in the container
COPY requirements /home/requirements

# Install requirements
RUN pip install -r /home/requirements/requirements.txt

# Copy script to /home
COPY src/run_cmb.py /home/run_cmb.py

# Set entrypoint
ENTRYPOINT [ "python", "/home/run_cmb.py" ]
