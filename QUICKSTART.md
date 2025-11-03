# 🚀 Quick Start Guide - CD-Ripper Installation

Schnellanleitung für die Installation des CD-Rippers auf einem Raspberry Pi.

## Voraussetzungen

- Raspberry Pi 4 (min. 2GB RAM)
- Raspberry Pi OS (Debian Bookworm)
- USB CD/DVD-Laufwerk
- Internet-Verbindung
- SSH-Zugang zum Pi

## Installation in 5 Minuten

### 1. Repository klonen

```bash
ssh pi@<deine-ip>
cd ~
git clone https://github.com/dmyrenne/cd-ripper.git
cd cd-ripper
```

### 2. Dependencies installieren

```bash
# System-Pakete
sudo apt-get update && sudo apt-get install -y \
    cdparanoia flac lame ffmpeg libdiscid0 rsync sshpass eject \
    python3-pip python3-venv

# Python-Umgebung
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Konfiguration

```bash
# Beispiel-Config kopieren
cp config/config.yaml.example config/config.yaml

# Config bearbeiten
nano config/config.yaml
```

**Mindest-Anpassungen:**

```yaml
# Zeile ~3: CD-Laufwerk
ripper:
  device: /dev/sr0  # Dein Laufwerk

# Zeile ~30: Server-Einstellungen
sync:
  host: 10.10.1.3      # Dein NAS/Server
  user: dein_username   # SSH-User
  password: passwort    # Oder SSH-Key nutzen!
```

### 4. Service installieren

```bash
sudo ./install-service.sh
```

### 5. Fertig! 🎉

Web-Interface öffnen:
```
http://<raspberry-pi-ip>:5000
```

CD einlegen und automatisches Ripping beobachten!

## Erste Schritte

1. **Test-CD einlegen** → Service erkennt automatisch
2. **Web-Interface öffnen** → Fortschritt beobachten
3. **Einstellungen anpassen** → Button "⚙️ Einstellungen"
4. **Logs prüfen** → `sudo journalctl -u cd-ripper -f`

## Troubleshooting

### CD wird nicht erkannt

```bash
# Prüfe Laufwerk
lsblk | grep sr0

# Teste cdparanoia
cdparanoia -vsQ
```

### Service läuft nicht

```bash
# Status prüfen
sudo systemctl status cd-ripper

# Logs anschauen
sudo journalctl -u cd-ripper -n 50
```

### Web-Interface nicht erreichbar

```bash
# Port prüfen
sudo netstat -tlnp | grep 5000

# Service neu starten
sudo systemctl restart cd-ripper
```

## Nächste Schritte

- [Vollständige README](README.md)
- [Konfiguration](config/config.yaml.example)
- [Status-Management](docs/STATUS-MANAGEMENT.md)

## Support

Bei Problemen: [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)

---

**Viel Spaß beim Rippen! 🎵💿**
