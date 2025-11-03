# 🎵 CD-Ripper# 🎵 CD-Ripper - Automatic CD Ripping Service



[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-red.svg)](https://www.raspberrypi.org/)[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)



Automatic CD ripping service with intelligent categorization and web interface. Insert CD → Get tagged audio files on your server.[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-red.svg)](https://www.raspberrypi.org/)[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)



---

## ✨ Features[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

## Features



### 🎯 Automatic Workflow

- **CD Detection** - Automatically recognizes audio CDs### 🎯 Core FunctionsAutomatic service for audio CDs with intelligent categorization, format-specific conversion, and web interface for monitoring and configuration.[![Raspberry Pi](https://img.shields.io/badge/Raspberry%20Pi-4-red.svg)](https://www.raspberrypi.org/)

- **Identification** - Fetches metadata from MusicBrainz

- **Categorization** - Kids content, audiobooks, or music- **Automatic CD Detection**: Automatically recognizes inserted audio CDs

- **Format Selection** - MP3 320kbps or FLAC lossless

- **Server Sync** - Automatic upload via rsync- **MusicBrainz Integration**: Identifies CDs and downloads metadata + cover art

- **Auto-Eject** - Done and ready for next CD

- **Intelligent Categorization**: 

### 🌐 Web Interface

- Real-time status with album cover  - Category 1: Children's content (audio plays, children's music)![CD-Ripper Web Interface - Active Ripping](https://via.placeholder.com/1200x600/1e293b/ffffff?text=CD-Ripper+Web+Interface)## 📋 Projekt-Ziel

- Progress tracking per track

- Settings editor (all parameters)  - Category 2: Audiobooks for adults

- Mobile-responsive design

- Multilingual (English/German)  - Category 3: MusicEin vollautomatischer CD-Ripping-Service, der beim Einlegen einer Audio-CD:

- Live logs

- **Format Optimization**:

### ⚙️ Technical

- Systemd service with auto-start  - Categories 1+2: MP3 @ 320 kbit/s (space-saving)## ✨ Features1. Die CD identifiziert

- YAML configuration

- Robust error handling  - Category 3: FLAC Lossless (maximum quality)

- Thread-safe status management

- **Server Synchronization**: Automatic upload to NAS/Server via rsync

---

- **Auto-Cleanup**: Local files are deleted after upload

## Quick Start

### 🎯 Core Functions2. Unterscheide zwischen Kategorien: 

```bash

# 1. Clone### 🌐 Web Interface

git clone https://github.com/dmyrenne/cd-ripper.git

cd cd-ripper- **Real-time Status**: Live display of ripping progress- **Automatic CD Detection**: Automatically recognizes inserted audio CDs



# 2. Install dependencies- **Cover Display**: Shows album cover during ripping

sudo apt-get install -y cdparanoia flac lame ffmpeg libdiscid0 rsync sshpass eject python3-pip python3-venv

python3 -m venv venv- **Progress Tracking**: Detailed progress display per track- **MusicBrainz Integration**: Identifies CDs and downloads metadata + cover artAutomatischer Service für Audio-CDs mit intelligenter Kategorisierung, formatspezifischer Konvertierung und Web-Interface zur Überwachung und Konfiguration.    Kategorie 1: Hörspiel oder Musik für Kinder

source venv/bin/activate

pip install -r requirements.txt- **Settings Editor**: All parameters adjustable via web UI



# 3. Configure- **Mobile-Optimized**: Responsive design for smartphone/tablet- **Intelligent Categorization**: 

cp config/config.yaml.example config/config.yaml

nano config/config.yaml  # Edit: CD drive, server, paths- **Live Logs**: Real-time log display in browser



# 4. Install service- **Multilingual**: English & German interface (configurable)  - Category 1: Children's content (audio plays, children's music)    Kategorie 2: Hörbücher eher für Erwachsene

sudo ./install-service.sh



# 5. Open web interface

# http://<raspberry-pi-ip>:5000### 🔧 Technical Features  - Category 2: Audiobooks for adults

```

- **Systemd Service**: Automatic start on boot

---

- **Fault Tolerance**: Retry logic and robust error handling  - Category 3: Music![CD-Ripper Web Interface - Aktives Ripping](https://via.placeholder.com/1200x600/1e293b/ffffff?text=CD-Ripper+Web+Interface)    Kategorie 3: Musik (Künstler, Album, Tracks)

## Configuration

- **Status Persistence**: SharedStatus via JSON file with fcntl locking

### Minimal Setup

- **Configurable**: YAML-based configuration- **Format Optimization**:

Edit `config/config.yaml`:

- **Complete Logging**: Audit trail of all operations

```yaml

ripper:- **Internationalization**: Easy to add more languages  - Categories 1+2: MP3 @ 320 kbit/s (space-saving)2. Entsprechend der Kategorie unterschiedliche Ripping Einstellungen wählen:

  device: /dev/sr0              # Your CD drive



sync:

  host: 10.10.1.3               # Your NAS/Server## 📋 Requirements  - Category 3: FLAC Lossless (maximum quality)

  user: your_username

  password: your_password       # Or use SSH keys (recommended)

  remote_paths:

    category_1: /path/to/kids           # Children's content### Hardware- **Server Synchronization**: Automatic upload to NAS/Server via rsync## ✨ Features    Kategorie 1 + 2: MP3 320KBit/s

    category_2: /path/to/audiobooks     # Audiobooks

    category_3: /path/to/music          # Music- **Raspberry Pi 4** (or similar, min. 2GB RAM recommended)



web_interface:- **USB CD/DVD Drive**- **Auto-Cleanup**: Local files are deleted after upload

  port: 5000

  language: en                  # en or de- **Network Access** for MusicBrainz and server sync

```

    Kategorie 3: FLAC (16 Bit 44,000Hz)

### Encoding Profiles

### Software

```yaml

encoder:- **Raspberry Pi OS** (Debian Bookworm or newer)### 🌐 Web Interface

  profiles:

    category_1_2:               # Kids + Audiobooks- **Python 3.8+**

      format: mp3

      bitrate: 320- **Root Access** (for systemd service)- **Real-time Status**: Live display of ripping progress### 🎯 Kern-Funktionen3. In das gewünschte Format konvertiert (FLAC, MP3)

    category_3:                 # Music

      format: flac

      compression_level: 8

```## 🚀 Installation- **Cover Display**: Shows album cover during ripping



---



## Usage### 1. Clone Repository- **Progress Tracking**: Detailed progress display per track- **Automatische CD-Erkennung**: Erkennt eingelegte Audio-CDs automatisch4. Metadaten und Cover einbettet



### Automatic Mode

1. Insert CD → Service detects automatically

2. Watch progress in web interface```bash- **Settings Editor**: All parameters adjustable via web UI

3. CD is ejected when done

4. Files are on your servercd ~



### Service Managementgit clone https://github.com/dmyrenne/cd-ripper.git- **Mobile-Optimized**: Responsive design for smartphone/tablet- **MusicBrainz Integration**: Identifiziert CDs und lädt Metadaten + Cover-Art5. Automatisch auf einen lokalen Server synchronisiert



```bashcd cd-ripper

sudo systemctl status cd-ripper    # Check status

sudo systemctl restart cd-ripper   # Restart```- **Live Logs**: Real-time log display in browser

sudo journalctl -u cd-ripper -f    # View logs

```



### Web Interface### 2. Install System Dependencies- **Intelligente Kategorisierung**: 



Open `http://<ip>:5000`:

- **Main page** - Status, progress, cover art

- **Settings** - Edit all configuration```bash### 🔧 Technical Features  - Kategorie 1: Kinderinhalte (Hörspiele, Kindermusik)

- **Logs** - Real-time log viewer

sudo apt-get update

---

sudo apt-get install -y \- **Systemd Service**: Automatic start on boot  - Kategorie 2: Hörbücher für Erwachsene

## Requirements

    cdparanoia \

**Hardware:**

- Raspberry Pi 4 (2GB+ RAM)    flac \- **Fault Tolerance**: Retry logic and robust error handling  - Kategorie 3: Musik

- USB CD/DVD drive

- Network connection    lame \



**Software:**    ffmpeg \- **Status Persistence**: SharedStatus via JSON file with fcntl locking- **Format-Optimierung**:

- Raspberry Pi OS (Debian Bookworm+)

- Python 3.8+    libdiscid0 \

- Root access (for systemd)

    rsync \- **Configurable**: YAML-based configuration  - Kategorien 1+2: MP3 @ 320 kbit/s (platzsparend)

---

    sshpass \

## Troubleshooting

    eject \- **Complete Logging**: Audit trail of all operations  - Kategorie 3: FLAC Lossless (maximale Qualität)

### CD not detected

```bash    python3-pip \

lsblk | grep sr0              # Check if drive exists

cdparanoia -vsQ               # Test drive    python3-venv- **Server-Synchronisation**: Automatischer Upload auf NAS/Server via rsync

```

```

### Service won't start

```bash## 📋 Requirements- **Auto-Cleanup**: Lokale Dateien werden nach Upload gelöscht

sudo journalctl -u cd-ripper -n 50          # Check logs

python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"  # Validate config### 3. Create Python Virtual Environment

```



### Sync fails

```bash```bash

ssh user@host                 # Test SSH connection

rsync -avz /tmp/test user@host:/path/  # Test rsyncpython3 -m venv venv### Hardware### 🌐 Web-Interface

```

source venv/bin/activate

### Web interface not accessible

```bashpip install -r requirements.txt- **Raspberry Pi 4** (or similar, min. 2GB RAM recommended)- **Echtzeit-Status**: Live-Anzeige des Ripping-Fortschritts

sudo netstat -tlnp | grep 5000   # Check if port is listening

curl http://localhost:5000        # Test locally```

```

- **USB CD/DVD Drive**- **Cover-Anzeige**: Zeigt Album-Cover während des Rippings

---

### 4. Create Configuration

## Project Structure

- **Network Access** for MusicBrainz and server sync- **Progress-Tracking**: Detaillierte Fortschrittsanzeige pro Track

```

cd-ripper/```bash

├── src/                    # Python source code

│   ├── main.py            # Main service loopcp config/config.yaml.example config/config.yaml- **Einstellungs-Editor**: Alle Parameter über Web-UI anpassbar

│   ├── service.py         # Service launcher

│   ├── cd_detector.py     # Hardware detectionnano config/config.yaml

│   ├── cd_identifier.py   # MusicBrainz API

│   ├── cd_categorizer.py  # Category logic```### Software- **Mobile-optimiert**: Responsive Design für Smartphone/Tablet

│   ├── ripper.py          # cdparanoia wrapper

│   ├── encoder.py         # Audio conversion

│   ├── tagger.py          # Metadata tagging

│   ├── syncer.py          # Server sync**Important Settings:**- **Raspberry Pi OS** (Debian Bookworm or newer)- **Live-Logs**: Echtzeit-Log-Anzeige im Browser

│   └── web_interface.py   # Flask web app

├── web/                    # Web interface

│   ├── static/            # CSS, JS, i18n

│   └── templates/         # HTML templates```yaml- **Python 3.8+**

├── config/

│   └── config.yaml.exampleripper:

├── tests/                  # Test scripts

├── docs/                   # Documentation  device: /dev/sr0  # Your CD drive- **Root Access** (for systemd service)### 🔧 Technische Features

└── cd-ripper.service      # Systemd unit file

```  



---sync:- **Systemd-Service**: Automatischer Start beim Boot



## Security  enabled: true



**Use SSH keys instead of passwords:**  host: 10.10.1.3  # Your NAS/Server## 🚀 Installation- **Fehlertoleranz**: Retry-Logik und robustes Error-Handling



```bash  user: your_username

ssh-keygen -t ed25519

ssh-copy-id user@server  password: your_password  # Better: Use SSH keys!- **Status-Persistence**: SharedStatus via JSON-File mit fcntl-Locking

# Remove password from config.yaml

```  remote_paths:



**Restrict web interface access:**    category_1: /path/to/kids### 1. Clone Repository- **Konfigurierbar**: YAML-basierte Konfiguration



```bash    category_2: /path/to/audiobooks

sudo ufw allow from 192.168.1.0/24 to any port 5000

```    category_3: /path/to/music- **Vollständiges Logging**: Audit-Trail aller Operationen



---



## Developmentoutput:```bash



### Adding Languages  local_path: /mnt/dietpi_userdata/rips  # Local output



Edit `web/static/i18n.js`:cd ~## 📋 Voraussetzungen



```javascriptweb_interface:

const translations = {

    en: { /* English */ },  port: 5000git clone https://github.com/dmyrenne/cd-ripper.git

    de: { /* German */ },

    fr: { /* Add French */ }  language: en  # en (English) or de (Deutsch)

};

``````cd cd-ripper### Hardware



See [docs/INTERNATIONALIZATION.md](docs/INTERNATIONALIZATION.md) for details.



### Running Tests### 5. Install Service```- **Raspberry Pi 4** (oder ähnlich, min. 2GB RAM empfohlen)



```bash

python3 tests/test_web_updates.py   # Simulated test

``````bash- **USB CD/DVD-Laufwerk**



---sudo ./install-service.sh



## Credits```### 2. Install System Dependencies- **Netzwerk-Zugang** für MusicBrainz und Server-Sync



- **cdparanoia** - CD ripping with error correction

- **MusicBrainz** - CD metadata database

- **Flask** - Web frameworkThe script:

- **mutagen** - Audio tagging

- Copies the systemd service file

---

- Enables auto-start on boot```bash### Software

## License

- Starts the service

MIT License - see [LICENSE](LICENSE)

sudo apt-get update- **Raspberry Pi OS** (Debian Bookworm oder neuer)

## Support

### 6. Open Web Interface

- **Issues:** [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)

- **Discussions:** [GitHub Discussions](https://github.com/dmyrenne/cd-ripper/discussions)sudo apt-get install -y \- **Python 3.8+**



---```



**Made with ❤️ for music lovers | Runs on Raspberry Pi 4**http://<raspberry-pi-ip>:5000    cdparanoia \- **Root-Zugriff** (für systemd-Service)


```

    flac \

**Default Port**: 5000 (configurable in config.yaml)

    lame \## 🚀 Installation

## 🎮 Usage

    ffmpeg \

### Automatic Operation

    libdiscid0 \### 1. Repository klonen

1. **Insert CD** → Service detects CD automatically

2. **Identification** → MusicBrainz query for metadata    rsync \

3. **Categorization** → Automatic assignment

4. **Ripping** → cdparanoia extracts audio    sshpass \```bash

5. **Encoding** → Conversion to target format

6. **Tagging** → Embed metadata + cover    eject \cd ~

7. **Sync** → Upload to server

8. **Cleanup** → Delete local files    python3-pip \git clone https://github.com/dmyrenne/cd-ripper.git

9. **Eject** → Automatically eject CD

    python3-venvcd cd-ripper

### Manual Operation

``````

#### Service Commands



```bash

# Start service### 3. Create Python Virtual Environment### 2. System-Dependencies installieren

sudo systemctl start cd-ripper



# Stop service

sudo systemctl stop cd-ripper```bash```bash



# Restart servicepython3 -m venv venvsudo apt-get update

sudo systemctl restart cd-ripper

source venv/bin/activatesudo apt-get install -y \

# Check status

sudo systemctl status cd-ripperpip install -r requirements.txt    cdparanoia \



# Disable auto-start```    flac \

sudo systemctl disable cd-ripper

    lame \

# Enable auto-start

sudo systemctl enable cd-ripper### 4. Create Configuration    ffmpeg \

```

    libdiscid0 \

#### View Logs

```bash    rsync \

```bash

# Live logscp config/config.yaml.example config/config.yaml    sshpass \

sudo journalctl -u cd-ripper -f

nano config/config.yaml    eject \

# Last 100 lines

sudo journalctl -u cd-ripper -n 100```    python3-pip \



# Log file directly    python3-venv

tail -f ~/cd-ripper/logs/ripper.log

```**Important Settings:**```



#### Manually Eject CD



```bash```yaml### 3. Python Virtual Environment erstellen

# Via web interface: "Eject" button

# Or terminal:ripper:

eject /dev/sr0

```  device: /dev/sr0  # Your CD drive```bash



## ⚙️ Configuration  python3 -m venv venv



### Via Web Interfacesync:source venv/bin/activate



1. Open `http://<ip>:5000`  enabled: truepip install -r requirements.txt

2. Click on "⚙️ Settings"

3. Edit settings  host: 10.10.1.3  # Your NAS/Server```

4. Click "💾 Save & Restart"

  user: your_username

### Via Config File

  password: your_password  # Better: Use SSH keys!### 4. Konfiguration erstellen

```bash

nano ~/cd-ripper/config/config.yaml  remote_paths:

sudo systemctl restart cd-ripper

```    category_1: /path/to/kids```bash



### Important Parameters    category_2: /path/to/audiobookscp config/config.yaml.example config/config.yaml



#### Ripper Settings    category_3: /path/to/musicnano config/config.yaml

```yaml

ripper:```

  device: /dev/sr0        # CD drive

  quality: paranoia       # paranoia, normal, fastoutput:

```

  local_path: /mnt/dietpi_userdata/rips  # Local output**Wichtige Einstellungen:**

#### Encoding Profiles

```yaml```

encoder:

  profiles:```yaml

    category_1_2:         # Kids + Audiobooks

      format: mp3### 5. Install Serviceripper:

      bitrate: 320

    category_3:           # Music  device: /dev/sr0  # Dein CD-Laufwerk

      format: flac

      compression_level: 8```bash  

```

sudo ./install-service.shsync:

#### Server Sync

```yaml```  enabled: true

sync:

  enabled: true  host: 192.168.1.213  # Dein NAS/Server

  host: 10.10.1.3

  user: dietpiThe script:  user: dein_username

  cleanup: true           # Delete local files

  auto_eject: true        # Eject CD after sync- Copies the systemd service file  password: dein_passwort  # Besser: SSH-Keys nutzen!

```

- Enables auto-start on boot  remote_paths:

#### Web Interface

```yaml- Starts the service    category_1: /pfad/zu/Kinderinhalte

web_interface:

  enabled: true    category_2: /pfad/zu/Hörbücher

  host: "0.0.0.0"

  port: 5000### 6. Open Web Interface    category_3: /pfad/zu/Musik

  language: en            # en (English), de (Deutsch)

```



### Language Settings```output:



The web interface supports multiple languages:http://<raspberry-pi-ip>:5000  local_path: /mnt/dietpi_userdata/rips  # Lokaler Output



- **English (en)** - Default``````

- **Deutsch (de)** - German



Change language via:

1. Settings page → Web Interface section → Language dropdown**Default Port**: 5000 (configurable in config.yaml)### 5. Service installieren

2. Or edit `config/config.yaml` → `web_interface.language`



For developers: See [INTERNATIONALIZATION.md](docs/INTERNATIONALIZATION.md) for adding new languages.

## 🎮 Usage```bash

## 📂 Project Structure

sudo ./install-service.sh

```

cd-ripper/### Automatic Operation```

├── config/

│   ├── config.yaml              # Active configuration (not in repo)

│   └── config.yaml.example      # Example configuration

├── docs/1. **Insert CD** → Service detects CD automaticallyDas Script:

│   ├── INTERNATIONALIZATION.md  # i18n documentation

│   ├── screenshots/             # Screenshots for README2. **Identification** → MusicBrainz query for metadata- Kopiert die systemd-Service-Datei

│   └── STATUS-MANAGEMENT.md     # Technical documentation

├── logs/3. **Categorization** → Automatic assignment- Aktiviert Auto-Start beim Boot

│   └── ripper.log              # Service logs

├── output/                      # Temporary ripped CDs (gets cleared)4. **Ripping** → cdparanoia extracts audio- Startet den Service

├── src/

│   ├── main.py                 # Main service5. **Encoding** → Conversion to target format

│   ├── service.py              # Service launcher

│   ├── cd_detector.py          # Hardware detection6. **Tagging** → Embed metadata + cover### 6. Web-Interface öffnen

│   ├── cd_identifier.py        # MusicBrainz integration

│   ├── cd_categorizer.py       # Categorization logic7. **Sync** → Upload to server

│   ├── ripper.py               # cdparanoia wrapper

│   ├── encoder.py              # Audio conversion8. **Cleanup** → Delete local files```

│   ├── tagger.py               # Metadata tagging

│   ├── syncer.py               # Server sync9. **Eject** → Automatically eject CDhttp://<raspberry-pi-ip>:5000

│   ├── web_interface.py        # Flask web app

│   ├── shared_status.py        # IPC mechanism```

│   └── utils.py                # Helper functions

├── tests/### Manual Operation

│   ├── test_simulate_rip.py    # Simulation test

│   └── test_web_updates.py     # Web interface test**Standard-Port**: 5000 (in config.yaml änderbar)

├── web/

│   ├── static/#### Service Commands

│   │   ├── app.js              # Frontend logic

│   │   ├── settings.js         # Settings editor## 🎮 Verwendung

│   │   ├── i18n.js             # Internationalization

│   │   └── style.css           # Design```bash

│   └── templates/

│       ├── index.html          # Main page# Start service### Automatischer Betrieb

│       └── settings.html       # Settings

├── cd-ripper.service           # systemd service filesudo systemctl start cd-ripper

├── install-service.sh          # Installation script

├── uninstall-service.sh        # Uninstallation script1. **CD einlegen** → Service erkennt CD automatisch

├── requirements.txt            # Python dependencies

└── README.md                   # This file# Stop service2. **Identifikation** → MusicBrainz-Abfrage für Metadaten

```

sudo systemctl stop cd-ripper3. **Kategorisierung** → Automatische Zuordnung

## 🐛 Troubleshooting

4. **Ripping** → cdparanoia extrahiert Audio

### CD Not Detected

# Restart service5. **Encoding** → Konvertierung in Zielformat

```bash

# Check if drive is recognizedsudo systemctl restart cd-ripper6. **Tagging** → Metadaten + Cover einbetten

lsblk | grep sr0

7. **Sync** → Upload auf Server

# Test cdparanoia directly

cdparanoia -vsQ# Check status8. **Cleanup** → Lokale Dateien löschen



# Check device in configsudo systemctl status cd-ripper9. **Eject** → CD automatisch auswerfen

cat config/config.yaml | grep device

```



### Service Won't Start# Disable auto-start### Manuelles Bedienen



```bashsudo systemctl disable cd-ripper

# Check logs

sudo journalctl -u cd-ripper -n 50#### Service-Befehle



# Check config syntax# Enable auto-start

python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

sudo systemctl enable cd-ripper```bash

# Test manually

cd ~/cd-ripper```# Service starten

source venv/bin/activate

python3 src/service.pysudo systemctl start cd-ripper

```

#### View Logs

### MusicBrainz Can't Find CD

# Service stoppen

- Check internet connection

- Some CDs are not in MusicBrainz```bashsudo systemctl stop cd-ripper

- Manual assignment via web interface possible (planned)

# Live logs

### Server Sync Fails

sudo journalctl -u cd-ripper -f# Service neu starten

```bash

# Test rsync manuallysudo systemctl restart cd-ripper

rsync -avz --progress /path/to/file user@host:/path/

# Last 100 lines

# Check SSH access

ssh user@hostsudo journalctl -u cd-ripper -n 100# Status prüfen



# Check sshpasssudo systemctl status cd-ripper

which sshpass

# Log file directly

# Better: SSH keys instead of password

ssh-copy-id user@hosttail -f ~/cd-ripper/logs/ripper.log# Auto-Start deaktivieren

# Then remove password from config.yaml

``````sudo systemctl disable cd-ripper



### Web Interface Not Accessible



```bash#### Manually Eject CD# Auto-Start aktivieren

# Check if service is running

sudo systemctl status cd-rippersudo systemctl enable cd-ripper



# Check port```bash```

sudo netstat -tlnp | grep 5000

# Via web interface: "Eject" button

# Check firewall

sudo ufw status# Or terminal:#### Logs anschauen



# Test locallyeject /dev/sr0

curl http://localhost:5000

`````````bash



### Wrong Language Display# Live-Logs



```bash## ⚙️ Configurationsudo journalctl -u cd-ripper -f

# Clear browser cache and localStorage

# Then change language in settings



# Or edit config directly### Via Web Interface# Letzte 100 Zeilen

nano config/config.yaml

# web_interface:sudo journalctl -u cd-ripper -n 100

#   language: en  # or de

```1. Open `http://<ip>:5000`



## 🔒 Security2. Click on "⚙️ Settings"# Log-Datei direkt



### SSH Keys Instead of Password (Recommended)3. Edit settingstail -f ~/cd-ripper/logs/ripper.log



```bash4. Click "💾 Save & Restart"```

# Generate SSH key

ssh-keygen -t ed25519



# Copy key to server### Via Config File#### CD manuell auswerfen

ssh-copy-id user@server



# In config.yaml: remove or leave password field empty

``````bash```bash



### Firewallnano ~/cd-ripper/config/config.yaml# Via Web-Interface: Button "Auswerfen"



```bashsudo systemctl restart cd-ripper# Oder Terminal:

# Only allow from local network

sudo ufw allow from 192.168.1.0/24 to any port 5000```eject /dev/sr0

```

```

### Permissions

### Important Parameters

```bash

# Protect config from other users (because of password)## ⚙️ Konfiguration

chmod 600 ~/cd-ripper/config/config.yaml

```#### Ripper Settings



## 🛠️ Development```yaml### Via Web-Interface



### Run Testsripper:



```bash  device: /dev/sr0        # CD drive1. Öffne `http://<ip>:5000`

# Simulation test (without real CD)

python3 tests/test_web_updates.py  quality: paranoia       # paranoia, normal, fast2. Klicke auf "⚙️ Einstellungen"



# Playwright browser test```3. Bearbeite Einstellungen

# (requires playwright-mcp)

```4. Klicke "💾 Speichern & Neu starten"



### Adding New Languages#### Encoding Profiles



See [INTERNATIONALIZATION.md](docs/INTERNATIONALIZATION.md) for detailed instructions on adding translations.```yaml### Via Konfig-Datei



Quick example:encoder:



1. Edit `web/static/i18n.js`  profiles:```bash

2. Add new language object:

```javascript    category_1_2:         # Kids + Audiobooksnano ~/cd-ripper/config/config.yaml

fr: {

    'app_title': 'CD-Ripper',      format: mp3sudo systemctl restart cd-ripper

    'btn_eject': 'Éjecter',

    // ... more translations      bitrate: 320```

}

```    category_3:           # Music

3. Add option to language selector in settings

4. Test thoroughly      format: flac### Wichtige Parameter



### New Features      compression_level: 8



1. Fork the repository```#### Ripper-Einstellungen

2. Create feature branch: `git checkout -b feature/name`

3. Commit changes: `git commit -m 'Add feature'````yaml

4. Push branch: `git push origin feature/name`

5. Open pull request#### Server Syncripper:



## 📝 To-Do / Planned Features```yaml  device: /dev/sr0        # CD-Laufwerk



- [ ] ST7789 display support for standalone operationsync:  quality: paranoia       # paranoia, normal, fast

- [ ] SSH key authentication without password

- [ ] Multi-CD batch processing  enabled: true```

- [ ] Manual metadata editing in web interface

- [ ] Cover art upload for CDs without MusicBrainz entry  host: 10.10.1.3

- [ ] Statistics (ripped CDs, storage space, etc.)

- [ ] Email notifications on errors  user: dietpi#### Encoding-Profile

- [ ] Docker container for easy installation

- [ ] More languages (French, Spanish, etc.)  cleanup: true           # Delete local files```yaml

- [ ] Dark mode theme

  auto_eject: true        # Eject CD after syncencoder:

## 🙏 Credits

```  profiles:

### Dependencies

- [cdparanoia](https://www.xiph.org/paranoia/) - CD ripping with error correction    category_1_2:         # Kinder + Hörbücher

- [MusicBrainz](https://musicbrainz.org/) - CD identification & metadata

- [Flask](https://flask.palletsprojects.com/) - Web framework## 📂 Project Structure      format: mp3

- [mutagen](https://mutagen.readthedocs.io/) - Audio tagging

      bitrate: 320

### Inspiration

- Inspired by classic CD ripping tools like K3b, Grip and abcde```    category_3:           # Musik

- Web interface design inspired by modern admin panels

cd-ripper/      format: flac

## 📄 License

├── config/      compression_level: 8

MIT License - see [LICENSE](LICENSE) file for details

│   ├── config.yaml              # Active configuration (not in repo)```

## 🤝 Support

│   └── config.yaml.example      # Example configuration

- **Issues**: [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)

- **Discussions**: [GitHub Discussions](https://github.com/dmyrenne/cd-ripper/discussions)├── docs/#### Server-Sync

- **Wiki**: [GitHub Wiki](https://github.com/dmyrenne/cd-ripper/wiki)

│   ├── screenshots/             # Screenshots for README```yaml

## 🌟 Contributors

│   └── STATUS-MANAGEMENT.md     # Technical documentationsync:

- Daniel Myrenne - Initial Work - [@dmyrenne](https://github.com/dmyrenne)

├── logs/  enabled: true

---

│   └── ripper.log              # Service logs  host: 10.10.1.3

**Made with ❤️ for music lovers and audiobook enthusiasts**

├── output/                      # Temporary ripped CDs (gets cleared)  user: dietpi

*CD-Ripper runs stable on Raspberry Pi 4 with Raspberry Pi OS (Debian Bookworm)*

├── src/  cleanup: true           # Lokale Dateien löschen

│   ├── main.py                 # Main service  auto_eject: true        # CD nach Sync auswerfen

│   ├── service.py              # Service launcher```

│   ├── cd_detector.py          # Hardware detection

│   ├── cd_identifier.py        # MusicBrainz integration## 📂 Projektstruktur

│   ├── cd_categorizer.py       # Categorization logic

│   ├── ripper.py               # cdparanoia wrapper```

│   ├── encoder.py              # Audio conversioncd-ripper/

│   ├── tagger.py               # Metadata tagging├── config/

│   ├── syncer.py               # Server sync│   ├── config.yaml              # Aktive Konfiguration (nicht im Repo)

│   ├── web_interface.py        # Flask web app│   └── config.yaml.example      # Beispiel-Konfiguration

│   ├── shared_status.py        # IPC mechanism├── docs/

│   └── utils.py                # Helper functions│   ├── screenshots/             # Screenshots für README

├── tests/│   └── STATUS-MANAGEMENT.md     # Technische Doku

│   ├── test_simulate_rip.py    # Simulation test├── logs/

│   └── test_web_updates.py     # Web interface test│   └── ripper.log              # Service-Logs

├── web/├── output/                      # Temporäre gerippte CDs (wird geleert)

│   ├── static/├── src/

│   │   ├── app.js              # Frontend logic│   ├── main.py                 # Haupt-Service

│   │   ├── settings.js         # Settings editor│   ├── service.py              # Service-Launcher

│   │   └── style.css           # Design│   ├── cd_detector.py          # Hardware-Erkennung

│   └── templates/│   ├── cd_identifier.py        # MusicBrainz Integration

│       ├── index.html          # Main page│   ├── cd_categorizer.py       # Kategorisierungs-Logik

│       └── settings.html       # Settings│   ├── ripper.py               # cdparanoia Wrapper

├── cd-ripper.service           # systemd service file│   ├── encoder.py              # Audio-Konvertierung

├── install-service.sh          # Installation script│   ├── tagger.py               # Metadaten-Tagging

├── uninstall-service.sh        # Uninstallation script│   ├── syncer.py               # Server-Sync

├── requirements.txt            # Python dependencies│   ├── web_interface.py        # Flask Web-App

└── README.md                   # This file│   ├── shared_status.py        # IPC-Mechanismus

```│   └── utils.py                # Helper-Funktionen

├── tests/

## 🐛 Troubleshooting│   ├── test_simulate_rip.py    # Simulations-Test

│   └── test_web_updates.py     # Web-Interface Test

### CD Not Detected├── web/

│   ├── static/

```bash│   │   ├── app.js              # Frontend-Logik

# Check if drive is recognized│   │   ├── settings.js         # Settings-Editor

lsblk | grep sr0│   │   └── style.css           # Design

│   └── templates/

# Test cdparanoia directly│       ├── index.html          # Hauptseite

cdparanoia -vsQ│       └── settings.html       # Einstellungen

├── cd-ripper.service           # systemd Service-Datei

# Check device in config├── install-service.sh          # Installations-Script

cat config/config.yaml | grep device├── uninstall-service.sh        # Deinstallations-Script

```├── requirements.txt            # Python-Dependencies

└── README.md                   # Diese Datei

### Service Won't Start```



```bash## 🐛 Troubleshooting

# Check logs

sudo journalctl -u cd-ripper -n 50### CD wird nicht erkannt



# Check config syntax```bash

python3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"# Prüfe ob Laufwerk erkannt wird

lsblk | grep sr0

# Test manually

cd ~/cd-ripper# Teste cdparanoia direkt

source venv/bin/activatecdparanoia -vsQ

python3 src/service.py

```# Prüfe Device in Config

cat config/config.yaml | grep device

### MusicBrainz Can't Find CD```



- Check internet connection### Service startet nicht

- Some CDs are not in MusicBrainz

- Manual assignment via web interface possible (planned)```bash

# Prüfe Logs

### Server Sync Failssudo journalctl -u cd-ripper -n 50



```bash# Prüfe Config-Syntax

# Test rsync manuallypython3 -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

rsync -avz --progress /path/to/file user@host:/path/

# Teste manuell

# Check SSH accesscd ~/cd-ripper

ssh user@hostsource venv/bin/activate

python3 src/service.py

# Check sshpass```

which sshpass

### MusicBrainz findet CD nicht

# Better: SSH keys instead of password

ssh-copy-id user@host- Prüfe Internet-Verbindung

# Then remove password from config.yaml- Manche CDs sind nicht in MusicBrainz

```- Manuelle Zuordnung über Web-Interface möglich (geplant)



### Web Interface Not Accessible### Server-Sync schlägt fehl



```bash```bash

# Check if service is running# Teste rsync manuell

sudo systemctl status cd-ripperrsync -avz --progress /pfad/zu/datei user@host:/pfad/



# Check port# Prüfe SSH-Zugang

sudo netstat -tlnp | grep 5000ssh user@host



# Check firewall# Prüfe sshpass

sudo ufw statuswhich sshpass



# Test locally# Besser: SSH-Keys statt Passwort

curl http://localhost:5000ssh-copy-id user@host

```# Dann password in config.yaml entfernen

```

## 🔒 Security

### Web-Interface nicht erreichbar

### SSH Keys Instead of Password (Recommended)

```bash

```bash# Prüfe ob Service läuft

# Generate SSH keysudo systemctl status cd-ripper

ssh-keygen -t ed25519

# Prüfe Port

# Copy key to serversudo netstat -tlnp | grep 5000

ssh-copy-id user@server

# Prüfe Firewall

# In config.yaml: remove or leave password field emptysudo ufw status

```

# Teste lokal

### Firewallcurl http://localhost:5000

```

```bash

# Only allow from local network## 🔒 Sicherheit

sudo ufw allow from 192.168.1.0/24 to any port 5000

```### SSH-Keys statt Passwort (empfohlen)



### Permissions```bash

# SSH-Key generieren

```bashssh-keygen -t ed25519

# Protect config from other users (because of password)

chmod 600 ~/cd-ripper/config/config.yaml# Key zum Server kopieren

```ssh-copy-id user@server



## 🛠️ Development# In config.yaml: password-Feld entfernen oder leer lassen

```

### Run Tests

### Firewall

```bash

# Simulation test (without real CD)```bash

python3 tests/test_web_updates.py# Nur aus lokalem Netzwerk erlauben

sudo ufw allow from 192.168.1.0/24 to any port 5000

# Playwright browser test```

# (requires playwright-mcp)

```### Berechtigungen



### New Features```bash

# Config vor anderen Nutzern schützen (wegen Passwort)

1. Fork the repositorychmod 600 ~/cd-ripper/config/config.yaml

2. Create feature branch: `git checkout -b feature/name````

3. Commit changes: `git commit -m 'Add feature'`

4. Push branch: `git push origin feature/name`## 🛠️ Entwicklung

5. Open pull request

### Tests ausführen

## 📝 To-Do / Planned Features

```bash

- [ ] ST7789 display support for standalone operation# Simulationstest (ohne echte CD)

- [ ] SSH key authentication without passwordpython3 tests/test_web_updates.py

- [ ] Multi-CD batch processing

- [ ] Manual metadata editing in web interface# Playwright-Browser-Test

- [ ] Cover art upload for CDs without MusicBrainz entry# (erfordert playwright-mcp)

- [ ] Statistics (ripped CDs, storage space, etc.)```

- [ ] Email notifications on errors

- [ ] Docker container for easy installation### Neue Features



## 🙏 Credits1. Fork das Repository

2. Feature-Branch erstellen: `git checkout -b feature/name`

### Dependencies3. Änderungen committen: `git commit -m 'Add feature'`

- [cdparanoia](https://www.xiph.org/paranoia/) - CD ripping with error correction4. Branch pushen: `git push origin feature/name`

- [MusicBrainz](https://musicbrainz.org/) - CD identification & metadata5. Pull Request öffnen

- [Flask](https://flask.palletsprojects.com/) - Web framework

- [mutagen](https://mutagen.readthedocs.io/) - Audio tagging## 📝 To-Do / Geplante Features



### Inspiration- [ ] ST7789 Display-Unterstützung für Standalone-Betrieb

- Inspired by classic CD ripping tools like K3b, Grip and abcde- [ ] SSH-Key-Authentication ohne Passwort

- Web interface design inspired by modern admin panels- [ ] Multi-CD-Batch-Processing

- [ ] Manuelle Metadaten-Bearbeitung im Web-Interface

## 📄 License- [ ] Cover-Art Upload für CDs ohne MusicBrainz-Eintrag

- [ ] Statistiken (gerippte CDs, Speicherplatz, etc.)

MIT License - see [LICENSE](LICENSE) file for details- [ ] Email-Benachrichtigungen bei Fehlern

- [ ] Docker-Container für einfache Installation

## 🤝 Support

## 🙏 Credits

- **Issues**: [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)

- **Discussions**: [GitHub Discussions](https://github.com/dmyrenne/cd-ripper/discussions)### Dependencies

- **Wiki**: [GitHub Wiki](https://github.com/dmyrenne/cd-ripper/wiki)- [cdparanoia](https://www.xiph.org/paranoia/) - CD-Ripping mit Fehlerkorrektur

- [MusicBrainz](https://musicbrainz.org/) - CD-Identifikation & Metadaten

## 🌟 Contributors- [Flask](https://flask.palletsprojects.com/) - Web-Framework

- [mutagen](https://mutagen.readthedocs.io/) - Audio-Tagging

- Daniel Myrenne - Initial Work - [@dmyrenne](https://github.com/dmyrenne)

### Inspiration

---- Inspiriert von klassischen CD-Ripping-Tools wie K3b, Grip und abcde

- Web-Interface Design angelehnt an moderne Admin-Panels

**Made with ❤️ for music lovers and audiobook enthusiasts**

## 📄 Lizenz

*CD-Ripper runs stable on Raspberry Pi 4 with Raspberry Pi OS (Debian Bookworm)*

MIT License - siehe [LICENSE](LICENSE) Datei für Details

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)
- **Diskussionen**: [GitHub Discussions](https://github.com/dmyrenne/cd-ripper/discussions)
- **Wiki**: [GitHub Wiki](https://github.com/dmyrenne/cd-ripper/wiki)

## 🌟 Contributors

- Daniel Myrenne - Initial Work - [@dmyrenne](https://github.com/dmyrenne)
- Copilot - Sonnet 4.5 - Heavy lifting

---

**Made with ❤️ for music lovers and audiobook enthusiasts**

*CD-Ripper läuft stabil auf Raspberry Pi 4 mit Raspberry Pi OS (Debian Bookworm)*
