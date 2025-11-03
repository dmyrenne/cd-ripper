#!/usr/bin/env python3
"""
Audio Tagger Module
Schreibt Metadaten (ID3/FLAC) und Cover-Art in Audio-Dateien
"""

import logging
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, TIT2, TPE1, TALB, TDRC, TRCK, APIC
from mutagen.id3 import ID3NoHeaderError


class AudioTagger:
    """
    Schreibt Metadaten und Cover-Art in Audio-Dateien
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialisiert den Tagger
        
        Args:
            config: Konfigurations-Dictionary
        """
        self.config = config
        self.logger = logging.getLogger('cd_ripper.tagger')
        self.timeout = config.get('tagger', {}).get('timeout', 10)
        
    def tag_file(self, audio_file: str, metadata: Dict[str, Any], 
                 cover_url: Optional[str] = None) -> bool:
        """
        Schreibt Metadaten in Audio-Datei
        
        Args:
            audio_file: Pfad zur Audio-Datei
            metadata: Dictionary mit Metadaten
            cover_url: URL zum Cover-Bild (optional)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        file_path = Path(audio_file)
        
        if not file_path.exists():
            self.logger.error(f"Audio-Datei nicht gefunden: {audio_file}")
            return False
        
        # Format anhand Dateiendung erkennen
        ext = file_path.suffix.lower()
        
        try:
            if ext == '.flac':
                return self._tag_flac(str(file_path), metadata, cover_url)
            elif ext == '.mp3':
                return self._tag_mp3(str(file_path), metadata, cover_url)
            else:
                self.logger.error(f"Nicht unterstütztes Format: {ext}")
                return False
        except Exception as e:
            self.logger.error(f"Fehler beim Tagging von {audio_file}: {e}", exc_info=True)
            return False
    
    def _tag_flac(self, file_path: str, metadata: Dict[str, Any], 
                  cover_url: Optional[str] = None) -> bool:
        """
        Schreibt Metadaten in FLAC-Datei
        
        Args:
            file_path: Pfad zur FLAC-Datei
            metadata: Metadaten-Dictionary
            cover_url: URL zum Cover-Bild
            
        Returns:
            True bei Erfolg
        """
        self.logger.info(f"Tagging FLAC: {file_path}")
        
        audio = FLAC(file_path)
        
        # Vorbis Comments setzen
        if 'title' in metadata and metadata['title']:
            audio['TITLE'] = metadata['title']
        
        if 'artist' in metadata and metadata['artist']:
            audio['ARTIST'] = metadata['artist']
        
        if 'album' in metadata and metadata['album']:
            audio['ALBUM'] = metadata['album']
        
        if 'date' in metadata and metadata['date']:
            audio['DATE'] = str(metadata['date'])
        
        if 'track_number' in metadata and metadata['track_number']:
            audio['TRACKNUMBER'] = str(metadata['track_number'])
        
        if 'track_total' in metadata and metadata['track_total']:
            audio['TRACKTOTAL'] = str(metadata['track_total'])
        
        # Zusätzliche Felder
        if 'album_artist' in metadata and metadata['album_artist']:
            audio['ALBUMARTIST'] = metadata['album_artist']
        
        if 'genre' in metadata and metadata['genre']:
            audio['GENRE'] = metadata['genre']
        
        if 'disc_number' in metadata and metadata['disc_number']:
            audio['DISCNUMBER'] = str(metadata['disc_number'])
        
        # Cover-Art hinzufügen
        if cover_url:
            self._add_flac_cover(audio, cover_url)
        
        # Speichern
        audio.save()
        self.logger.info(f"FLAC erfolgreich getaggt: {file_path}")
        return True
    
    def _tag_mp3(self, file_path: str, metadata: Dict[str, Any], 
                 cover_url: Optional[str] = None) -> bool:
        """
        Schreibt Metadaten in MP3-Datei
        
        Args:
            file_path: Pfad zur MP3-Datei
            metadata: Metadaten-Dictionary
            cover_url: URL zum Cover-Bild
            
        Returns:
            True bei Erfolg
        """
        self.logger.info(f"Tagging MP3: {file_path}")
        
        audio = MP3(file_path)
        
        # ID3 Tags initialisieren falls nicht vorhanden
        if audio.tags is None:
            audio.add_tags()
            self.logger.debug("ID3 Tags initialisiert")
        
        # ID3v2.4 Tags setzen
        if 'title' in metadata and metadata['title']:
            audio.tags.add(TIT2(encoding=3, text=metadata['title']))
        
        if 'artist' in metadata and metadata['artist']:
            audio.tags.add(TPE1(encoding=3, text=metadata['artist']))
        
        if 'album' in metadata and metadata['album']:
            audio.tags.add(TALB(encoding=3, text=metadata['album']))
        
        if 'date' in metadata and metadata['date']:
            audio.tags.add(TDRC(encoding=3, text=str(metadata['date'])))
        
        if 'track_number' in metadata and metadata['track_number']:
            track_str = str(metadata['track_number'])
            if 'track_total' in metadata and metadata['track_total']:
                track_str += f"/{metadata['track_total']}"
            audio.tags.add(TRCK(encoding=3, text=track_str))
        
        # Cover-Art hinzufügen
        if cover_url:
            self._add_mp3_cover(audio, cover_url)
        
        # Speichern
        audio.save()
        self.logger.info(f"MP3 erfolgreich getaggt: {file_path}")
        return True
    
    def _add_flac_cover(self, audio: FLAC, cover_url: str) -> bool:
        """
        Fügt Cover-Art zu FLAC-Datei hinzu
        
        Args:
            audio: FLAC-Objekt
            cover_url: URL zum Cover-Bild
            
        Returns:
            True bei Erfolg
        """
        try:
            self.logger.debug(f"Lade Cover von: {cover_url}")
            response = requests.get(cover_url, timeout=self.timeout)
            response.raise_for_status()
            
            # Picture erstellen
            picture = Picture()
            picture.type = 3  # Cover (front)
            picture.mime = response.headers.get('Content-Type', 'image/jpeg')
            picture.desc = 'Cover'
            picture.data = response.content
            
            # Cover hinzufügen
            audio.clear_pictures()
            audio.add_picture(picture)
            
            self.logger.info(f"Cover erfolgreich hinzugefügt ({len(picture.data)} bytes)")
            return True
            
        except Exception as e:
            self.logger.warning(f"Fehler beim Cover-Download: {e}")
            return False
    
    def _add_mp3_cover(self, audio: MP3, cover_url: str) -> bool:
        """
        Fügt Cover-Art zu MP3-Datei hinzu
        
        Args:
            audio: MP3-Objekt
            cover_url: URL zum Cover-Bild
            
        Returns:
            True bei Erfolg
        """
        try:
            self.logger.debug(f"Lade Cover von: {cover_url}")
            response = requests.get(cover_url, timeout=self.timeout)
            response.raise_for_status()
            
            # APIC Frame erstellen
            audio.tags.add(
                APIC(
                    encoding=3,  # UTF-8
                    mime=response.headers.get('Content-Type', 'image/jpeg'),
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=response.content
                )
            )
            
            self.logger.info(f"Cover erfolgreich hinzugefügt ({len(response.content)} bytes)")
            return True
            
        except Exception as e:
            self.logger.warning(f"Fehler beim Cover-Download: {e}")
            return False
    
    def tag_album(self, audio_files: list[str], album_metadata: Dict[str, Any],
                  cover_url: Optional[str] = None) -> Dict[str, bool]:
        """
        Tagged mehrere Dateien mit Album-Metadaten
        
        Args:
            audio_files: Liste von Audio-Dateien
            album_metadata: Basis-Metadaten (Artist, Album, Date, etc.)
            cover_url: URL zum Cover-Bild
            
        Returns:
            Dictionary mit Dateinamen und Erfolgs-Status
        """
        results = {}
        
        for audio_file in audio_files:
            # Track-spezifische Metadaten extrahieren
            # Annahme: Dateiname Format "01 - Title.ext"
            file_path = Path(audio_file)
            filename = file_path.stem
            
            # Track-Metadaten aus Dateinamen parsen
            track_metadata = album_metadata.copy()
            
            # Versuche Track-Nummer zu extrahieren
            import re
            match = re.match(r'^(\d+)\s*[-_]?\s*(.+)$', filename)
            if match:
                track_metadata['track_number'] = int(match.group(1))
                track_metadata['title'] = match.group(2).strip()
            else:
                track_metadata['title'] = filename
            
            # Taggen
            success = self.tag_file(audio_file, track_metadata, cover_url)
            results[audio_file] = success
            
            if not success:
                self.logger.warning(f"Tagging fehlgeschlagen: {audio_file}")
        
        # Zusammenfassung
        success_count = sum(1 for v in results.values() if v)
        total_count = len(results)
        self.logger.info(f"Album-Tagging abgeschlossen: {success_count}/{total_count} erfolgreich")
        
        return results


def main():
    """Test-Funktion"""
    import yaml
    
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Config laden
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Tagger testen
    tagger = AudioTagger(config)
    
    # Test-Metadaten
    metadata = {
        'title': 'Test Track',
        'artist': 'Test Artist',
        'album': 'Test Album',
        'date': '2025',
        'track_number': 1,
        'track_total': 10,
        'genre': 'Test'
    }
    
    # Test-Datei (muss existieren)
    test_file_mp3 = "/root/projects/cd-ripper/output/test_encode_track01.mp3"
    test_file_flac = "/root/projects/cd-ripper/output/test_encode_track01.flac"
    
    # Test-Cover-URL (MusicBrainz Beispiel)
    cover_url = "https://coverartarchive.org/release/76df3287-6cda-33eb-8e9a-044b5e15ffdd/829521842.jpg"
    
    # Test MP3
    if Path(test_file_mp3).exists():
        print("=== Testing MP3 Tagging ===")
        success = tagger.tag_file(test_file_mp3, metadata, cover_url)
        print(f"Tagging {'erfolgreich' if success else 'fehlgeschlagen'}")
        
        # Metadaten auslesen zur Verifikation
        if success:
            audio = MP3(test_file_mp3)
            print("\n=== Verifikation der geschriebenen MP3 Tags ===")
            print(f"Title: {audio.tags.get('TIT2', 'N/A')}")
            print(f"Artist: {audio.tags.get('TPE1', 'N/A')}")
            print(f"Album: {audio.tags.get('TALB', 'N/A')}")
            print(f"Date: {audio.tags.get('TDRC', 'N/A')}")
            print(f"Track: {audio.tags.get('TRCK', 'N/A')}")
            print(f"Cover: {'Ja' if audio.tags.get('APIC:Cover') else 'Nein'}")
    else:
        print(f"MP3 Test-Datei nicht gefunden: {test_file_mp3}")
    
    # Test FLAC
    if Path(test_file_flac).exists():
        print("\n\n=== Testing FLAC Tagging ===")
        success = tagger.tag_file(test_file_flac, metadata, cover_url)
        print(f"Tagging {'erfolgreich' if success else 'fehlgeschlagen'}")
        
        # Metadaten auslesen zur Verifikation
        if success:
            audio = FLAC(test_file_flac)
            print("\n=== Verifikation der geschriebenen FLAC Tags ===")
            print(f"Title: {audio.get('TITLE', ['N/A'])[0]}")
            print(f"Artist: {audio.get('ARTIST', ['N/A'])[0]}")
            print(f"Album: {audio.get('ALBUM', ['N/A'])[0]}")
            print(f"Date: {audio.get('DATE', ['N/A'])[0]}")
            print(f"Track: {audio.get('TRACKNUMBER', ['N/A'])[0]}/{audio.get('TRACKTOTAL', ['N/A'])[0]}")
            print(f"Cover: {'Ja' if audio.pictures else 'Nein'}")
            if audio.pictures:
                print(f"Cover Size: {len(audio.pictures[0].data)} bytes")
    else:
        print(f"FLAC Test-Datei nicht gefunden: {test_file_flac}")


if __name__ == "__main__":
    main()
