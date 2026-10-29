#!/usr/bin/env python3
"""Render a template from this skill by filling its placeholders.

Works for installer_template.command and mac_wrapper_template.sh.

Placeholders:
  __PUBKEY_BLOB__       second field of the VM public key line
  __MAC_USER__          the Mac account user name
  __VM_TAILNET_IP__     the VM tailnet IPv4 (must sit in 100.64.0.0/10)
  __MAC_HOST__          the Mac MagicDNS name used as the ssh target
  __PROXY_CONNECT_PATH__  absolute path to proxy_connect.py on the VM

Examples:
  render_installer.py installer_template.command out.command \
      --pubkey-file ~/.ssh/id_ed25519.pub --mac-user alice --vm-ip 100.101.2.3

  render_installer.py mac_wrapper_template.sh mac \
      --mac-user alice --mac-host alices-mac.tail1234.ts.net \
      --proxy-path /home/hatch/workspace/mac-ssh/proxy_connect.py
"""
import argparse
import ipaddress
import re
import sys
from pathlib import Path

KNOWN = ["__PUBKEY_BLOB__", "__MAC_USER__", "__VM_TAILNET_IP__",
         "__MAC_HOST__", "__PROXY_CONNECT_PATH__"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("template")
    ap.add_argument("output")
    ap.add_argument("--pubkey-file", help="path to the VM .pub file")
    ap.add_argument("--pubkey", help="full public key line, as an alternative")
    ap.add_argument("--mac-user")
    ap.add_argument("--vm-ip")
    ap.add_argument("--mac-host")
    ap.add_argument("--proxy-path")
    args = ap.parse_args()

    values = {}
    if args.pubkey_file or args.pubkey:
        line = (Path(args.pubkey_file).read_text().strip()
                if args.pubkey_file else args.pubkey.strip())
        parts = line.split()
        if len(parts) < 2 or parts[0] not in ("ssh-ed25519", "ssh-rsa",
                                              "ecdsa-sha2-nistp256"):
            print("public key line looks wrong", file=sys.stderr)
            return 1
        if not re.fullmatch(r"[A-Za-z0-9+/=]+", parts[1]):
            print("public key blob has unexpected characters", file=sys.stderr)
            return 1
        values["__PUBKEY_BLOB__"] = parts[1]
    if args.mac_user:
        if not re.fullmatch(r"[a-z_][a-z0-9_-]*", args.mac_user):
            print("mac user name looks wrong", file=sys.stderr)
            return 1
        values["__MAC_USER__"] = args.mac_user
    if args.vm_ip:
        ip = ipaddress.ip_address(args.vm_ip)
        if ip not in ipaddress.ip_network("100.64.0.0/10"):
            print("vm ip is not a tailnet address in 100.64.0.0/10",
                  file=sys.stderr)
            return 1
        values["__VM_TAILNET_IP__"] = args.vm_ip
    if args.mac_host:
        values["__MAC_HOST__"] = args.mac_host
    if args.proxy_path:
        values["__PROXY_CONNECT_PATH__"] = args.proxy_path

    text = Path(args.template).read_text()
    needed = [ph for ph in KNOWN if ph in text]
    missing = [ph for ph in needed if ph not in values]
    if missing:
        print(f"missing values for placeholders: {', '.join(missing)}",
              file=sys.stderr)
        return 1
    for ph, val in values.items():
        text = text.replace(ph, val)
    leftovers = re.findall(r"__[A-Z_]+__", text)
    if leftovers:
        print(f"unfilled placeholders remain: {sorted(set(leftovers))}",
              file=sys.stderr)
        return 1

    out = Path(args.output)
    out.write_text(text)
    out.chmod(0o755)
    print(f"wrote {out} ({len(text.encode())} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
