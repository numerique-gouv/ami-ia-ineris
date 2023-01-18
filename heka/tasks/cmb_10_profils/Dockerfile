# Base image
FROM python:3.8-slim-buster

# Copy requirements to /home in the container
COPY requirements /home/requirements

# Install requirements
RUN pip install -r /home/requirements/requirements.txt

# Copy script to /home
COPY src/rum_cmb_10_profils.py /home/rum_cmb_10_profils.py
COPY src/pmf_profiles.xlsx /home/pmf_profiles.xlsx

# Set entrypoint
ENTRYPOINT [ "python", "/home/rum_cmb_10_profils.py" ]
