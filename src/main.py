#!/usr/bin/env python3
"""
CD-Ripper Main Service
Orchestriert den kompletten CD-Ripping-Workflow
"""

import logging
import time
import signal
import sys
from pathlib import Path
from typing import Optional
import yaml

from cd_detector import CDDetector
from cd_identifier import CDIdentifier
from cd_categorizer import CDCategorizer
from ripper import CDRipper
from encoder import AudioEncoder
from tagger import AudioTagger
from syncer import ServerSyncer
from utils import setup_logging, sanitize_filename


class CDRipperService:
    """
    Hauptservice für automatisches CD-Ripping
    """
    
    def __init__(self, config_path: str):
        """
        Initialisiert den Service
        
        Args:
            config_path: Pfad zur Konfigurationsdatei
        """
        # Konfiguration laden
        with open(config_path) as f:
            self.config = yaml.safe_load(f)
        
        # Logging einrichten
        self.logger = setup_logging(self.config)
        
        self.logger.info("=" * 60)
        self.logger.info("CD-Ripper Service wird gestartet...")
        self.logger.info("=" * 60)
        
        # Module initialisieren
        device = self.config.get('ripper', {}).get('device', '/dev/sr0')
        self.detector = CDDetector(device=device, poll_interval=2)
        self.identifier = CDIdentifier(device=device)
        self.categorizer = CDCategorizer()
        self.ripper = CDRipper(
            device=self.config.get('ripper', {}).get('device', '/dev/sr0'),
            quality=self.config.get('ripper', {}).get('quality', 'paranoia')
        )
        self.encoder = AudioEncoder(self.config)
        self.tagger = AudioTagger(self.config)
        self.syncer = ServerSyncer(self.config)
        
        # Output-Verzeichnis
        self.output_dir = Path(self.config.get('output', {}).get('local_path', '/mnt/dietpi_userdata/rips'))
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Service-Status
        self.running = True
        self.processing = False
        
        # Signal-Handler für graceful shutdown
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
        self.logger.info("Service erfolgreich initialisiert")
    
    def _signal_handler(self, signum, frame):
        """
        Handler für Shutdown-Signale
        """
        self.logger.info(f"Signal {signum} empfangen, beende Service...")
        self.running = False
        
        if self.processing:
            self.logger.info("Warte auf Abschluss der aktuellen Verarbeitung...")
    
    def process_cd(self) -> bool:
        """
        Verarbeitet eine eingelegte CD komplett
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        self.processing = True
        
        try:
            self.logger.info("=" * 60)
            self.logger.info("Starte CD-Verarbeitung")
            self.logger.info("=" * 60)
            
            # 1. CD identifizieren
            self.logger.info("Schritt 1/6: CD-Identifikation")
            cd_info = self.identifier.identify_cd()
            
            if not cd_info:
                self.logger.error("CD konnte nicht identifiziert werden")
                return False
            
            self.logger.info(f"CD identifiziert: {cd_info.artist} - {cd_info.album}")
            
            # 2. Kategorisieren
            self.logger.info("Schritt 2/6: Kategorisierung")
            category_result = self.categorizer.categorize(
                artist=cd_info.artist,
                album=cd_info.album,
                genre=cd_info.genre,
                tracks=cd_info.tracks,
                year=cd_info.year
            )
            self.logger.info(f"Kategorie: {category_result.category_name} (Confidence: {category_result.confidence:.2f})")
            self.logger.info(f"Grund: {category_result.reason}")
            
            # 3. Format-Profil ermitteln
            profile = self.encoder.get_profile(category_result.category)
            self.logger.info(f"Encoding-Format: {profile['format'].upper()}")
            
            # 4. Arbeitsverzeichnis erstellen
            album_dir = self._create_album_directory(cd_info)
            self.logger.info(f"Arbeitsverzeichnis: {album_dir}")
            
            # 5. Tracks rippen
            self.logger.info("Schritt 3/6: CD-Ripping")
            ripped_files = []
            
            for track_info in cd_info.tracks:
                if not self.running:
                    self.logger.warning("Service wird beendet, breche Ripping ab")
                    return False
                
                track_num = track_info.number
                
                # Dateinamen erstellen
                track_name = sanitize_filename(track_info.title)
                wav_file = album_dir / f"track{track_num:02d}.wav"
                
                self.logger.info(f"Rippe Track {track_num}/{len(cd_info.tracks)}: {track_name}")
                
                success = self.ripper.rip_track(
                    track_num,
                    str(wav_file),
                    progress_callback=lambda p: self.logger.debug(f"Track {track_num} Progress: {p}%")
                )
                
                if success:
                    ripped_files.append((track_num, str(wav_file), track_info))
                    self.logger.info(f"✓ Track {track_num} erfolgreich gerippt")
                else:
                    self.logger.error(f"✗ Track {track_num} fehlgeschlagen")
            
            if not ripped_files:
                self.logger.error("Keine Tracks erfolgreich gerippt")
                return False
            
            # 6. Encoding
            self.logger.info("Schritt 4/6: Audio-Encoding")
            encoded_files = []
            
            for track_num, wav_file, track_info in ripped_files:
                if not self.running:
                    self.logger.warning("Service wird beendet, breche Encoding ab")
                    return False
                
                track_name = sanitize_filename(track_info.title)
                output_file = album_dir / f"{track_num:02d} - {track_name}.{profile['format']}"
                
                self.logger.info(f"Encodiere Track {track_num}: {track_name}")
                
                if profile['format'] == 'mp3':
                    success = self.encoder.encode_to_mp3(
                        wav_file,
                        str(output_file),
                        bitrate=profile.get('bitrate', 320)
                    )
                else:  # FLAC
                    success = self.encoder.encode_to_flac(
                        wav_file,
                        str(output_file),
                        compression=profile.get('compression', 8)
                    )
                
                if success:
                    encoded_files.append((track_num, str(output_file), track_info))
                    self.logger.info(f"✓ Track {track_num} erfolgreich encodiert")
                    # WAV-Datei löschen nach Encoding
                    Path(wav_file).unlink()
                else:
                    self.logger.error(f"✗ Track {track_num} Encoding fehlgeschlagen")
            
            if not encoded_files:
                self.logger.error("Keine Tracks erfolgreich encodiert")
                return False
            
            # 7. Tagging
            self.logger.info("Schritt 5/6: Metadaten-Tagging")
            
            # Album-Metadaten vorbereiten
            album_metadata = {
                'artist': cd_info.artist,
                'album': cd_info.album,
                'date': str(cd_info.year) if cd_info.year else None,
                'track_total': len(cd_info.tracks),
                'genre': cd_info.genre
            }
            
            for track_num, audio_file, track_info in encoded_files:
                if not self.running:
                    self.logger.warning("Service wird beendet, breche Tagging ab")
                    return False
                
                track_metadata = album_metadata.copy()
                track_metadata.update({
                    'title': track_info.title,
                    'track_number': track_num
                })
                
                self.logger.info(f"Tagge Track {track_num}: {track_info.title}")
                
                success = self.tagger.tag_file(
                    audio_file,
                    track_metadata,
                    cover_url=cd_info.cover_url
                )
                
                if success:
                    self.logger.info(f"✓ Track {track_num} erfolgreich getaggt")
                else:
                    self.logger.warning(f"⚠ Track {track_num} Tagging fehlgeschlagen")
            
            # 8. Sync zum Server
            if self.config.get('sync', {}).get('enabled', True):
                self.logger.info("Schritt 6/6: Server-Synchronisation")
                
                success = self.syncer.sync_directory(
                    str(album_dir.parent),
                    category_result.category,
                    progress_callback=lambda p: self.logger.info(f"Sync Progress: {p}%")
                )
                
                if success:
                    self.logger.info("✓ Server-Sync erfolgreich")
                else:
                    self.logger.error("✗ Server-Sync fehlgeschlagen")
                    return False
            else:
                self.logger.info("Server-Sync deaktiviert")
            
            # 9. CD auswerfen
            if self.config.get('sync', {}).get('auto_eject', True):
                self.logger.info("Werfe CD aus...")
                self.detector.eject_cd()
            
            self.logger.info("=" * 60)
            self.logger.info("✅ CD-Verarbeitung erfolgreich abgeschlossen!")
            self.logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler bei CD-Verarbeitung: {e}", exc_info=True)
            return False
        finally:
            self.processing = False
    
    def _create_album_directory(self, cd_info) -> Path:
        """
        Erstellt Verzeichnisstruktur für Album
        
        Args:
            cd_info: CD-Informationen
            
        Returns:
            Pfad zum Album-Verzeichnis
        """
        # Dateinamen bereinigen
        artist = sanitize_filename(cd_info.artist)
        album = sanitize_filename(cd_info.album)
        
        # Organisationsstruktur aus Config
        organize_by = self.config.get('output', {}).get('organize_by', 'artist/album')
        
        if organize_by == 'artist/album':
            album_dir = self.output_dir / artist / album
        elif organize_by == 'album':
            album_dir = self.output_dir / album
        else:  # flat
            album_dir = self.output_dir / f"{artist} - {album}"
        
        album_dir.mkdir(parents=True, exist_ok=True)
        return album_dir
    
    def run(self):
        """
        Hauptschleife des Services
        """
        self.logger.info("Service-Loop gestartet")
        last_cd_present = False
        
        while self.running:
            try:
                # CD erkennen
                cd_info = self.detector.get_cd_info()
                
                if cd_info.present and cd_info.is_audio and not last_cd_present:
                    # Neue Audio-CD erkannt
                    self.logger.info("Neue Audio-CD erkannt")
                    last_cd_present = True
                    
                    # CD verarbeiten
                    success = self.process_cd()
                    
                    if not success:
                        self.logger.error("CD-Verarbeitung fehlgeschlagen")
                        # Warte vor erneutem Versuch
                        time.sleep(30)
                elif not cd_info.present and last_cd_present:
                    # CD wurde entfernt
                    self.logger.info("CD wurde entfernt")
                    last_cd_present = False
                
                # Polling-Intervall
                time.sleep(2)
                
            except KeyboardInterrupt:
                self.logger.info("Keyboard Interrupt empfangen")
                break
            except Exception as e:
                self.logger.error(f"Fehler in Service-Loop: {e}", exc_info=True)
                time.sleep(10)
        
        self.logger.info("Service-Loop beendet")
    
    def shutdown(self):
        """
        Sauberes Herunterfahren des Services
        """
        self.logger.info("Service wird heruntergefahren...")
        self.running = False


def main():
    """
    Haupteinstiegspunkt
    """
    # Konfigurationsdatei
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    if not config_path.exists():
        print(f"Fehler: Konfigurationsdatei nicht gefunden: {config_path}")
        sys.exit(1)
    
    # Service starten
    service = CDRipperService(str(config_path))
    
    try:
        service.run()
    except Exception as e:
        service.logger.error(f"Fataler Fehler: {e}", exc_info=True)
        sys.exit(1)
    finally:
        service.shutdown()


if __name__ == "__main__":
    main()
