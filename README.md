**Disclaimer:** I can't code Python, so I completely generated this code with VS Code and the Copilot using Sonnet 4.5

# CD-Ripper

Automatic CD ripping service that detects audio CDs, identifies them via MusicBrainz, rips to MP3/FLAC, and syncs to your server.

## Installation

```bash
# Clone repository
git clone https://github.com/dmyrenne/cd-ripper.git
cd cd-ripper

# Install system dependencies
sudo apt-get update
sudo apt-get install -y cdparanoia flac lame ffmpeg libdiscid0 rsync sshpass eject python3-pip python3-venv build-essential python3-dev

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp config/config.yaml.example config/config.yaml
nano config/config.yaml
# Edit: device (/dev/sr0), server host, user, password, remote paths

# Optional: ST7789 Display (240x320 SPI)
# Connect display pins to Raspberry Pi GPIO (Adafruit Standard Pinout):
# https://learn.adafruit.com/2-0-inch-320-x-240-color-ips-tft-display/python-wiring-and-setup
# Display Vin  → Pin 1  (3.3V)
# Display GND  → Pin 6  (GND)
# Display CLK  → Pin 23 (GPIO 11 / SPI0 SCLK)
# Display MOSI → Pin 19 (GPIO 10 / SPI0 MOSI)
# Display CS   → Pin 24 (GPIO 8 / CE0)
# Display RST  → Pin 18 (GPIO 24)
# Display DC   → Pin 22 (GPIO 25)
# Enable SPI: sudo raspi-config → Interface Options → SPI → Enable
# Install Adafruit library: pip install adafruit-circuitpython-rgb-display (inside venv)
# Set display.enabled: true in config.yaml

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
