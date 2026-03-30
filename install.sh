#!/bin/bash
# install.sh - Productie-klare deployment script voor Debian LXC
set -e

echo "Systeembeheer Productie-Installatie Start..."

# Bepaal de huidige gebruiker
CURRENT_USER=$(whoami)
APP_DIR="/var/www/systeembeheer"

# 1. Installeer systeem pakketten inclusief SQLCipher
echo "Installeren van systeem pakketten..."
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx sqlcipher libsqlcipher-dev build-essential openssl

# 2. App directory setup
echo "Inrichten van directory: $APP_DIR"
sudo mkdir -p $APP_DIR
sudo chown -R $CURRENT_USER:$CURRENT_USER $APP_DIR

# 3. Kopieer bronbestanden
echo "Kopiëren van bestanden..."
cp -r . $APP_DIR/
cd $APP_DIR

# 4. Automate .env configuratie (DATABASE_KEY & JWT_SECRET)
if [ ! -f ".env" ]; then
    echo "Genereren van nieuwe .env configuratie..."
    DATABASE_KEY=$(openssl rand -hex 32)
    JWT_SECRET=$(openssl rand -hex 32)
    cat <<EOF > .env
DATABASE_KEY=$DATABASE_KEY
JWT_SECRET=$JWT_SECRET
ADMIN_PASSWORD=Welkom01!
APP_ENV=production
EOF
else
    echo ".env bestand bestaat al, overslaan van generatie."
fi

# 5. Virtual Environment setup & installatie
echo "Setup van Python Virtual Environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 6. Initialiseer Database & Seed Data
echo "Initialiseren van de database..."
python3 -m app.seed

# 7. Systemd Service Configuratie (Gunicorn)
echo "Configureren van Systemd service..."
cat << EOF | sudo tee /etc/systemd/system/systeembeheer.service
[Unit]
Description=Gunicorn Systeembeheer Service
After=network.target

[Service]
User=$CURRENT_USER
Group=www-data
WorkingDirectory=$APP_DIR
EnvironmentFile=$APP_DIR/.env
Environment="PATH=$APP_DIR/venv/bin"
ExecStart=$APP_DIR/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 127.0.0.1:8000

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable systeembeheer
sudo systemctl start systeembeheer || (journalctl -u systeembeheer --no-pager | tail -n 20 && exit 1)

# 8. Nginx Configuratie (Reverse Proxy)
echo "Configureren van Nginx..."
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

# 9. Setup Cron-job voor backup.sh
echo "Instellen van de nachtelijke backup..."
chmod +x scripts/backup.sh
mkdir -p logs
# Voorkom dubbele cronjobs
(crontab -l 2>/dev/null | grep -v "scripts/backup.sh"; echo "0 2 * * * /bin/bash $APP_DIR/scripts/backup.sh >> $APP_DIR/logs/backup.log 2>&1") | crontab -

echo "Productie-installatie voltooid. Applicatie draait op poort 80."
echo "Backup is ingesteld voor elke nacht om 02:00 uur (Logs: $APP_DIR/logs/backup.log)."
