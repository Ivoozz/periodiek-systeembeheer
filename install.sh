#!/bin/bash
# install.sh v3.0 - ROBUUSTE INSTALLATIE VOOR PRODUCTIE
set -e

APP_DIR="/var/www/systeembeheer"
FORCE_REFRESH=false
if [[ "$1" == "--force" ]]; then
    FORCE_REFRESH=true
fi

echo ">>> Systeembeheer Productie Installatie Start..."

# 1. Systeem pakketten
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv nginx sqlite3 sqlcipher libsqlcipher-dev openssl curl

# 2. App directory setup
sudo mkdir -p $APP_DIR/logs $APP_DIR/backups $APP_DIR/app/static/uploads
sudo chown -R $USER:www-data $APP_DIR
sudo chmod -R 775 $APP_DIR

# 3. Virtual Environment
cd $APP_DIR
if [ ! -d "venv" ] || [ "$FORCE_REFRESH" = true ]; then
    echo ">>> Venv inrichten..."
    rm -rf venv
    python3 -m venv venv
fi
./venv/bin/pip install --upgrade pip
./venv/bin/pip install -r requirements.txt

# 4. Secrets (.env)
if [ ! -f .env ] || [ "$FORCE_REFRESH" = true ]; then
    echo ">>> Secrets genereren..."
    cat << EOF > .env
DATABASE_KEY=$(openssl rand -hex 32)
JWT_SECRET=$(openssl rand -hex 32)
SERVICE_API_TOKEN=$(openssl rand -hex 24)
ADMIN_PASSWORD=Welkom01!
APP_ENV=production
EOF
fi

# 5. Database initialiseren
echo ">>> Database initialiseren..."
export PYTHONPATH=$APP_DIR
./venv/bin/python3 -m app.seed

# 6. Systemd Service
echo ">>> Systemd service registreren..."
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
ExecStart=$APP_DIR/venv/bin/gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 127.0.0.1:8000 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable systeembeheer
sudo systemctl restart systeembeheer

# 7. Nginx Configuratie
echo ">>> Nginx configureren op poort 80..."
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

echo ">>> INSTALLATIE VOLTOOID!"
