# CD-Ripper

Automatic CD ripping service that detects audio CDs, identifies them via MusicBrainz, rips to MP3/FLAC, and syncs to your server.

## Installation

```bash
# Clone repository
git clone https://github.com/dmyrenne/cd-ripper.git
cd cd-ripper

# Install system dependencies
sudo apt-get update
sudo apt-get install -y cdparanoia flac lame ffmpeg libdiscid0 rsync sshpass eject python3-pip python3-venv

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp config/config.yaml.example config/config.yaml
nano config/config.yaml
# Edit: device (/dev/sr0), server host, user, password, remote paths

# Install and start service
sudo ./install-service.sh
```

## Usage

Web interface: `http://<raspberry-pi-ip>:5000`

Service commands:
```bash
sudo systemctl status cd-ripper
sudo systemctl restart cd-ripper
sudo journalctl -u cd-ripper -f
```

## License

MIT
