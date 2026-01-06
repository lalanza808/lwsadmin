#!/bin/bash

set -x

export RPC_CREDS="${1}"
export DAEMON_ADDRESS="${2}"
export WALLET_FILE=/data/wallet

# Create new wallet if it doesn't exist
if [[ ! -d ${WALLET_FILE} ]]; then
  monero-wallet-cli \
    --generate-new-wallet ${WALLET_FILE} \
    --daemon-address ${DAEMON_ADDRESS} \
    --trusted-daemon \
    --use-english-language-names \
    --mnemonic-language English
fi

# Run RPC wallet
monero-wallet-rpc \
  --daemon-address ${DAEMON_ADDRESS} \
  --wallet-file ${WALLET_FILE} \
  --password "" \
  --rpc-login "${RPC_CREDS}" \
  --rpc-bind-port 8000 \
  --rpc-bind-ip 0.0.0.0 \
  --confirm-external-bind \
  --log-file ${WALLET_FILE}-rpc.log \
  --trusted-daemon