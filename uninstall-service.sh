#!/bin/bash
# Deinstallations-Script für CD-Ripper systemd Service

set -e

# Farben
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${RED}═══════════════════════════════════════${NC}"
echo -e "${RED}  CD-Ripper Service Deinstallation${NC}"
echo -e "${RED}═══════════════════════════════════════${NC}\n"

# Root-Check
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ Bitte als root ausführen (sudo)${NC}"
    exit 1
fi

# Service stoppen
echo -e "${YELLOW}⏹️  Stoppe Service...${NC}"
systemctl stop cd-ripper.service 2>/dev/null || true

# Auto-Start deaktivieren
echo -e "${YELLOW}🚫 Deaktiviere Auto-Start...${NC}"
systemctl disable cd-ripper.service 2>/dev/null || true

# Service-Datei entfernen
echo -e "${YELLOW}🗑️  Entferne Service-Datei...${NC}"
rm -f /etc/systemd/system/cd-ripper.service

# systemd neu laden
echo -e "${YELLOW}🔄 Lade systemd neu...${NC}"
systemctl daemon-reload
systemctl reset-failed

echo -e "\n${GREEN}✅ Service deinstalliert!${NC}\n"
