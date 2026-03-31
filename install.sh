#!/bin/bash
# Periodiek Systeembeheer v4.0 "Ultra Visual" - Installatiescript
set -e

# Configuratie
APP_DIR="/var/www/systeembeheer"
LOG_DIR="$APP_DIR/logs"
VENV_DIR="$APP_DIR/venv"
USER_NAME="root"

echo ">>> Systeembeheer v4.0 'Ultra Visual' Installatie Start..."

# 1. Voorbereiding
echo ">>> Systeem pakketten bijwerken..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx libsqlcipher-dev openssl sqlite3 curl wget rsync

# 2. Mapstructuur
echo ">>> Bestandsstructuur inrichten..."
sudo mkdir -p "$APP_DIR" "$LOG_DIR"

# Kopieer bestanden (zonder git/venv)
echo ">>> Projectbestanden synchroniseren..."
sudo rsync -av --exclude '.git' --exclude 'venv' --exclude '__pycache__' ./* "$APP_DIR/"
sudo chown -R $USER_NAME:www-data "$APP_DIR"

cd "$APP_DIR"

# 3. Virtual Environment
if [ ! -d "$VENV_DIR" ]; then
    echo ">>> Virtual environment aanmaken..."
    python3 -m venv "$VENV_DIR"
fi

echo ">>> Dependencies installeren..."
"$VENV_DIR/bin/pip" install --upgrade pip
"$VENV_DIR/bin/pip" install -r requirements.txt

# 3.5 Database Initialisatie
# 3.5 Database Seeding
echo ">>> Database initialiseren en seeden..."
for arg in "$@"; do
    if [ "$arg" == "--reset-db" ]; then
        echo ">>> WAARSCHUWING: Database wordt gereset vanwege schema wijzigingen!"
        rm -f data.db
    fi
done
"$VENV_DIR/bin/python" seed.py

# 4. Secrets (.env)
if [ ! -f .env ]; then
    echo ">>> Nieuwe secrets genereren voor v4.0..."
    cat << EOF > .env
DATABASE_KEY=$(openssl rand -hex 32)
SECRET_KEY=$(openssl rand -hex 32)
APP_ENV=production
EXTERNAL_API_KEY=po-secret-api-key-2026
EOF
else
    echo ">>> Bestaande .env behouden."
fi

# 5. Nginx Configuratie
echo ">>> Nginx configureren op poort 80..."
sudo tee /etc/nginx/sites-available/systeembeheer > /dev/null << EOF
server {
    listen 80 default_server;
    server_name _;

    # Verhoog upload limiet voor eventuele rapporten
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static/ {
        alias $APP_DIR/app/static/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/systeembeheer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default || true

# Test nginx config
sudo nginx -t
sudo systemctl restart nginx

# 6. Systemd Service (Gunicorn + Uvicorn)
echo ">>> Systemd service registreren..."
sudo tee /etc/systemd/system/systeembeheer.service > /dev/null << EOF
[Unit]
Description=Periodiek Systeembeheer v4.0 Gunicorn Service
After=network.target

[Service]
User=$USER_NAME
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$VENV_DIR/bin"
Environment="PYTHONPATH=$APP_DIR"
ExecStart=$VENV_DIR/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable systeembeheer
sudo systemctl restart systeembeheer

# 7. Cleanup & Verify
echo ">>> Opruimen en status controleren..."
sudo journalctl --unit=systeembeheer.service --no-pager | tail -n 20

echo ">>> INSTALLATIE v4.0 VOLTOOID!"
echo "De app is nu bereikbaar op http://\$(hostname -I | awk '{print \$1}')"
