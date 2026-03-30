#!/bin/bash
# install.sh v2.2 - Productie-klare uitrol voor Debian LXC met Force Refresh
set -e

# Controleer op --force vlag
FORCE_REFRESH=false
if [[ "$1" == "--force" ]]; then
    FORCE_REFRESH=true
    echo "WAARSCHUWING: Force Refresh geactiveerd. Bestaande configuratie wordt overschreven."
fi

echo "Systeembeheer Productie Installatie Start..."

# 1. Systeem pakketten installeren
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx sqlite3 sqlcipher libsqlcipher-dev openssl

# 2. App directory setup
APP_DIR="/var/www/systeembeheer"
sudo mkdir -p $APP_DIR
sudo mkdir -p $APP_DIR/logs
sudo mkdir -p $APP_DIR/backups
sudo chown -R $USER:$USER $APP_DIR

# 3. Bestanden kopiëren
cp -r . $APP_DIR/
cd $APP_DIR

# 4. Virtual Environment instellen
if [ ! -d "venv" ] || [ "$FORCE_REFRESH" = true ]; then
    rm -rf venv
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. Secrets genereren (.env)
if [ ! -f .env ] || [ "$FORCE_REFRESH" = true ]; then
    echo "Secrets genereren voor .env..."
    DB_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    SERVICE_TOKEN=$(openssl rand -hex 24)
    cat << EOF > .env
DATABASE_KEY=$DB_KEY
JWT_SECRET=$JWT_SECRET
SERVICE_API_TOKEN=$SERVICE_TOKEN
ADMIN_PASSWORD=Welkom01!
APP_ENV=production
EOF
    echo "Nieuwe .env aangemaakt met unieke sleutels."
fi

# 6. Database initialiseren (SQLCipher)
echo "Database initialiseren..."
# Bij force refresh, optioneel db verwijderen (gevaarlijk, dus doen we alleen handmatig of via seed script)
python3 -m app.seed

# 7. Systemd Service instellen (Gunicorn)
cat << EOF | sudo tee /etc/systemd/system/systeembeheer.service
[Unit]
Description=Gunicorn Systeembeheer Service
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable systeembeheer
sudo systemctl restart systeembeheer

# 8. Nginx Configuratie
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
        client_max_body_size 20M;
    }
    
    # Static files direct serveren
    location /static/ {
        alias /var/www/systeembeheer/app/static/;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/systeembeheer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t
sudo systemctl restart nginx

# 9. Backup Cron-job
(crontab -l 2>/dev/null | grep -v "scripts/backup.sh"; echo "0 2 * * * /bin/bash $APP_DIR/scripts/backup.sh") | crontab -

echo "-------------------------------------------------------"
echo "Installatie voltooid!"
# Forceer herladen van env om de token te tonen
TOKEN=$(grep SERVICE_API_TOKEN .env | cut -d'=' -f2)
echo "Service API Token: $TOKEN"
echo "Beheerder wachtwoord: Welkom01!"
echo "-------------------------------------------------------"
