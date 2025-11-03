# 🚀 Quick Start Guide - CD-Ripper Installation

Quick installation guide for the CD-Ripper on a Raspberry Pi.

## Prerequisites

- Raspberry Pi 4 (min. 2GB RAM)
- Raspberry Pi OS (Debian Bookworm)
- USB CD/DVD Drive
- Internet Connection
- SSH Access to the Pi

## Installation in 5 Minutes

### 1. Clone Repository

```bash
ssh pi@<your-ip>
cd ~
git clone https://github.com/dmyrenne/cd-ripper.git
cd cd-ripper
```

### 2. Install Dependencies

```bash
# System packages
sudo apt-get update && sudo apt-get install -y \
    cdparanoia flac lame ffmpeg libdiscid0 rsync sshpass eject \
    python3-pip python3-venv

# Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy example config
cp config/config.yaml.example config/config.yaml

# Edit config
nano config/config.yaml
```

**Minimum Adjustments:**

```yaml
# Line ~3: CD drive
ripper:
  device: /dev/sr0  # Your drive

# Line ~30: Server settings
sync:
  host: 10.10.1.3      # Your NAS/Server
  user: your_username  # SSH user
  password: password   # Or use SSH key!
```

### 4. Install Service

```bash
sudo ./install-service.sh
```

### 5. Done! 🎉

Open web interface:
```
http://<raspberry-pi-ip>:5000
```

Insert CD and watch automatic ripping!

## First Steps

1. **Insert test CD** → Service detects automatically
2. **Open web interface** → Watch progress
3. **Adjust settings** → Button "⚙️ Settings"
4. **Check logs** → `sudo journalctl -u cd-ripper -f`

## Troubleshooting

### CD Not Detected

```bash
# Check drive
lsblk | grep sr0

# Test cdparanoia
cdparanoia -vsQ
```

### Service Not Running

```bash
# Check status
sudo systemctl status cd-ripper

# View logs
sudo journalctl -u cd-ripper -n 50
```

### Web Interface Not Accessible

```bash
# Check port
sudo netstat -tlnp | grep 5000

# Restart service
sudo systemctl restart cd-ripper
```

## Next Steps

- [Complete README](README.md)
- [Configuration](config/config.yaml.example)
- [Status Management](docs/STATUS-MANAGEMENT.md)

## Support

For issues: [GitHub Issues](https://github.com/dmyrenne/cd-ripper/issues)

---

**Happy ripping! 🎵💿**
