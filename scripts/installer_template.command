#!/bin/zsh
# Cai SSH siet chat cho Muse - chi key, chi user __MAC_USER__, chi tu IP Tailscale cua Muse VM
# Chay 1 lan tren Mac. Se hoi mat khau admin (sudo) 1 lan.
set -u

LOG="$HOME/Downloads/cai-ssh-muse.log"
PUBKEY_BLOB="__PUBKEY_BLOB__"
PUBKEY_LINE="ssh-ed25519 $PUBKEY_BLOB muse-vm"
DROPIN="/etc/ssh/sshd_config.d/100-muse-hardened.conf"

exec > >(tee -a "$LOG") 2>&1
echo ""
echo "=== Cai SSH cho Muse - $(date) ==="
echo "Trang thai Remote Login TRUOC:"
/usr/sbin/systemsetup -getremotelogin 2>/dev/null || echo "(khong doc duoc)"

# ---------- 1. authorized_keys (khong can sudo) ----------
echo ""
echo "[1/4] Them khoa cong khai cua Muse vao ~/.ssh/authorized_keys ..."
mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"
touch "$HOME/.ssh/authorized_keys"
chmod 600 "$HOME/.ssh/authorized_keys"
if grep -q "$PUBKEY_BLOB" "$HOME/.ssh/authorized_keys"; then
  echo "  -> Key da co san, bo qua."
else
  echo "$PUBKEY_LINE" >> "$HOME/.ssh/authorized_keys"
  echo "  -> Da them key."
fi

# ---------- 2. Cau hinh sshd siet chat (can sudo) ----------
echo ""
echo "[2/4] Ghi cau hinh sshd siet chat (se hoi mat khau admin cua Mac)..."
sudo -v || { echo "LOI: sudo that bai. Dung lai."; echo "Nhan Enter de dong..."; read -r; exit 1; }

sudo mkdir -p /etc/ssh/sshd_config.d
if [ -f "$DROPIN" ]; then
  sudo cp "$DROPIN" "$DROPIN.bak-$(date +%Y%m%d%H%M%S)"
  echo "  -> Da backup cau hinh cu."
fi

sudo tee "$DROPIN" > /dev/null <<'EOF'
# Muse hardened SSH (2026-10-29) - key-only, 1 user, 1 nguon Tailscale
PasswordAuthentication no
KbdInteractiveAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
AllowUsers __MAC_USER__@__VM_TAILNET_IP__
X11Forwarding no
AllowAgentForwarding no
AllowTcpForwarding no
MaxAuthTries 3
EOF
echo "  -> Da ghi $DROPIN"

# Host keys PHAI tao truoc: thieu host key thi sshd -t bao loi du cau hinh dung (da gap 15:17)
sudo /usr/bin/ssh-keygen -A >/dev/null 2>&1 || true
echo "  -> Da tao/kiem tra host keys."

# Kiem tra cu phap cau hinh truoc khi bat
echo ""
echo "[3/4] Kiem tra cau hinh + bat Remote Login..."
if ! sudo /usr/sbin/sshd -t; then
  echo "LOI: sshd -t bao cau hinh sai. Dang go cau hinh vua ghi de tranh loi he thong..."
  sudo rm -f "$DROPIN"
  echo "Da go $DROPIN. Bao lai cho Muse."
  echo "Nhan Enter de dong..."; read -r; exit 1
fi
echo "  -> Cau hinh hop le."

# Bat Remote Login
sudo /usr/sbin/systemsetup -f -setremotelogin on 2>/dev/null || sudo /usr/sbin/systemsetup -setremotelogin on
sudo launchctl load -w /System/Library/LaunchDaemons/ssh.plist 2>/dev/null || true
sleep 2

# ---------- 4. Kiem chung ----------
echo ""
echo "[4/4] Kiem chung:"
echo "Trang thai Remote Login SAU:"
sudo /usr/sbin/systemsetup -getremotelogin 2>/dev/null || echo "(khong doc duoc)"
echo ""
echo "Cau hinh sshd thuc te (sshd -T):"
sudo /usr/sbin/sshd -T -C user=__MAC_USER__,host=mac.local,addr=__VM_TAILNET_IP__ 2>/dev/null | grep -Ei '^(passwordauthentication|kbdinteractiveauthentication|pubkeyauthentication|permitrootlogin|allowusers|maxauthtries)' || echo "(khong doc duoc sshd -T)"
echo ""
echo "Cong 22 dang nghe:"
lsof -nP -iTCP:22 -sTCP:LISTEN 2>/dev/null || echo "(chua thay cong 22 - cho vai giay roi kiem tra lai)"

echo ""
echo "=== MUSE_SSH_SETUP_DONE ==="
echo "Xong. Quay lai bao cho Muse biet de Muse test SSH ngay."
echo "Nhan Enter de dong cua so nay..."
read -r
