# Muse Terminal Connector

## Know the shape of the problem

- Treat the paired Mac app channel as file and screen access only, because it has no shell or program runner and it always skips Terminal and scripting apps.

- Route SSH through the Tailscale tunnel instead, because the tunnel carries plain TCP and the docs for it name SSH as a covered service once an address is approved.

- Never test SSH through the standard egress proxy port 3128, because that proxy kills the SSH protocol before authentication and the failure looks like a Mac problem when it is a proxy problem.

- Swap the runtime proxy port to 3130 for every tailnet connection, because 3130 is the Tailscale tunnel port and 3128 is general web egress.

- Read `~/docs/devices/tailscale.md` before the first connection attempt, because the approval model and the one address rule in that doc decide whether the test works at all.

## Gather the values first

- Read the Mac user name, home folder and macOS version with the paired device environment command before writing anything.

- Run `/opt/hatch/bin/tailscale status` on this computer and record the VM tailnet IPv4 and the Mac peer name and IPv4.

- Read the VM public key at `~/.ssh/id_ed25519.pub` and create the key pair with `ssh-keygen` only when it is missing.

- Confirm both machines sit on the same tailnet before preparing the installer, because the whole route depends on that shared network and no other inbound path is opened.

## Explain the risk and lock the defaults

- Tell the user plainly that Remote Login opens an SSH listener on the Mac and that a key given to this VM is full shell access as their user if the VM is ever compromised.

- Get an explicit yes for the hardened setup before preparing any file, because the convenience is permanent while the consent moment is short.

- Default to key-only login with password and keyboard interactive authentication off, root login off, forwarding and X11 off, and at most 3 authentication tries.

- Restrict the login to one account and one source with an `AllowUsers` line in the form `user@<VM tailnet IPv4>`, because that one line stops every other machine on the LAN and the tailnet from even trying the key.

- Name the three revocation paths up front, which are turning Remote Login off, deleting the key line from `~/.ssh/authorized_keys` on the Mac, and deleting the sshd drop-in config.

## Prepare the Mac with one user-run installer

- Render the installer from `scripts/installer_template.command` with `scripts/render_installer.py`, because the template carries placeholders for the public key blob, the Mac user name and the VM tailnet IPv4 and hand editing invites silent mistakes.

- Keep the installer idempotent so a second run skips an existing key, backs up an existing drop-in config and ends in the same state.

- Generate the SSH host keys with `ssh-keygen -A` before running any `sshd -t` validation, because a Mac that never served SSH has no host keys and the validation fails with a misleading no hostkeys error even when the config is right.

- Validate the rendered config with `sshd -t` before enabling Remote Login and roll the drop-in back out on any validation error, because a broken sshd config left in place can lock the user out of a service they may use themselves.

- Log the whole install to a file in the Mac Downloads folder and end the log with a clear done marker, because the agent reads that log through the file channel instead of trusting the user report alone.

- Verify the byte count of the installer after writing it to the Mac, because the file channel confirms a write and the count is the cheapest proof that the content arrived whole.

- Ask the user to run the installer from Terminal with `zsh ~/Downloads/<installer name>` rather than a double click, because files written through the device channel arrive without the execute bit and a double click fails with a privileges warning.

- Expect one admin password prompt inside that Terminal window, because every system change in the installer goes through `sudo` and the user types that password on the Mac, never in chat.

## Connect from this computer

- Connect with the helper in `scripts/proxy_connect.py` as the ssh `ProxyCommand`, because plain ssh cannot reach tailnet addresses and the helper performs the HTTP CONNECT through the tunnel proxy on port 3130.

- Prefer the Mac MagicDNS name as the ssh target when it was already approved for another service, because an approval covers later TCP services on that exact name while a fresh name or IP needs its own approval.

- Keep `StrictHostKeyChecking` at `accept-new` for the first connection and leave the recorded host key in place afterwards, because a changed host key after that point is a real warning sign.

- Use the wrapper pattern in `scripts/mac_wrapper_template.sh` for repeat work, because one short command with the proxy and key baked in removes a whole class of flag typos.

## Verify end to end before claiming success

- Run a harmless identity command first and report what came back, such as the Mac hostname, the user name and the macOS version.

- Run one harmless write and delete in the Mac home folder, because a login that cannot write proves less than the user needs from this setup.

- Run one deliberate password authentication attempt with public key disabled and confirm it is rejected with a publickey only error, because the hardened promise is only real when the weak path is seen to fail.

- Read the effective server config with `sshd -T` from the installer log and match it against the promised defaults line by line.

- Treat a 502 or a closed connection during early tunnel tests as proxy evidence rather than Mac evidence, and check which proxy port the attempt used before changing anything on the Mac.

## Grant Full Disk Access for protected folders

- Expect `~/Downloads`, `~/Documents` and `~/Desktop` to refuse SSH reads with an operation not permitted error until the user grants Full Disk Access, because macOS TCC treats an SSH session as its own client.

- Grant the access to `/usr/libexec/sshd-keygen-wrapper`, because that wrapper is the process macOS attributes SSH sessions to and granting it covers every later connection.

- Open the right settings pane from the SSH session with the `x-apple.systempreferences` Privacy All Files URL and copy the wrapper path to the Mac clipboard with `pbcopy`, because the user then needs only the add button, the path paste and their own authentication.

- Leave the add and authenticate clicks to the user, because macOS requires the owner for this grant and no agent channel can or should supply that password.

- Retest the three protected folders over SSH right after the grant and report the real listing or the real error.

## Revoke and troubleshoot

- Reverse the setup in the order the user asks for, from the lightest step of removing the key line to the full stop of turning Remote Login off and deleting the drop-in config.

- Check the proxy port first when a connection dies before authentication, because 3128 in any error line means the attempt never used the Tailscale tunnel.

- Check the VM tailnet IPv4 against the `AllowUsers` line when a valid key is suddenly refused, because a re-enrolled VM can return with a new address and the restriction then blocks the intended client too.

- Check host keys when the installer validation fails on a fresh Mac, and check TCC when only the protected folders refuse while the rest of the home folder works.

- Treat the systemsetup Full Disk Access warning during install as noise when the follow up check reports Remote Login on and the live SSH test passes, because the toggle can succeed through the launch daemon path while that one message still prints.

## Available connectors

- Use `muse.connector_search` to find other connectors and `muse.skill_search` to find related skills.

- If nothing here fits, look on the web for a maintained API or MCP server and set it up with [Custom Connectors and MCPs](/opt/muse/skills/custom-connector-setup/SKILL.md), or build a custom connector.
