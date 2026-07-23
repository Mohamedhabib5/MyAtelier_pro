#!/usr/bin/env bash
# ==============================================================================
# MyAtelier Pro - Linux Host Environment Setup Script
# ==============================================================================
# This script prepares a Linux host (e.g. Linux Mint / Ubuntu) for running
# MyAtelier Pro on limited hardware (i3 4th Gen, 6GB RAM, SSD).
# It configures:
#   1. A 4GB Swap file on SSD with swappiness=10
#   2. Increased max open files limits
#   3. Systemd service auto-start for docker-compose
# ==============================================================================

set -e

echo "=== [1/4] Checking Swap File Configuration ==="
SWAP_PATH="/swapfile"
SWAP_SIZE_GB=4

if free | grep -i swap | grep -v 0 > /dev/null; then
    echo "[+] Active Swap is detected:"
    free -h
else
    echo "[!] No active Swap detected. Creating a ${SWAP_SIZE_GB}GB Swap file on SSD..."
    if [ -f "$SWAP_PATH" ]; then
        echo "[*] Swapfile exists at $SWAP_PATH but is not active. Activating..."
    else
        sudo fallocate -l ${SWAP_SIZE_GB}G $SWAP_PATH || sudo dd if=/dev/zero of=$SWAP_PATH bs=1M count=$((SWAP_SIZE_GB * 1024))
        sudo chmod 600 $SWAP_PATH
        sudo mkswap $SWAP_PATH
    fi
    sudo swapon $SWAP_PATH
    echo "$SWAP_PATH none swap defaults 0 0" | sudo tee -a /etc/fstab
    echo "[+] 4GB Swap successfully activated!"
fi

echo "=== [2/4] Tuning Kernel Swappiness ==="
# Set swappiness to 10 so OS prefers physical RAM and uses SSD swap only when RAM > 90%
sudo sysctl vm.swappiness=10
if ! grep -q "vm.swappiness" /etc/sysctl.conf; then
    echo "vm.swappiness=10" | sudo tee -a /etc/sysctl.conf
else
    sudo sed -i 's/vm.swappiness=.*/vm.swappiness=10/g' /etc/sysctl.conf
fi
echo "[+] Swappiness set to 10."

echo "=== [3/4] Tuning File Descriptor Limits ==="
if ! grep -q "fs.file-max" /etc/sysctl.conf; then
    echo "fs.file-max=2097152" | sudo tee -a /etc/sysctl.conf
    sudo sysctl -p
fi
echo "[+] File descriptor limits verified."

echo "=== [4/4] Configuring Systemd Service ==="
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_FILE="/etc/systemd/system/myatelier-pro.service"

if [ -d "$PROJECT_DIR" ]; then
    echo "[*] Project directory: $PROJECT_DIR"
    sudo cp "$PROJECT_DIR/deploy/linux/myatelier-pro.service" "$SERVICE_FILE"
    sudo sed -i "s|/opt/myatelier-pro|$PROJECT_DIR|g" "$SERVICE_FILE"
    sudo systemctl daemon-reload
    sudo systemctl enable myatelier-pro.service
    echo "[+] Systemd service enabled to start on system boot!"
fi

echo "=============================================================================="
echo " Host Setup Completed Successfully!"
echo " System is now optimized for running MyAtelier Pro Docker stack."
echo "=============================================================================="
