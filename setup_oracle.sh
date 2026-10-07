#!/usr/bin/env bash
# ==============================================================================
# Script to setup Bali Downloader Backend on Oracle Cloud Instance (Ubuntu)
# ==============================================================================
set -e

PORT=5001
APP_DIR="/home/ubuntu/bali-downloader-backend"

echo "=== 1. Updating packages and installing dependencies ==="
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv ffmpeg git curl ufw

echo "=== 2. Creating Python virtual environment ==="
if [ ! -d "$APP_DIR/venv" ]; then
    python3 -m venv "$APP_DIR/venv"
fi

source "$APP_DIR/venv/bin/activate"
pip install --upgrade pip
pip install -r "$APP_DIR/requirements.txt"
pip install -U yt-dlp

echo "=== 3. Setting up systemd service ==="
sudo cp "$APP_DIR/bali-downloader.service" /etc/systemd/system/bali-downloader.service
sudo systemctl daemon-reload
sudo systemctl enable bali-downloader
sudo systemctl restart bali-downloader

echo "=== 4. Opening firewall for port $PORT ==="
# Oracle Ubuntu iptables rule
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport $PORT -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true

# UFW rule if enabled
sudo ufw allow $PORT/tcp 2>/dev/null || true

echo "=== Done! Bali Downloader backend is running on port $PORT ==="
sudo systemctl status bali-downloader --no-pager
