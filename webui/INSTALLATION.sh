#!/bin/bash
# -*- coding: utf-8 -*-
# KIVerdienst V2 WebUI - Installation Script

set -e

echo "?? KIVerdienst V2 WebUI - Installation"
echo "======================================="
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo -e "${RED}? Bitte als root ausf?hren: sudo ./INSTALLATION.sh${NC}"
    exit 1
fi

# Backup existing files
if [ -d "/opt/kiverdienst" ]; then
    echo -e "${YELLOW}??  Backup existing installation...${NC}"
    cp -r /opt/kiverdienst /opt/kiverdienst.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}? Backup created${NC}"
fi

# Create directory if not exists
mkdir -p /opt/kiverdienst/{templates,static/js,static/css,database,uploads}

# Copy files
echo -e "${YELLOW}?? Copying files...${NC}"
cp -v app.py /opt/kiverdienst/
cp -v templates/*.html /opt/kiverdienst/templates/ 2>/dev/null || echo "No templates found"
cp -v static/js/*.js /opt/kiverdienst/static/js/
cp -v static/css/*.css /opt/kiverdienst/static/css/

# Set permissions
echo -e "${YELLOW}?? Setting permissions...${NC}"
chown -R www-data:www-data /opt/kiverdienst/
chmod +x /opt/kiverdienst/app.py

# Install Python dependencies
echo -e "${YELLOW}?? Installing Python dependencies...${NC}"
pip3 install flask gunicorn 2>/dev/null || echo "Dependencies already installed"

# Create or update systemd service
echo -e "${YELLOW}??  Creating systemd service...${NC}"
cat > /etc/systemd/system/kiverdienst-webui.service <<EOF
[Unit]
Description=KIVerdienst V2 WebUI
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/kiverdienst
Environment="PYTHONIOENCODING=utf-8"
Environment="LANG=de_DE.UTF-8"
ExecStart=/usr/bin/python3 /opt/kiverdienst/app.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and start service
echo -e "${YELLOW}?? Reloading systemd...${NC}"
systemctl daemon-reload
systemctl enable kiverdienst-webui
systemctl restart kiverdienst-webui

# Wait for service to start
sleep 3

# Check service status
if systemctl is-active --quiet kiverdienst-webui; then
    echo ""
    echo -e "${GREEN}? Installation erfolgreich!${NC}"
    echo ""
    echo "Service Status:"
    systemctl status kiverdienst-webui --no-pager
    echo ""
    echo "WebUI verf?gbar unter:"
    echo "  http://$(hostname -I | awk '{print $1}'):5000"
    echo "  http://localhost:5000"
    echo ""
    echo "Logs anzeigen:"
    echo "  sudo journalctl -u kiverdienst-webui -f"
else
    echo ""
    echo -e "${RED}? Service Start fehlgeschlagen!${NC}"
    echo "Logs anzeigen mit:"
    echo "  sudo journalctl -u kiverdienst-webui -n 50"
    exit 1
fi
