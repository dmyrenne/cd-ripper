# CD-Ripper Projekt - Copilot Instructions

## Projekt-Übersicht
Automatischer CD-Ripping-Service für Audio-CDs mit intelligenter Kategorisierung und formatspezifischer Verarbeitung.

## Kern-Funktionalität

### Workflow
1. **CD-Identifikation**
   - CD automatisch beim Einlegen erkennen
   - Metadaten von MusicBrainz/CDDB abrufen
   - Künstler, Album, Track-Namen ermitteln

2. **Kategorisierung**
   - **Kategorie 1**: Hörspiel oder Musik für Kinder
   - **Kategorie 2**: Hörbücher für Erwachsene
   - **Kategorie 3**: Musik (Künstler, Album, Tracks)

3. **Format-Auswahl basierend auf Kategorie**
   - **Kategorie 1 + 2**: MP3 @ 320 kbit/s
   - **Kategorie 3**: FLAC (16-bit, 44.1 kHz)

4. **Konvertierung**
   - Audio in gewähltes Format konvertieren
   - Qualitätsparameter entsprechend Kategorie anwenden

5. **Metadaten & Cover**
   - ID3-Tags/FLAC-Tags einbetten
   - Cover-Art herunterladen und einbetten

6. **Synchronisation**
   - Automatischer Upload auf lokalen Server
   - Strukturierte Organisation nach Künstler/Album

## Technische Anforderungen

### System-Tools
- `cdparanoia` - CD-Ripping mit Fehlerkorrektur ✅
- `flac` - FLAC-Encoding ✅
- `lame` - MP3-Encoding ✅
- `ffmpeg` - Audio-Processing ✅
- `libdiscid` - CD-TOC Identifikation ✅
- `rsync` - Datei-Synchronisation ✅
- `sshpass` - SSH-Password-Authentication ✅
- `eject` - CD-Auswurf ✅

### Python-Stack
- Python 3.x
- `discid` - CD-Identifikation
- `musicbrainzngs` - Metadaten-Abfrage
- `mutagen` - Audio-Tagging
- `pyudev` - Hardware-Event-Erkennung
- `requests` - Cover-Art Download
- Flask/FastAPI - Web-Interface (geplant)

### Ziel-Umgebung
- **Server**: 10.10.1.3
- **User**: dietpi (passwortbasierte Auth via sshpass)
- **Remote-Pfade** (kategoriebasiert, via Web-Interface anpassbar):
  - **Kategorie 1** (Kinderinhalte): /mnt/SSD-1TB/dietpi_userdata/Music/Kids
  - **Kategorie 2** (Hörbücher): /mnt/SSD-1TB/dietpi_userdata/Audiobooks
  - **Kategorie 3** (Musik): /mnt/SSD-1TB/dietpi_userdata/Music
- **Lokaler Output**: /mnt/dietpi_userdata/rips
- **Auto-Cleanup**: Lokale Dateien werden nach erfolgreichem Sync gelöscht

## Architektur-Prinzipien

1. **Modularität**: Jede Komponente als eigenständiges Modul
2. **Fehlertoleranz**: Retry-Logik und robustes Error-Handling
3. **Automatisierung**: Kein manueller Eingriff erforderlich
4. **Logging**: Vollständiges Audit-Trail aller Operationen
5. **Konfigurierbarkeit**: YAML-basierte Konfiguration
6. **Service-Betrieb**: 
   - Systemd-Service für automatischen Start
   - Auto-Start nach Boot/Stromausfall
   - Restart bei Crashes
   - Persistenz über Neustarts hinweg

## Geplante Module

```
src/
├── main.py              # Orchestrierung & Service-Loop
├── cd_detector.py       # Hardware-Erkennung (udev/polling)
├── cd_identifier.py     # MusicBrainz/CDDB Integration
├── cd_categorizer.py    # Kategorisierungs-Logik
├── ripper.py            # cdparanoia Wrapper
├── encoder.py           # Format-Konvertierung
├── tagger.py            # Metadaten-Handling
├── syncer.py            # Server-Sync
├── web_interface.py     # Status-Weboberfläche
└── utils.py             # Helper-Funktionen
```

## Entwicklungs-Richtlinien

### Code-Style
- PEP 8 konform
- Type Hints verwenden
- Docstrings für alle öffentlichen Funktionen
- Aussagekräftige Variablennamen

### Error-Handling
- Try-except Blöcke für I/O-Operationen
- Logging statt print()
- Graceful degradation bei Fehlern
- Retry-Mechanismen für Netzwerk-Operationen

### Testing
- Unit-Tests für kritische Funktionen
- Mock-Objekte für Hardware-Zugriffe
- Integration-Tests für End-to-End Workflow

## Web-Interface Anforderungen
- Anzeige der aktuell eingelegten CD (Cover + Name)
- Status des Ripping-Prozesses (Progress Bar)
- Status des Sync-Prozesses zum Zielserver (Progress Bar)
- Log-Anzeige der letzten Operationen
- **Konfiguration (editierbar)**:
  - Ripping-Profile pro Kategorie (Format, Bitrate, Compression)
  - Zielpfade pro Kategorie (lokal & remote)
  - Sync-Einstellungen (Server, User, Methode)
- Einfaches, responsives Design
- Keine Authentifizierung erforderlich (lokales Netzwerk)

## Wichtige Konfigurationsparameter

### Ripping-Profile (Default, via Web-Interface anpassbar)
- **Kategorie 1+2**: MP3, CBR 320 kbit/s, Stereo
- **Kategorie 3**: FLAC Lossless, Compression Level 8
  - Originale Sample-Rate und Bit-Tiefe erhalten
  - Typisch: 16-bit/44.1kHz (CD-Standard), aber nicht erzwungen

### Dateiorganisation
- Pattern: `{Künstler}/{Album}/{Track:02d} - {Titel}.{ext}`
- Sonderzeichen bereinigen
- Kollisions-Handling bei Duplikaten

### Sync-Verhalten
- rsync mit Kompression
- Delta-Transfer
- **Kategoriebasiertes Routing**:
  - Kategorie 1 → Kids-Ordner
  - Kategorie 2 → Audiobooks-Ordner
  - Kategorie 3 → Music-Ordner
- Auto-Eject nach erfolgreichem Sync
- Temp-Cleanup nach Übertragung

## Kontext für AI-Assistenz

Wenn der User Änderungen oder Erweiterungen wünscht:
1. Beachte die Kategorisierungs-Logik (3 Kategorien, 2 Format-Profile)
2. Halte die Modularität bei
3. Verwende bestehende Python-Bibliotheken
4. Priorisiere Robustheit über Features
5. Dokumentiere neue Konfigurationsoptionen
6. Aktualisiere Logging entsprechend
7. **Service muss als systemd-Service laufen** (Auto-Start, Restart on Failure)

## Systemd-Service Anforderungen

- **Service-Datei**: `/etc/systemd/system/cd-ripper.service`
- **Auto-Start**: `enabled` für automatischen Start nach Boot
- **Restart-Policy**: `on-failure` mit Delay
- **User**: Als Root oder dedizierter User mit CD-Zugriff
- **Dependencies**: Nach network.target starten
- **Logging**: Journal-Integration für systemd logs
- **Graceful Shutdown**: SIGTERM handling für sauberes Beenden

## Status-Tracking
Siehe `README.md` für aktuelle Entwicklungs-Checkliste.

---

## 📝 ToDo-Liste

### Phase 1: Setup & Grundstruktur ✅
- [x] 1.1 System-Dependencies installieren (cdparanoia, flac, lame, ffmpeg, libdiscid, rsync)
- [x] 1.2 Python-Dependencies installieren (requirements.txt erstellen & installieren)
- [x] 1.3 Projekt-Verzeichnisstruktur erstellen (src/, config/, logs/, output/)
- [x] 1.4 Basis-Konfigurationsdatei erstellen (config/config.yaml)

### Phase 2: Core-Module ✅
- [x] 2.1 utils.py: Helper-Funktionen (Logging-Setup, Dateinamen-Bereinigung)
- [x] 2.2 cd_detector.py: CD-Erkennung implementieren (Polling von /dev/sr0)
- [x] 2.3 cd_identifier.py: MusicBrainz Integration (Disc-ID, Metadaten-Abfrage)
- [x] 2.4 cd_categorizer.py: Kategorisierungs-Logik (Regeln für 3 Kategorien)
- [x] 2.5 ripper.py: cdparanoia Wrapper (Track-Extraktion zu WAV)
- [x] 2.6 encoder.py: Format-Konvertierung (WAV → FLAC/MP3 mit Profilen)
- [x] 2.7 tagger.py: Metadaten-Tagging (ID3/FLAC-Tags + Cover-Art)
- [x] 2.8 syncer.py: Server-Sync (rsync mit kategoriebasierten Pfaden + lokales Cleanup)

### Phase 3: Integration & Orchestrierung ✅
- [x] 3.1 main.py: Service-Loop implementieren (CD-Detection → Workflow)
- [x] 3.2 End-to-End Test: Kompletter Workflow mit echter CD ("Das kleine Gespenst, Teil 1")
- [x] 3.3 Error-Handling & Retry-Logik testen (funktioniert bei Fehlern & Abbruch)
- [x] 3.4 Logging & Monitoring verifizieren (vollständiges Audit-Trail)

### Phase 4: Web-Interface
- [ ] 4.1 Flask/FastAPI Setup
- [ ] 4.2 Status-Anzeige (Cover, CD-Info, Progress Bar)
- [ ] 4.3 Log-Viewer implementieren
- [ ] 4.4 Konfigurations-Editor (Ripping-Profile, Pfade)
- [ ] 4.5 Responsive Design & Testing

### Phase 5: Service-Installation
- [ ] 5.1 systemd Service-Datei erstellen
- [ ] 5.2 Installation-Script (install.sh) erstellen
- [ ] 5.3 Service installieren & aktivieren
- [ ] 5.4 Auto-Start nach Boot testen
- [ ] 5.5 Restart-on-Failure testen

### Phase 6: Finalisierung
- [ ] 6.1 Dokumentation vervollständigen (README.md)
- [ ] 6.2 Production-Tests mit verschiedenen CDs
- [ ] 6.3 Performance-Optimierung
- [ ] 6.4 SSH-Key-basierte Authentifizierung implementieren (statt Passwort in Config)
- [ ] 6.5 Projekt abgeschlossen ✅

---

### 📌 Hinweise zur ToDo-Verwaltung
- **Aktualisierung**: Liste wird nach erfolgreichem Test einer Aufgabe aktualisiert
- **Reihenfolge**: Phasen sequentiell abarbeiten, innerhalb einer Phase flexibel
- **Testing**: Jedes Modul einzeln testen bevor zur nächsten Phase übergegangen wird
- **Blocking Issues**: Bei Problemen dokumentieren und User informieren
