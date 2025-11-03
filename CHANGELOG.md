# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added
- ✅ Automatische CD-Erkennung via `/dev/sr0` polling
- ✅ MusicBrainz Integration für CD-Identifikation
- ✅ CoverArtArchive Integration für Album-Cover
- ✅ Intelligente 3-Kategorien-Erkennung (Kinder/Hörbücher/Musik)
- ✅ Format-basiertes Encoding (MP3 320kbps / FLAC Lossless)
- ✅ cdparanoia Ripping mit Fehlerkorrektur
- ✅ Automatisches Audio-Tagging (ID3/FLAC Vorbis)
- ✅ Server-Synchronisation via rsync
- ✅ Kategoriebasierte Remote-Pfade
- ✅ Auto-Cleanup nach erfolgreichem Upload
- ✅ Automatischer CD-Auswurf
- ✅ Web-Interface mit Echtzeit-Status
- ✅ Cover-Anzeige im Web-Interface
- ✅ Progress-Tracking pro Track
- ✅ Live-Log-Anzeige im Browser
- ✅ Einstellungs-Editor im Web-Interface
- ✅ Mobile-responsive Design
- ✅ Systemd-Service mit Auto-Start
- ✅ SharedStatus IPC via JSON-File
- ✅ Vollständiges Logging
- ✅ YAML-basierte Konfiguration
- ✅ Install/Uninstall Scripts

### Technical Details
- Flask Web-Framework für REST-API und UI
- fcntl-basiertes File-Locking für Thread-Safety
- Threading für parallel laufende Services
- Signal-Handler für graceful shutdown
- Comprehensive error handling mit Retry-Logik

## [Unreleased]

### Planned Features
- [ ] ST7789 Display-Unterstützung
- [ ] SSH-Key Authentication
- [ ] Multi-CD Batch-Processing
- [ ] Manuelle Metadaten-Bearbeitung
- [ ] Cover-Upload für unbekannte CDs
- [ ] Statistiken-Dashboard
- [ ] Email-Benachrichtigungen
- [ ] Docker-Container

---

**Format**: [version] - YYYY-MM-DD

**Categories**: Added, Changed, Deprecated, Removed, Fixed, Security
