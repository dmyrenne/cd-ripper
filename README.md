# 🎵 CD-Ripper - Automatischer CD-Ripping-Service# 🎵 Automatischer CD-Ripper - Projektübersicht



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-red.svg)](https://www.raspberrypi.org/)

## 📋 Projekt-Ziel
Ein vollautomatischer CD-Ripping-Service, der beim Einlegen einer Audio-CD:
1. Die CD identifiziert

2. Unterscheide zwischen Kategorien: 

Automatischer Service für Audio-CDs mit intelligenter Kategorisierung, formatspezifischer Konvertierung und Web-Interface zur Überwachung und Konfiguration.    Kategorie 1: Hörspiel oder Musik für Kinder

    Kategorie 2: Hörbücher eher für Erwachsene

![CD-Ripper Web Interface - Aktives Ripping](https://via.placeholder.com/1200x600/1e293b/ffffff?text=CD-Ripper+Web+Interface)    Kategorie 3: Musik (Künstler, Album, Tracks)

2. Entsprechend der Kategorie unterschiedliche Ripping Einstellungen wählen:

## ✨ Features    Kategorie 1 + 2: MP3 320KBit/s

    Kategorie 3: FLAC (16 Bit 44,000Hz)

### 🎯 Kern-Funktionen3. In das gewünschte Format konvertiert (FLAC, MP3)

- **Automatische CD-Erkennung**: Erkennt eingelegte Audio-CDs automatisch4. Metadaten und Cover einbettet

- **MusicBrainz Integration**: Identifiziert CDs und lädt Metadaten + Cover-Art5. Automatisch auf einen lokalen Server synchronisiert

- **Intelligente Kategorisierung**: 
  - Kategorie 1: Kinderinhalte (Hörspiele, Kindermusik)
  - Kategorie 2: Hörbücher für Erwachsene
  - Kategorie 3: Musik
- **Format-Optimierung**:
  - Kategorien 1+2: MP3 @ 320 kbit/s (platzsparend)
  - Kategorie 3: FLAC Lossless (maximale Qualität)
- **Server-Synchronisation**: Automatischer Upload auf NAS/Server via rsync
- **Auto-Cleanup**: Lokale Dateien werden nach Upload gelöscht

### 🌐 Web-Interface
- **Echtzeit-Status**: Live-Anzeige des Ripping-Fortschritts
- **Cover-Anzeige**: Zeigt Album-Cover während des Rippings
- **Progress-Tracking**: Detaillierte Fortschrittsanzeige pro Track
- **Einstellungs-Editor**: Alle Parameter über Web-UI anpassbar
- **Mobile-optimiert**: Responsive Design für Smartphone/Tablet
- **Live-Logs**: Echtzeit-Log-Anzeige im Browser

### 🔧 Technische Features
- **Systemd-Service**: Automatischer Start beim Boot
- **Fehlertoleranz**: Retry-Logik und robustes Error-Handling
- **Status-Persistence**: SharedStatus via JSON-File mit fcntl-Locking
- **Konfigurierbar**: YAML-basierte Konfiguration
- **Vollständiges Logging**: Audit-Trail aller Operationen

## 📋 Voraussetzungen

### Hardware
- **Raspberry Pi 4** (oder ähnlich, min. 2GB RAM empfohlen)
- **USB CD/DVD-Laufwerk**
- **Netzwerk-Zugang** für MusicBrainz und Server-Sync

### Software
- **Raspberry Pi OS** (Debian Bookworm oder neuer)
- **Python 3.8+**
- **Root-Zugriff** (für systemd-Service)

## 🚀 Installation

### 1. Repository klonen

```bash
cd ~
git clone https://github.com/dmyrenne/cd-ripper.git
cd cd-ripper
```

### 2. System-Dependencies installieren

```bash
sudo apt-get update
sudo apt-get install -y \
    cdparanoia \
    flac \
    lame \
    ffmpeg \
    libdiscid0 \
    rsync \
    sshpass \
    eject \
    python3-pip \
    python3-venv
```

### 3. Python Virtual Environment erstellen

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Konfiguration erstellen

```bash
cp config/config.yaml.example config/config.yaml
nano config/config.yaml
```

**Wichtige Einstellungen:**

```yaml
ripper:
  device: /dev/sr0  # Dein CD-Laufwerk
  
sync:
  enabled: true
  host: 10.10.1.3  # Dein NAS/Server
  user: dein_username
  password: dein_passwort  # Besser: SSH-Keys nutzen!
  remote_paths:
    category_1: /pfad/zu/Kinderinhalte
    category_2: /pfad/zu/Hörbücher
    category_3: /pfad/zu/Musik

output:
  local_path: /mnt/dietpi_userdata/rips  # Lokaler Output
```

### 5. Service installieren

```bash
sudo ./install-service.sh
```

Das Script:
- Kopiert die systemd-Service-Datei
- Aktiviert Auto-Start beim Boot
- Startet den Service

### 6. Web-Interface öffnen

```
http://<raspberry-pi-ip>:5000
```

**Standard-Port**: 5000 (in config.yaml änderbar)

## 🎮 Verwendung

### Automatischer Betrieb

1. **CD einlegen** → Service erkennt CD automatisch
2. **Identifikation** → MusicBrainz-Abfrage für Metadaten
3. **Kategorisierung** → Automatische Zuordnung
4. **Ripping** → cdparanoia extrahiert Audio
5. **Encoding** → Konvertierung in Zielformat
6. **Tagging** → Metadaten + Cover einbetten
7. **Sync** → Upload auf Server
8. **Cleanup** → Lokale Dateien löschen
9. **Eject** → CD automatisch auswerfen

### Manuelles Bedienen

#### Service-Befehle

```bash
# Service starten
sudo systemctl start cd-ripper

# Service stoppen
sudo systemctl stop cd-ripper

# Service neu starten
sudo systemctl restart cd-ripper

# Status prüfen
sudo systemctl status cd-ripper

# Auto-Start deaktivieren
sudo systemctl disable cd-ripper

# Auto-Start aktivieren
sudo systemctl enable cd-ripper
```

#### Logs anschauen

```bash
# Live-Logs
sudo journalctl -u cd-ripper -f

# Letzte 100 Zeilen
sudo journalctl -u cd-ripper -n 100

# Log-Datei direkt
tail -f ~/cd-ripper/logs/ripper.log
```

#### CD manuell auswerfen

```bash
# Via Web-Interface: Button "Auswerfen"
# Oder Terminal:
eject /dev/sr0
```

## ⚙️ Konfiguration

### Via Web-Interface

1. Öffne `http://<ip>:5000`
2. Klicke auf "⚙️ Einstellungen"
3. Bearbeite Einstellungen
4. Klicke "💾 Speichern & Neu starten"

### Via Konfig-Datei

```bash
nano ~/cd-ripper/config/config.yaml
sudo systemctl restart cd-ripper
```

### Wichtige Parameter

#### Ripper-Einstellungen
```yaml
ripper:
  device: /dev/sr0        # CD-Laufwerk
  quality: paranoia       # paranoia, normal, fast
```

#### Encoding-Profile
```yaml
encoder:
  profiles:
    category_1_2:         # Kinder + Hörbücher
      format: mp3
      bitrate: 320
    category_3:           # Musik
      format: flac
      compression_level: 8
```

#### Server-Sync
```yaml
sync:
  enabled: true
  host: 10.10.1.3
  user: dietpi
  cleanup: true           # Lokale Dateien löschen
  auto_eject: true        # CD nach Sync auswerfen
```

## 📂 Projektstruktur

```
cd-ripper/
├── config/
│   ├── config.yaml              # Aktive Konfiguration (nicht im Repo)
│   └── config.yaml.example      # Beispiel-Konfiguration
├── docs/
│   ├── screenshots/             # Screenshots für README
│   └── STATUS-MANAGEMENT.md     # Technische Doku
├── logs/
│   └── ripper.log              # Service-Logs
├── output/                      # Temporäre gerippte CDs (wird geleert)
├── src/
│   ├── main.py                 # Haupt-Service
│   ├── service.py              # Service-Launcher
│   ├── cd_detector.py          # Hardware-Erkennung
│   ├── cd_identifier.py        # MusicBrainz Integration
│   ├── cd_categorizer.py       # Kategorisierungs-Logik
│   ├── ripper.py               # cdparanoia Wrapper
│   ├── encoder.py              # Audio-Konvertierung
│   ├── tagger.py               # Metadaten-Tagging
│   ├── syncer.py               # Server-Sync
│   ├── web_interface.py        # Flask Web-App
│   ├── shared_status.py        # IPC-Mechanismus
│   └── utils.py                # Helper-Funktionen
├── tests/
│   ├── test_simulate_rip.py    # Simulations-Test
│   └── test_web_updates.py     # Web-Interface Test
├── web/
│   ├── static/
│   │   ├── app.js              # Frontend-Logik
│   │   ├── settings.js         # Settings-Editor
│   │   └── style.css           # Design
│   └── templates/
│       ├── index.html          # Hauptseite
│       └── settings.html       # Einstellungen
├── cd-ripper.service           # systemd Service-Datei
├── install-service.sh          # Installations-Script
├── uninstall-service.sh        # Deinstallations-Script
├── requirements.txt            # Python-Dependencies
└── README.md                   # Diese Datei
```

## 🐛 Troubleshooting

### CD wird nicht erkannt

```bash
# Prüfe ob Laufwerk erkannt wird
lsblk | grep sr0

# Teste cdparanoia direkt
cdparanoia -vsQ

# Prüfe Device in Config
cat config/config.yaml | grep device
```

### Service startet nicht

```bash
# Prüfe Logs
sudo journalctl -u cd-ripper -n 50

# Prüfe Config-Syntax
python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Teste manuell
cd ~/cd-ripper
source venv/bin/activate
python3 src/service.py
```

### MusicBrainz findet CD nicht

- Prüfe Internet-Verbindung
- Manche CDs sind nicht in MusicBrainz
- Manuelle Zuordnung über Web-Interface möglich (geplant)

### Server-Sync schlägt fehl

```bash
# Teste rsync manuell
rsync -avz --progress /pfad/zu/datei user@host:/pfad/

# Prüfe SSH-Zugang
ssh user@host

# Prüfe sshpass
which sshpass

# Besser: SSH-Keys statt Passwort
ssh-copy-id user@host
# Dann password in config.yaml entfernen
```

### Web-Interface nicht erreichbar

```bash
# Prüfe ob Service läuft
sudo systemctl status cd-ripper

# Prüfe Port
sudo netstat -tlnp | grep 5000

# Prüfe Firewall
sudo ufw status

# Teste lokal
curl http://localhost:5000
```

## 🔒 Sicherheit

### SSH-Keys statt Passwort (empfohlen)

```bash
# SSH-Key generieren
ssh-keygen -t ed25519

# Key zum Server kopieren
ssh-copy-id user@server

# In config.yaml: password-Feld entfernen oder leer lassen
```

### Firewall

```bash
# Nur aus lokalem Netzwerk erlauben
sudo ufw allow from 192.168.1.0/24 to any port 5000
```

### Berechtigungen

```bash
# Config vor anderen Nutzern schützen (wegen Passwort)
chmod 600 ~/cd-ripper/config/config.yaml
```

## 🛠️ Entwicklung

### Tests ausführen

```bash
# Simulationstest (ohne echte CD)
python3 tests/test_web_updates.py

# Playwright-Browser-Test
# (erfordert playwright-mcp)
```

### Neue Features

1. Fork das Repository
2. Feature-Branch erstellen: `git checkout -b feature/name`
3. Änderungen committen: `git commit -m 'Add feature'`
4. Branch pushen: `git push origin feature/name`
5. Pull Request öffnen

## 📝 To-Do / Geplante Features

- [ ] ST7789 Display-Unterstützung für Standalone-Betrieb
- [ ] SSH-Key-Authentication ohne Passwort
- [ ] Multi-CD-Batch-Processing
- [ ] Manuelle Metadaten-Bearbeitung im Web-Interface
- [ ] Cover-Art Upload für CDs ohne MusicBrainz-Eintrag
- [ ] Statistiken (gerippte CDs, Speicherplatz, etc.)
- [ ] Email-Benachrichtigungen bei Fehlern
- [ ] Docker-Container für einfache Installation

## 🙏 Credits

### Dependencies
- [cdparanoia](https://www.xiph.org/paranoia/) - CD-Ripping mit Fehlerkorrektur
- [MusicBrainz](https://musicbrainz.org/) - CD-Identifikation & Metadaten
- [Flask](https://flask.palletsprojects.com/) - Web-Framework
- [mutagen](https://mutagen.readthedocs.io/) - Audio-Tagging

### Inspiration
- Inspiriert von klassischen CD-Ripping-Tools wie K3b, Grip und abcde
- Web-Interface Design angelehnt an moderne Admin-Panels

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE) Datei für Details

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/dmyrenne/cd-ripper/discussions)
- **Wiki**: [GitHub Wiki](https://github.com/dmyrenne/cd-ripper/wiki)

## 🌟 Contributors

- Daniel Myrenne - Initial Work - [@dmyrenne](https://github.com/dmyrenne)

---

**Made with ❤️ for music lovers and audiobook enthusiasts**

*CD-Ripper läuft stabil auf Raspberry Pi 4 mit Raspberry Pi OS (Debian Bookworm)*
