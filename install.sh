#!/bin/bash
# install.sh - One-click deployment script voor Debian LXC
set -e

echo "Systeembeheer Installatie Start..."

# Installeer systeem pakketten
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx sqlite3

# App directory setup
APP_DIR="/var/www/systeembeheer"
sudo mkdir -p $APP_DIR
sudo chown -R $USER:$USER $APP_DIR

# Kopieer bronbestanden (ervan uitgaande dat we in de repo root zijn)
cp -r . $APP_DIR/
cd $APP_DIR

# Virtual Environment setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialiseer Database & Seed Data
python3 -m app.seed

# Systemd Service Configuratie
cat << 'EOF' | sudo tee /etc/systemd/system/systeembeheer.service
[Unit]
Description=FastAPI Systeembeheer Service
After=network.target

[Service]
User=root
Group=www-data
WorkingDirectory=/var/www/systeembeheer
Environment="PATH=/var/www/systeembeheer/venv/bin"
ExecStart=/var/www/systeembeheer/venv/bin/uvicorn app.main:app --host 127.0.0.1 --port 8000

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable systeembeheer
sudo systemctl start systeembeheer

# Nginx Configuratie (Port 80 naar 8000)
cat << 'EOF' | sudo tee /etc/nginx/sites-available/systeembeheer
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/systeembeheer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

echo "Installatie voltooid. Applicatie draait op poort 80."
