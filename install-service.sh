#!/bin/bash
# Installation Script für CD-Ripper systemd Service

set -e

# Farben für Output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}  CD-Ripper Service Installation${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

# Root-Check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bitte als root ausführen (sudo)${NC}"
    exit 1
fi

# Projekt-Verzeichnis ermitteln
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
echo -e "${BLUE}📁 Projekt-Verzeichnis: ${NC}$PROJECT_DIR"

# Service-Datei kopieren
echo -e "\n${YELLOW}📋 Installiere systemd Service...${NC}"
cp "$PROJECT_DIR/cd-ripper.service" /etc/systemd/system/
chmod 644 /etc/systemd/system/cd-ripper.service

# systemd neu laden
echo -e "${YELLOW}🔄 Lade systemd neu...${NC}"
systemctl daemon-reload

# Service aktivieren (Auto-Start beim Boot)
echo -e "${YELLOW}🚀 Aktiviere Auto-Start beim Boot...${NC}"
systemctl enable cd-ripper.service

# Service starten
echo -e "${YELLOW}▶️  Starte Service...${NC}"
systemctl start cd-ripper.service

# Kurze Pause für Service-Start
sleep 2

# Status prüfen
echo -e "\n${BLUE}═══════════════════════════════════════${NC}"
echo -e "${GREEN}✅ Installation abgeschlossen!${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}\n"

systemctl status cd-ripper.service --no-pager

echo -e "\n${GREEN}📌 Nützliche Befehle:${NC}"
echo -e "  ${YELLOW}Status prüfen:${NC}      sudo systemctl status cd-ripper"
echo -e "  ${YELLOW}Logs anzeigen:${NC}      sudo journalctl -u cd-ripper -f"
echo -e "  ${YELLOW}Service stoppen:${NC}    sudo systemctl stop cd-ripper"
echo -e "  ${YELLOW}Service neu starten:${NC} sudo systemctl restart cd-ripper"
echo -e "  ${YELLOW}Auto-Start deaktivieren:${NC} sudo systemctl disable cd-ripper"
echo -e "\n${GREEN}🌐 Web-Interface:${NC} http://$(hostname -I | awk '{print $1}'):5000"
echo ""
