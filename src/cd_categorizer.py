#!/usr/bin/env python3
"""
CD Categorizer Module
Kategorisiert CDs in: Kinderinhalte, Hörbücher, Musik
"""

import logging
import re
from typing import Optional
from dataclasses import dataclass


@dataclass
class CategoryResult:
    """Ergebnis der Kategorisierung"""
    category: int  # 1, 2, oder 3
    category_name: str
    confidence: float  # 0.0 - 1.0
    reason: str


class CDCategorizer:
    """
    Kategorisiert CDs basierend auf Metadaten
    """
    
    # Keywords für Kategorien
    KIDS_KEYWORDS = [
        # Deutsche Keywords
        'kinder', 'kinderlied', 'kindergarten', 'kind', 'kids',
        'hörspiel', 'märchen', 'geschichten für', 'disney',
        'für kinder', 'ab 3', 'ab 4', 'ab 5', 'ab 6',
        'bibi', 'benjamin', 'conni', 'tkkg', 'drei fragezeichen',
        'die drei ???', 'europa', 'karussell',
        # Namen bekannter Kinderautoren/Erzähler
        'janosch', 'otfried preußler', 'astrid lindgren',
        'paul maar', 'erich kästner', 'michael ende',
        # Englische Keywords
        'children', 'kid', 'baby', 'toddler', 'nursery'
    ]
    
    AUDIOBOOK_KEYWORDS = [
        # Deutsche Keywords
        'hörbuch', 'hörspiel', 'gelesen von', 'ungekürzt', 'gekürzt',
        'roman', 'erzählung', 'lesung', 'sprecher', 'vorgelesen',
        'audible', 'hörbuchverlag', 'argon', 'lübbe audio',
        # Englische Keywords
        'audiobook', 'unabridged', 'narrated', 'narration',
        'read by', 'performed by'
    ]
    
    # Genre-Mappings
    MUSIC_GENRES = [
        'album', 'ep', 'single', 'compilation', 'soundtrack',
        'live', 'remix'
    ]
    
    def __init__(self):
        """Initialisiert den Categorizer"""
        self.logger = logging.getLogger('cd_ripper.categorizer')
        
    def _check_keywords(self, text: str, keywords: list) -> float:
        """
        Prüft Text auf Keywords
        
        Args:
            text: Zu prüfender Text
            keywords: Liste von Keywords
            
        Returns:
            Score 0.0 - 1.0 basierend auf Treffern
        """
        if not text:
            return 0.0
        
        text_lower = text.lower()
        matches = 0
        
        for keyword in keywords:
            if keyword.lower() in text_lower:
                matches += 1
        
        # Score basierend auf Anzahl Treffer
        if matches == 0:
            return 0.0
        elif matches == 1:
            return 0.6
        elif matches == 2:
            return 0.8
        else:
            return 1.0
    
    def _analyze_artist(self, artist: str) -> tuple[Optional[int], float]:
        """
        Analysiert Künstler-Namen
        
        Returns:
            (Kategorie, Confidence) oder (None, 0.0)
        """
        # Kinder-Content Check
        kids_score = self._check_keywords(artist, self.KIDS_KEYWORDS)
        if kids_score > 0.5:
            return (1, kids_score)
        
        # Hörbuch-Autoren/Sprecher Check
        audiobook_score = self._check_keywords(artist, self.AUDIOBOOK_KEYWORDS)
        if audiobook_score > 0.5:
            return (2, audiobook_score)
        
        return (None, 0.0)
    
    def _analyze_album(self, album: str) -> tuple[Optional[int], float]:
        """
        Analysiert Album-Titel
        
        Returns:
            (Kategorie, Confidence) oder (None, 0.0)
        """
        # Kinder-Content Check
        kids_score = self._check_keywords(album, self.KIDS_KEYWORDS)
        if kids_score > 0.5:
            return (1, kids_score)
        
        # Hörbuch Check
        audiobook_score = self._check_keywords(album, self.AUDIOBOOK_KEYWORDS)
        if audiobook_score > 0.5:
            return (2, audiobook_score)
        
        return (None, 0.0)
    
    def _analyze_genre(self, genre: Optional[str]) -> tuple[Optional[int], float]:
        """
        Analysiert Genre
        
        Returns:
            (Kategorie, Confidence) oder (None, 0.0)
        """
        if not genre:
            return (None, 0.0)
        
        genre_lower = genre.lower()
        
        # Explizite Audiobook-Genres
        if 'audiobook' in genre_lower or 'spoken' in genre_lower:
            return (2, 0.9)
        
        # Musik-Genres
        if any(mg in genre_lower for mg in self.MUSIC_GENRES):
            return (3, 0.7)
        
        return (None, 0.0)
    
    def _analyze_tracks(self, tracks: list) -> tuple[Optional[int], float]:
        """
        Analysiert Track-Namen
        
        Returns:
            (Kategorie, Confidence) oder (None, 0.0)
        """
        if not tracks:
            return (None, 0.0)
        
        # Prüfe ersten Track-Titel
        first_track = tracks[0].title if hasattr(tracks[0], 'title') else str(tracks[0])
        
        kids_score = self._check_keywords(first_track, self.KIDS_KEYWORDS)
        if kids_score > 0.5:
            return (1, kids_score * 0.8)  # Etwas niedrigere Confidence
        
        audiobook_score = self._check_keywords(first_track, self.AUDIOBOOK_KEYWORDS)
        if audiobook_score > 0.5:
            return (2, audiobook_score * 0.8)
        
        # Hörbücher haben oft Kapitel-Nummerierung
        chapter_pattern = r'(kapitel|chapter|teil|track)\s*\d+'
        if re.search(chapter_pattern, first_track.lower()):
            return (2, 0.6)
        
        return (None, 0.0)
    
    def _count_tracks(self, tracks: list) -> tuple[Optional[int], float]:
        """
        Heuristik basierend auf Track-Anzahl
        
        Returns:
            (Kategorie, Confidence) oder (None, 0.0)
        """
        track_count = len(tracks) if tracks else 0
        
        if track_count == 0:
            return (None, 0.0)
        
        # Hörbücher haben oft wenige, lange Tracks (1-20)
        # Oder viele kurze Kapitel (20-99)
        # Musik-Alben: typisch 8-20 Tracks
        # Hörspiele für Kinder: oft 5-15 Tracks
        
        # Diese Heuristik ist schwach, daher niedrige Confidence
        if track_count <= 5:
            return (2, 0.3)  # Wahrscheinlich Hörbuch
        elif track_count > 50:
            return (2, 0.4)  # Viele Kapitel = Hörbuch
        
        return (None, 0.0)
    
    def categorize(self, artist: str, album: str, 
                   genre: Optional[str] = None,
                   tracks: Optional[list] = None,
                   year: Optional[int] = None) -> CategoryResult:
        """
        Kategorisiert eine CD
        
        Args:
            artist: Künstler/Interpret
            album: Album-Titel
            genre: Genre (optional)
            tracks: Track-Liste (optional)
            year: Erscheinungsjahr (optional)
            
        Returns:
            CategoryResult mit Kategorie und Confidence
        """
        self.logger.info(f"Kategorisiere: {artist} - {album}")
        
        # Sammle alle Scores
        scores = {1: 0.0, 2: 0.0, 3: 0.0}
        reasons = []
        
        # 1. Artist-Analyse (hohes Gewicht)
        cat, conf = self._analyze_artist(artist)
        if cat:
            scores[cat] += conf * 1.5
            reasons.append(f"Artist: {artist} → Kat.{cat}")
        
        # 2. Album-Analyse (hohes Gewicht)
        cat, conf = self._analyze_album(album)
        if cat:
            scores[cat] += conf * 1.5
            reasons.append(f"Album: {album} → Kat.{cat}")
        
        # 3. Genre-Analyse (mittleres Gewicht)
        cat, conf = self._analyze_genre(genre)
        if cat:
            scores[cat] += conf * 1.0
            reasons.append(f"Genre: {genre} → Kat.{cat}")
        
        # 4. Track-Analyse (niedriges Gewicht)
        if tracks:
            cat, conf = self._analyze_tracks(tracks)
            if cat:
                scores[cat] += conf * 0.8
                reasons.append(f"Tracks → Kat.{cat}")
            
            # Track-Count Heuristik
            cat, conf = self._count_tracks(tracks)
            if cat:
                scores[cat] += conf * 0.5
        
        # Bestimme Kategorie mit höchstem Score
        max_category = max(scores, key=scores.get)
        max_score = scores[max_category]
        
        # Normalisiere Score zu Confidence (0.0 - 1.0)
        # Max möglicher Score: ~4.8
        confidence = min(max_score / 3.0, 1.0)
        
        # Falls kein klarer Winner: Default zu Kategorie 3 (Musik)
        if confidence < 0.3:
            max_category = 3
            confidence = 0.5
            reason = "Default: Keine eindeutige Kategorisierung → Musik"
        else:
            reason = "; ".join(reasons) if reasons else "Heuristik"
        
        category_names = {
            1: "Kinderinhalte",
            2: "Hörbücher",
            3: "Musik"
        }
        
        result = CategoryResult(
            category=max_category,
            category_name=category_names[max_category],
            confidence=confidence,
            reason=reason
        )
        
        self.logger.info(
            f"✅ Kategorie {result.category} ({result.category_name}) "
            f"mit {result.confidence:.1%} Confidence"
        )
        self.logger.debug(f"   Grund: {result.reason}")
        
        return result


if __name__ == "__main__":
    # Test des Categorizers
    import sys
    sys.path.insert(0, '/root/projects/cd-ripper/src')
    from utils import load_config, setup_logging
    from cd_identifier import CDIdentifier
    
    print("Testing CD Categorizer...")
    
    # Setup
    config = load_config()
    logger = setup_logging(config)
    
    categorizer = CDCategorizer()
    
    # Test-Fälle
    print("\n📝 Test-Kategorisierungen:")
    
    test_cases = [
        ("Bibi Blocksberg", "Hexen hexen überall", None, None),
        ("Stephen King", "ES - Das Hörbuch", "Audiobook", None),
        ("Pink Floyd", "The Dark Side of the Moon", "Album", None),
        ("Die drei ???", "Folge 1: Der Super-Papagei", "Hörspiel", None),
        ("Various Artists", "Bravo Hits 100", "Compilation", None),
    ]
    
    for artist, album, genre, tracks in test_cases:
        result = categorizer.categorize(artist, album, genre, tracks)
        print(f"  {artist} - {album}")
        print(f"    → Kategorie {result.category} ({result.category_name}) @ {result.confidence:.0%}")
        print()
    
    # Test mit echter CD falls vorhanden
    print("\n🎵 Test mit eingelegter CD:")
    try:
        device = config.get('ripper', {}).get('device', '/dev/sr0')
        identifier = CDIdentifier(device=device)
        album_info = identifier.identify_cd()
        
        if album_info:
            result = categorizer.categorize(
                artist=album_info.artist,
                album=album_info.album,
                genre=album_info.genre,
                tracks=album_info.tracks,
                year=album_info.year
            )
            print(f"  CD: {album_info.artist} - {album_info.album}")
            print(f"  → Kategorie {result.category} ({result.category_name})")
            print(f"  → Confidence: {result.confidence:.0%}")
            print(f"  → Format: {'MP3 320kbps' if result.category in [1,2] else 'FLAC Lossless'}")
        else:
            print("  ℹ️  Keine CD zur Kategorisierung gefunden")
    except Exception as e:
        print(f"  ⚠️  Fehler: {e}")
    
    print("\n🎉 Categorizer Tests abgeschlossen!")
