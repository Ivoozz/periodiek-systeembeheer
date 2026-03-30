#!/bin/bash
# scripts/backup.sh - Nightly encrypted backup for Systeembeheer
set -e

# Configuratie
BACKUP_DIR="/var/www/systeembeheer/backups"
DB_PATH="/var/www/systeembeheer/systeembeheer.db"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/systeembeheer_$TIMESTAMP.db"

# Maak backup directory als deze niet bestaat
mkdir -p "$BACKUP_DIR"

# Laad environment variabelen voor de DATABASE_KEY
if [ -f "/var/www/systeembeheer/.env" ]; then
    export $(grep -v '^#' /var/www/systeembeheer/.env | xargs)
fi

if [ -z "$DATABASE_KEY" ]; then
    echo "Fout: DATABASE_KEY niet gevonden in .env bestand."
    exit 1
fi

echo "Starten van backup naar $BACKUP_FILE..."

# Gebruik SQLCipher om een consistente backup te maken
# We exporteren de database naar een nieuw bestand met dezelfde key
sqlcipher "$DB_PATH" <<EOF
PRAGMA key = '$DATABASE_KEY';
ATTACH DATABASE '$BACKUP_FILE' AS backup KEY '$DATABASE_KEY';
SELECT sqlcipher_export('backup');
DETACH DATABASE backup;
EOF

# Optioneel: Behoud alleen de laatste 7 dagen aan backups
find "$BACKUP_DIR" -name "systeembeheer_*.db" -mtime +7 -delete

echo "Backup succesvol afgerond."
