# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-03

### Added
- ✅ Automatic CD detection via `/dev/sr0` polling
- ✅ MusicBrainz integration for CD identification
- ✅ CoverArtArchive integration for album covers
- ✅ Intelligent 3-category recognition (Kids/Audiobooks/Music)
- ✅ Format-based encoding (MP3 320kbps / FLAC Lossless)
- ✅ cdparanoia ripping with error correction
- ✅ Automatic audio tagging (ID3/FLAC Vorbis)
- ✅ Server synchronization via rsync
- ✅ Category-based remote paths
- ✅ Auto-cleanup after successful upload
- ✅ Automatic CD ejection
- ✅ Web interface with real-time status
- ✅ Cover display in web interface
- ✅ Progress tracking per track
- ✅ Live log display in browser
- ✅ Settings editor in web interface
- ✅ Mobile-responsive design
- ✅ Multilingual interface (English & German)
- ✅ Language selection in settings
- ✅ Internationalization (i18n) framework
- ✅ Systemd service with auto-start
- ✅ SharedStatus IPC via JSON file
- ✅ Complete logging
- ✅ YAML-based configuration
- ✅ Install/Uninstall scripts

### Technical Details
- Flask web framework for REST API and UI
- fcntl-based file locking for thread safety
- Threading for parallel services
- Signal handlers for graceful shutdown
- Comprehensive error handling with retry logic
- JavaScript-based i18n system with localStorage persistence

## [Unreleased]

### Planned Features
- [ ] ST7789 display support
- [ ] SSH key authentication
- [ ] Multi-CD batch processing
- [ ] Manual metadata editing
- [ ] Cover upload for unknown CDs
- [ ] Statistics dashboard
- [ ] Email notifications
- [ ] Docker container

---

**Format**: [version] - YYYY-MM-DD

**Categories**: Added, Changed, Deprecated, Removed, Fixed, Security
