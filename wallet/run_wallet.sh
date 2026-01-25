#!/bin/bash

set -x

export WALLET_PATH=/data/wallet

# Create new wallet if it doesn't exist
if [[ ! -f $WALLET_PATH ]]; then
  echo -e "[+] Wallet does not yet exist. Creating it!"
  monero-wallet-cli \
    --generate-from-view-key ${WALLET_PATH} \
    --daemon-address ${WALLET_DAEMON_ADDRESS} \
    --trusted-daemon \
    --password ${WALLET_PASSWORD} << EOF
$WALLET_ADDRESS
$WALLET_VIEW_KEY
$WALLET_RESTORE_HEIGHT
EOF
fi

# Run RPC wallet
echo -e "[+] Running RPC wallet!"
monero-wallet-rpc \
  --daemon-address ${WALLET_DAEMON_ADDRESS} \
  --wallet-file ${WALLET_PATH} \
  --password $WALLET_PASSWORD \
  --rpc-login "$WALLET_RPC_USERNAME:$WALLET_RPC_PASSWORD" \
  --rpc-bind-port $WALLET_RPC_PORT \
  --rpc-bind-ip 0.0.0.0 \
  --confirm-external-bind \
  --log-file ${WALLET_PATH}-rpc.log \
  --trusted-daemon
