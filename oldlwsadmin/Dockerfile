FROM ubuntu:22.04

RUN apt-get update -y
RUN apt-get install -y python3 python3-venv
WORKDIR /srv/lwsadmin
RUN adduser \
   --system \
   --shell /bin/bash \
   --gecos 'lwsadmin' \
   --group \
   --disabled-password \
   --home /srv/lwsadmin \
   --uid 1000 \
   lwsadmin
COPY . .
RUN chown -R lwsadmin:lwsadmin .
USER lwsadmin
RUN python3 -m venv .venv
RUN .venv/bin/pip install poetry
RUN .venv/bin/poetry install