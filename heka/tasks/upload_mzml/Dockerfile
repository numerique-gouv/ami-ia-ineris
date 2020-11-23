# Base image
FROM python:3.8-slim-buster

# Copy requirements to /home in the container
COPY requirements /home/requirements

# Install requirements
RUN pip install -r /home/requirements/requirements.txt

# Copy script to /home
COPY src/uplaod_mzml.py /home/uplaod_mzml.py
COPY src/queries.py /home/queries.py


# Set entrypoint
ENTRYPOINT [ "python", "/home/uplaod_mzml.py" ]
