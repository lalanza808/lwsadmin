FROM ubuntu@sha256:c35e29c9450151419d9448b0fd75374fec4fff364a27f176fb458d472dfc9e54

RUN apt-get update -y
RUN apt-get install -y python3 python3-venv adduser curl
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
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/
COPY --chown=lwsadmin:lwsadmin pyproject.toml uv.lock ./
RUN mkdir data
RUN uv sync --frozen --no-dev
COPY --chown=lwsadmin:lwsadmin lws lws
COPY --chown=lwsadmin:lwsadmin app.py .
ENTRYPOINT ["uv", "run", "--frozen", "quart", "run"]
