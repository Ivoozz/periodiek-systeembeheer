#!/bin/bash
# install.sh v2.6 - ULTIEME FIX VOOR POORT 80 & SYSTEMD
set -e

# Controleer op --force vlag
FORCE_REFRESH=false
if [[ "$1" == "--force" ]]; then
    FORCE_REFRESH=true
    echo "WAARSCHUWING: Force Refresh geactiveerd."
fi

echo "Systeembeheer Productie Installatie Start..."

# 1. Systeem pakketten installeren
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx sqlite3 sqlcipher libsqlcipher-dev openssl curl net-tools

# 2. App directory setup
APP_DIR="/var/www/systeembeheer"
sudo mkdir -p $APP_DIR
sudo mkdir -p $APP_DIR/logs
sudo mkdir -p $APP_DIR/backups
sudo mkdir -p $APP_DIR/app/static/uploads
sudo chown -R $USER:www-data $APP_DIR
sudo chmod -R 775 $APP_DIR

# 3. Bestanden kopiëren
echo "Bestanden kopiëren naar $APP_DIR..."
cp -r . $APP_DIR/
cd $APP_DIR

# 4. Virtual Environment instellen
if [ ! -d "venv" ] || [ "$FORCE_REFRESH" = true ]; then
    echo "Venv inrichten..."
    rm -rf venv
    python3 -m venv venv
fi
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 5. Secrets genereren (.env)
if [ ! -f .env ] || [ "$FORCE_REFRESH" = true ]; then
    echo "Secrets genereren..."
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
fi

# 6. Database initialiseren
if [ "$FORCE_REFRESH" = true ]; then
    rm -f systeembeheer.db
fi
echo "Database initialiseren..."
export PYTHONPATH=$APP_DIR
./venv/bin/python3 -m app.seed

# 7. Systemd Service instellen (ROBUUST)
echo "Systemd service registreren..."
sudo tee /etc/systemd/system/systeembeheer.service > /dev/null << EOF
[Unit]
Description=Gunicorn Systeembeheer Service
After=network.target

[Service]
User=$USER
Group=www-data
WorkingDirectory=$APP_DIR
Environment="PATH=$APP_DIR/venv/bin"
Environment="PYTHONPATH=$APP_DIR"
# Forceer laden van .env via shell-wrapper indien nodig, maar gunicorn doet dit meestal zelf via de app
ExecStart=$APP_DIR/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable systeembeheer
sudo systemctl restart systeembeheer

# 8. Nginx Configuratie (Dwing poort 80 af)
echo "Nginx configureren op poort 80..."
sudo tee /etc/nginx/sites-available/systeembeheer > /dev/null << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    server_name _;

    access_log /var/www/systeembeheer/logs/nginx_access.log;
    error_log /var/www/systeembeheer/logs/nginx_error.log;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        client_max_body_size 50M;
    }
    
    location /static/ {
        alias /var/www/systeembeheer/app/static/;
    }
}
EOF

sudo ln -sf /etc/nginx/sites-available/systeembeheer /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default || true
sudo nginx -t
sudo systemctl restart nginx

echo "-------------------------------------------------------"
echo "INSTALLATIE VOLTOOID OP POORT 80!"
TOKEN=$(grep "SERVICE_API_TOKEN=" .env | cut -d'=' -f2)
echo "SERVICE API TOKEN: $TOKEN"
echo "SITE BEREIKBAAR OP: http://$(hostname -I | awk '{print $1}')"
echo "-------------------------------------------------------"
