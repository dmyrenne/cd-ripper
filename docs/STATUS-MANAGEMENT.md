# CD-Ripper Status-Management

## Status-Verhalten

### Automatische Status-Updates

Der Service aktualisiert den Status automatisch:

1. **CD eingelegt** → Status zeigt CD-Info + Cover
2. **Ripping läuft** → Progress-Updates in Echtzeit
3. **CD entfernt** → Status wird automatisch gelöscht

### Status-Zustände

```javascript
// Keine CD eingelegt
{
  "current_cd": null,
  "processing": false,
  "current_step": null,
  "progress": 0
}

// CD erkannt, wartet auf Verarbeitung
{
  "current_cd": {
    "name": "Album Name",
    "artist": "Künstler",
    "cover_url": "/api/cover"
  },
  "processing": false
}

// Verarbeitung läuft
{
  "current_cd": {...},
  "processing": true,
  "current_step": "ripping",  // ripping, encoding, tagging, syncing
  "progress": 45,
  "current_track": 5,
  "total_tracks": 12
}
```

### Web-Interface Verhalten

Das Web-Interface (http://localhost:5000) aktualisiert sich **alle 2 Sekunden** automatisch:

- **Keine CD**: Zeigt "Keine CD eingelegt" + Placeholder
- **CD eingelegt**: Zeigt Album + Artist + Cover
- **Ripping läuft**: Zeigt zusätzlich Progress-Bar + Warnung
- **CD entfernt**: Wechselt sofort zu "Keine CD eingelegt"

### Manuelles Status-Management

```bash
# Status anzeigen
cat /tmp/cd-ripper-status.json | python3 -m json.tool

# Status manuell löschen (falls nötig)
python3 -c "from src.shared_status import SharedStatus; SharedStatus().clear()"

# Cover anzeigen
ls -lh /tmp/current-cover.jpg
```

### Debugging

```bash
# Service-Logs live anschauen
sudo journalctl -u cd-ripper -f

# Letzte 50 Zeilen
sudo journalctl -u cd-ripper -n 50

# Ripper-Log anschauen
tail -f /root/projects/cd-ripper/logs/ripper.log
```

### Status-Datei

- **Pfad**: `/tmp/cd-ripper-status.json`
- **Locking**: fcntl (thread-safe)
- **Cover**: `/tmp/current-cover.jpg` (wird bei neuer CD überschrieben)
- **Persistenz**: Im RAM (/tmp), geht bei Reboot verloren (gewollt)

### Automatisches Cleanup

Der Service räumt automatisch auf:

1. **CD entfernt** → Status wird gelöscht (current_cd = null)
2. **Reboot** → /tmp wird geleert, Service startet fresh
3. **Service-Neustart** → Alter Status bleibt erhalten (nützlich für Debugging)
