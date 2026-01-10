FROM ubuntu@sha256:c35e29c9450151419d9448b0fd75374fec4fff364a27f176fb458d472dfc9e54

RUN apt-get update -y
RUN apt-get install -y python3 python3-venv adduser
RUN adduser \
   --system \
   --shell /bin/bash \
   --gecos 'lwsadmin' \
   --group \
   --disabled-password \
   --home /srv/lwsadmin \
   lwsadmin
WORKDIR /srv/lwsadmin
USER lwsadmin
COPY --chown=lwsadmin:lwsadmin requirements.txt .
RUN mkdir data
RUN python3 -m venv .venv
RUN .venv/bin/pip install -r requirements.txt
COPY --chown=lwsadmin:lwsadmin lws lws
COPY --chown=lwsadmin:lwsadmin app.py .
ENTRYPOINT [".venv/bin/quart", "run"]