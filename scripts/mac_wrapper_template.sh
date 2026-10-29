#!/bin/bash
# Run a command on the user's Mac over SSH through the Tailscale tunnel proxy.
# Render with render_installer.py, then call it as: mac '<remote command>'
exec ssh -o BatchMode=yes -o ConnectTimeout=30 \
  -o ProxyCommand="python3 __PROXY_CONNECT_PATH__ %h %p" \
  -i ~/.ssh/id_ed25519 \
  __MAC_USER__@__MAC_HOST__ "$@"
