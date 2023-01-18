# Base image
FROM python:3.8-slim-buster

# Copy requirements to /home in the container
COPY requirements /home/requirements

# Install requirements
RUN pip install -r /home/requirements/requirements.txt

# Copy script to /home
COPY src/pmf_profiles.xlsx /home/pmf_profiles.xlsx
COPY src/compute_score.py /home/compute_score.py

# Set entrypoint
ENTRYPOINT [ "python", "/home/compute_score.py" ]
