#!/usr/bin/env python3
"""
CD Identifier Module
Identifiziert CDs via MusicBrainz und lädt Metadaten/Cover
"""

import logging
import discid
import musicbrainzngs
import requests
from typing import Optional, Dict, List, Any
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class TrackInfo:
    """Informationen über einen einzelnen Track"""
    number: int
    title: str
    artist: str
    duration: int  # Sekunden
    

@dataclass
class AlbumInfo:
    """Informationen über ein Album/CD"""
    disc_id: str
    artist: str
    album: str
    year: Optional[int] = None
    genre: Optional[str] = None
    tracks: List[TrackInfo] = field(default_factory=list)
    cover_url: Optional[str] = None
    cover_data: Optional[bytes] = None
    musicbrainz_id: Optional[str] = None
    

class CDIdentifier:
    """
    Identifiziert Audio-CDs und lädt Metadaten
    """
    
    def __init__(self, device: str = "/dev/sr0", user_agent: str = "CD-Ripper/1.0"):
        """
        Initialisiert den CD-Identifier
        
        Args:
            device: CD-ROM Device-Pfad
            user_agent: User-Agent für MusicBrainz API
        """
        self.device = device
        self.logger = logging.getLogger('cd_ripper.identifier')
        
        # MusicBrainz konfigurieren
        musicbrainzngs.set_useragent(
            "CD-Ripper",
            "1.0",
            "https://github.com/user/cd-ripper"
        )
        musicbrainzngs.set_rate_limit(limit_or_interval=1.0)
        
    def read_disc_id(self) -> Optional[str]:
        """
        Liest die Disc-ID der eingelegten CD
        
        Returns:
            Disc-ID String oder None bei Fehler
        """
        try:
            disc = discid.read(self.device)
            self.logger.info(f"Disc-ID gelesen: {disc.id}")
            return disc.id
        except discid.DiscError as e:
            self.logger.error(f"Fehler beim Lesen der Disc-ID: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Unerwarteter Fehler bei Disc-ID: {e}")
            return None
    
    def get_disc_info(self) -> Optional[discid.Disc]:
        """
        Liest vollständige Disc-Informationen
        
        Returns:
            Disc-Objekt mit TOC-Daten
        """
        try:
            disc = discid.read(self.device)
            self.logger.debug(f"Disc: {disc.id}, {disc.sectors} Sektoren, {len(disc.tracks)} Tracks")
            return disc
        except discid.DiscError as e:
            self.logger.error(f"Fehler beim Lesen der Disc: {e}")
            return None
    
    def query_musicbrainz(self, disc_id: str) -> Optional[Dict[str, Any]]:
        """
        Fragt MusicBrainz nach Metadaten ab
        
        Args:
            disc_id: Disc-ID der CD
            
        Returns:
            Release-Dictionary von MusicBrainz
        """
        try:
            self.logger.info(f"Frage MusicBrainz ab für Disc-ID: {disc_id}")
            result = musicbrainzngs.get_releases_by_discid(
                disc_id,
                includes=["artists", "recordings", "release-groups"]
            )
            
            if "disc" in result and "release-list" in result["disc"]:
                releases = result["disc"]["release-list"]
                if releases:
                    self.logger.info(f"✅ {len(releases)} Release(s) gefunden")
                    return releases[0]  # Nimm erstes Match
                else:
                    self.logger.warning("Keine Releases für Disc-ID gefunden")
                    return None
            else:
                self.logger.warning("Ungültige MusicBrainz-Antwort")
                return None
                
        except musicbrainzngs.ResponseError as e:
            self.logger.error(f"MusicBrainz API-Fehler: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Fehler bei MusicBrainz-Abfrage: {e}")
            return None
    
    def get_cover_art(self, mb_release_id: str) -> Optional[bytes]:
        """
        Lädt Cover-Art von CoverArtArchive
        
        Args:
            mb_release_id: MusicBrainz Release-ID
            
        Returns:
            Bilddaten als Bytes oder None
        """
        try:
            url = f"https://coverartarchive.org/release/{mb_release_id}/front-500"
            self.logger.info(f"Lade Cover von: {url}")
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                self.logger.info(f"✅ Cover geladen ({len(response.content)} bytes)")
                return response.content
            else:
                self.logger.warning(f"Cover nicht verfügbar (HTTP {response.status_code})")
                return None
                
        except requests.RequestException as e:
            self.logger.error(f"Fehler beim Cover-Download: {e}")
            return None
    
    def identify_cd(self) -> Optional[AlbumInfo]:
        """
        Komplette CD-Identifikation mit allen Metadaten
        
        Returns:
            AlbumInfo-Objekt oder None bei Fehler
        """
        # 1. Disc-ID lesen
        disc = self.get_disc_info()
        if not disc:
            return None
        
        # 2. MusicBrainz abfragen
        release = self.query_musicbrainz(disc.id)
        if not release:
            self.logger.warning("CD konnte nicht identifiziert werden")
            return None
        
        # 3. Metadaten extrahieren
        album_info = AlbumInfo(
            disc_id=disc.id,
            artist="Unknown Artist",
            album="Unknown Album",
            musicbrainz_id=release.get("id")
        )
        
        # Artist
        if "artist-credit" in release and release["artist-credit"]:
            album_info.artist = release["artist-credit"][0]["artist"]["name"]
        
        # Album
        if "title" in release:
            album_info.album = release["title"]
        
        # Jahr
        if "date" in release:
            try:
                album_info.year = int(release["date"][:4])
            except:
                pass
        
        # Genre (aus Release-Group)
        if "release-group" in release:
            rg = release["release-group"]
            if "type" in rg:
                album_info.genre = rg["type"]
        
        # Tracks
        if "medium-list" in release:
            for medium in release["medium-list"]:
                if "disc-list" in medium:
                    # Prüfe ob Disc-ID übereinstimmt
                    for disc_entry in medium["disc-list"]:
                        if disc_entry.get("id") == disc.id:
                            # Track-Liste aus diesem Medium
                            if "track-list" in medium:
                                for track_data in medium["track-list"]:
                                    track_num = int(track_data.get("position", 0))
                                    recording = track_data.get("recording", {})
                                    
                                    track = TrackInfo(
                                        number=track_num,
                                        title=recording.get("title", f"Track {track_num}"),
                                        artist=album_info.artist,
                                        duration=int(recording.get("length", 0)) // 1000 if "length" in recording else 0
                                    )
                                    album_info.tracks.append(track)
                            break
        
        # Fallback: Tracks aus Disc-Objekt wenn MusicBrainz keine liefert
        if not album_info.tracks:
            self.logger.info("Erstelle Tracks aus Disc-TOC")
            for i, track in enumerate(disc.tracks, start=1):
                album_info.tracks.append(TrackInfo(
                    number=i,
                    title=f"Track {i:02d}",
                    artist=album_info.artist,
                    duration=track.sectors // 75  # 75 Sektoren = 1 Sekunde
                ))
        
        self.logger.info(f"✅ Album identifiziert: {album_info.artist} - {album_info.album}")
        self.logger.info(f"   {len(album_info.tracks)} Tracks")
        
        # 4. Cover laden
        if album_info.musicbrainz_id:
            cover_data = self.get_cover_art(album_info.musicbrainz_id)
            if cover_data:
                album_info.cover_data = cover_data
        
        return album_info
    
    def save_cover(self, album_info: AlbumInfo, output_path: str) -> bool:
        """
        Speichert Cover-Art in Datei
        
        Args:
            album_info: AlbumInfo mit cover_data
            output_path: Pfad für Cover-Datei
            
        Returns:
            True bei Erfolg
        """
        if not album_info.cover_data:
            self.logger.warning("Keine Cover-Daten vorhanden")
            return False
        
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'wb') as f:
                f.write(album_info.cover_data)
            
            self.logger.info(f"Cover gespeichert: {output_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Fehler beim Cover-Speichern: {e}")
            return False


if __name__ == "__main__":
    # Test des CD-Identifiers
    import sys
    sys.path.insert(0, '/root/projects/cd-ripper/src')
    from utils import load_config, setup_logging
    
    print("Testing CD Identifier...")
    
    # Setup
    config = load_config()
    logger = setup_logging(config)
    
    device = config.get('ripper', {}).get('device', '/dev/sr0')
    identifier = CDIdentifier(device=device)
    
    # Test Disc-ID
    disc_id = identifier.read_disc_id()
    if disc_id:
        print(f"✅ Disc-ID: {disc_id}")
    else:
        print("❌ Konnte Disc-ID nicht lesen (keine CD eingelegt?)")
        sys.exit(1)
    
    # Test vollständige Identifikation
    print("\n⏳ Identifiziere CD...")
    album_info = identifier.identify_cd()
    
    if album_info:
        print(f"\n✅ CD identifiziert!")
        print(f"   Künstler: {album_info.artist}")
        print(f"   Album: {album_info.album}")
        print(f"   Jahr: {album_info.year}")
        print(f"   Genre: {album_info.genre}")
        print(f"   Tracks: {len(album_info.tracks)}")
        
        if album_info.tracks:
            print(f"\n   Track-Liste:")
            for track in album_info.tracks[:5]:  # Erste 5 Tracks
                print(f"     {track.number:02d}. {track.title}")
            if len(album_info.tracks) > 5:
                print(f"     ... und {len(album_info.tracks) - 5} weitere")
        
        if album_info.cover_data:
            print(f"   Cover: ✅ ({len(album_info.cover_data)} bytes)")
            
            # Test Cover speichern
            test_cover_path = "/root/projects/cd-ripper/output/test_cover.jpg"
            if identifier.save_cover(album_info, test_cover_path):
                print(f"   Cover Test-Datei: {test_cover_path}")
        else:
            print(f"   Cover: ❌ nicht verfügbar")
    else:
        print("❌ CD konnte nicht identifiziert werden")
    
    print("\n🎉 CD-Identifier Tests abgeschlossen!")
