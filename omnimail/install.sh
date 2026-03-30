#!/bin/bash
set -e

echo "=========================================="
echo "    OmniMail - 1-Stop Installation        "
echo "=========================================="

if [ "$EUID" -ne 0 ]; then
  echo "Please run this script as root (e.g., using sudo)."
  exit 1
fi

echo "[1/4] Updating system packages..."
apt-get update -y
apt-get upgrade -y
apt-get install -y curl git build-essential sqlite3

echo "[2/4] Installing Node.js..."
if ! command -v node &> /dev/null; then
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y nodejs
else
  echo "Node.js is already installed."
fi

echo "[3/4] Installing application dependencies..."
npm install --legacy-peer-deps

echo "[4/4] Starting Interactive Setup..."
node setup.js

echo "=========================================="
echo "    Installation Complete!                "
echo "=========================================="
