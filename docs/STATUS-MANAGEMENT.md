# CD-Ripper Status Management

## Status Behavior

### Automatic Status Updates

The service updates the status automatically:

1. **CD inserted** → Status shows CD info + cover
2. **Ripping running** → Real-time progress updates
3. **CD removed** → Status is automatically cleared

### Status States

```javascript
// No CD inserted
{
  "current_cd": null,
  "processing": false,
  "current_step": null,
  "progress": 0
}

// CD detected, waiting for processing
{
  "current_cd": {
    "name": "Album Name",
    "artist": "Artist Name",
    "cover_url": "/api/cover"
  },
  "processing": false
}

// Processing in progress
{
  "current_cd": {...},
  "processing": true,
  "current_step": "ripping",  // ripping, encoding, tagging, syncing
  "progress": 45,
  "current_track": 5,
  "total_tracks": 12
}
```

### Web Interface Behavior

The web interface (http://localhost:5000) updates automatically **every 2 seconds**:

- **No CD**: Shows "No CD inserted" + Placeholder
- **CD inserted**: Shows Album + Artist + Cover
- **Ripping active**: Additionally shows progress bar + warning
- **CD removed**: Immediately switches to "No CD inserted"

### Manual Status Management

```bash
# Display status
cat /tmp/cd-ripper-status.json | python3 -m json.tool

# Manually clear status (if needed)
python3 -c "from src.shared_status import SharedStatus; SharedStatus().clear()"

# Display cover
ls -lh /tmp/current-cover.jpg
```

### Debugging

```bash
# Watch service logs live
sudo journalctl -u cd-ripper -f

# Last 50 lines
sudo journalctl -u cd-ripper -n 50

# Watch ripper log
tail -f /root/projects/cd-ripper/logs/ripper.log
```

### Status File

- **Path**: `/tmp/cd-ripper-status.json`
- **Locking**: fcntl (thread-safe)
- **Cover**: `/tmp/current-cover.jpg` (overwritten on new CD)
- **Persistence**: In RAM (/tmp), cleared on reboot (intentional)

### Automatic Cleanup

The service cleans up automatically:

1. **CD removed** → Status is cleared (current_cd = null)
2. **Reboot** → /tmp is cleared, service starts fresh
3. **Service restart** → Old status remains (useful for debugging)
