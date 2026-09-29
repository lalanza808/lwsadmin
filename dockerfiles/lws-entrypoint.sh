#!/bin/bash

set -ex

mkdir -p /data

if [[ ! -f /data/credentials.json ]]; then
    monero-lws-admin create_admin > /data/credentials.json
fi

monero-lws-daemon \
    --scan-threads ${SCAN_THREADS:-4} \
    --rest-threads ${REST_THREADS:-2} \
    --rest-server ${REST_SERVER:-http://127.0.0.1:8080} \
    --admin-rest-server ${ADMIN_REST_SERVER:-http://127.0.0.1:8081} \
    --log-level ${LOG_LEVEL:-1} \
    --daemon ${DAEMON_ZMQ_PUB:-tcp://127.0.0.1:18082} \
    --sub ${DAEMON_ZMQ_SUB:-tcp://127.0.0.1:18083} \
    --access-control-origin "${CORS:-\*}" \
    --auto-accept-creation \
    --auto-accept-import \
    --max-subaddresses ${MAX_SUBADDRESS:-200}
