#!/bin/bash
echo "==================================="
echo "  RYAN-HYDRA INSTALLER"
echo "==================================="
if ! command -v python3 &> /dev/null; then
    sudo apt update && sudo apt install python3 python3-pip -y
fi
pip3 install -r requirements.txt 2>/dev/null || pip3 install --break-system-packages -r requirements.txt
mkdir -p results
chmod +x ryan-hydra.py
echo "[✓] Installed! Run: python3 ryan-hydra.py"
