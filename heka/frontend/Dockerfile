FROM python:3.7

RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-sdk -y

RUN apt-get update -q && apt-get install -y --no-install-recommends -qq \
    jq \
  && rm -rf /var/lib/apt/lists/*

EXPOSE 80

COPY requirements.txt .
RUN if [ -f "requirements.txt" ]; then \
  pip3 install -r requirements.txt; fi

COPY src/ /heka/frontend

ENTRYPOINT [ "gunicorn" ]
CMD [ "--workers", "3", "-b", ":80", "--preload", "--chdir", "/heka/frontend", "app:server" ]
