# ST7789 Display Integration

## Hardware

# ST7789 Display Integration

## Hardware

**Display:** ST7789 LCD (240x320, SPI)  
**Interface:** SPI  
**Wiring Reference:** [Adafruit 2.0" 320x240 Display - Wiring Guide](https://learn.adafruit.com/2-0-inch-320-x-240-color-ips-tft-display/python-wiring-and-setup)  
**Usage Examples:** [Python Usage Guide](https://learn.adafruit.com/2-0-inch-320-x-240-color-ips-tft-display/python-usage)

**Pins (Adafruit Standard Pinout):**
- Vin  → 3.3V (Pin 1)
- GND  → GND (Pin 6)
- CLK  → SPI0 SCLK (GPIO 11 / Pin 23)
- MOSI → SPI0 MOSI (GPIO 10 / Pin 19)
- CS   → CE0 (GPIO 8 / Pin 24)
- RST  → GPIO 24 (Pin 18)
- DC   → GPIO 25 (Pin 22)

## Installation

```bash
# Enable SPI
sudo raspi-config
# Interface Options → SPI → Enable

# Install system dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-dev python3.13-venv python3-pil

# Install Adafruit RGB Display library in virtual environment
cd /root/projects/cd-ripper
python3 -m venv venv
source venv/bin/activate
pip install adafruit-circuitpython-rgb-display

# Reboot
sudo reboot
```

## Configuration

Edit `config/config.yaml`:

```yaml
display:
  enabled: true
  width: 240
  height: 320
  rotation: 0    # 0, 90, 180, 270
```

## What is Displayed

### Idle (No CD)
- CD icon
- "Keine CD" text

### CD Detected
- Album cover (180x180)
- Album name
- Artist name

### Ripping/Processing
- Current step (Rippe, Kodiere, Tagge, Synchronisiere)
- Track number (Track 5/12)
- Progress bar
- Percentage

### Done
- Green checkmark
- "Fertig!" text

### Error
- Red error screen
- Error message

## Troubleshooting

### Display stays black
```bash
# Check SPI
ls /dev/spi*
# Should show: /dev/spidev0.0  /dev/spidev0.1

# Test manually
python3 << EOF
from ST7789 import ST7789
from PIL import Image
display = ST7789(port=0, cs=1, dc=9, backlight=13, rotation=0)
display.begin()
img = Image.new('RGB', (240, 240), color=(255, 0, 0))
display.display(img)
EOF
```

### Permission denied
```bash
sudo usermod -a -G spi,gpio $USER
# Logout and login again
```

### Wrong colors/orientation
Adjust `rotation` in config:
- 0 = normal
- 90 = rotated 90° clockwise
- 180 = upside down
- 270 = rotated 270° clockwise

## Disable Display

Set in `config/config.yaml`:
```yaml
display:
  enabled: false
```

Service will run without display functionality.
