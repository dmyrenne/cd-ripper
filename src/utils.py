#!/usr/bin/env python3
"""
Utility Functions für CD-Ripper
Logging-Setup, Dateinamen-Bereinigung, Config-Loading
"""

import logging
import os
import re
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from logging.handlers import RotatingFileHandler


def setup_logging(config: Dict[str, Any]) -> logging.Logger:
    """
    Richtet das Logging-System ein
    
    Args:
        config: Konfigurations-Dictionary mit logging-Parametern
        
    Returns:
        Konfigurierter Logger
    """
    log_config = config.get('logging', {})
    log_level = getattr(logging, log_config.get('level', 'INFO'))
    log_file = log_config.get('file', '/root/projects/cd-ripper/logs/ripper.log')
    max_bytes = log_config.get('max_bytes', 10485760)  # 10MB
    backup_count = log_config.get('backup_count', 5)
    console_output = log_config.get('console_output', True)
    
    # Logger erstellen
    logger = logging.getLogger('cd_ripper')
    logger.setLevel(log_level)
    
    # Bestehende Handler entfernen (falls vorhanden)
    logger.handlers.clear()
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File Handler mit Rotation
    log_dir = Path(log_file).parent
    log_dir.mkdir(parents=True, exist_ok=True)
    
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(log_level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Console Handler (optional)
    if console_output:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    logger.info("=" * 70)
    logger.info("CD-Ripper Service gestartet")
    logger.info("=" * 70)
    
    return logger


def load_config(config_path: str = "/root/projects/cd-ripper/config/config.yaml") -> Dict[str, Any]:
    """
    Lädt die YAML-Konfigurationsdatei
    
    Args:
        config_path: Pfad zur config.yaml
        
    Returns:
        Konfigurations-Dictionary
        
    Raises:
        FileNotFoundError: Wenn Config-Datei nicht existiert
        yaml.YAMLError: Bei ungültigem YAML
    """
    config_file = Path(config_path)
    
    if not config_file.exists():
        raise FileNotFoundError(f"Konfigurationsdatei nicht gefunden: {config_path}")
    
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    return config


def sanitize_filename(filename: str) -> str:
    """
    Bereinigt Dateinamen von ungültigen Zeichen
    
    Args:
        filename: Original-Dateiname
        
    Returns:
        Bereinigter Dateiname
    """
    # Ungültige Zeichen für Dateisysteme
    invalid_chars = r'[<>:"/\\|?*\x00-\x1f]'
    
    # Ersetzen durch Unterstrich
    sanitized = re.sub(invalid_chars, '_', filename)
    
    # Mehrfache Unterstriche reduzieren
    sanitized = re.sub(r'_+', '_', sanitized)
    
    # Führende/Trailing Leerzeichen und Punkte entfernen
    sanitized = sanitized.strip(' .')
    
    # Leere Strings abfangen
    if not sanitized:
        sanitized = "unknown"
    
    return sanitized


def sanitize_path(path: str) -> str:
    """
    Bereinigt Pfad-Komponenten
    
    Args:
        path: Original-Pfad
        
    Returns:
        Bereinigter Pfad
    """
    parts = path.split('/')
    sanitized_parts = [sanitize_filename(part) for part in parts if part]
    return '/'.join(sanitized_parts)


def ensure_directory(directory: str) -> Path:
    """
    Stellt sicher, dass ein Verzeichnis existiert
    
    Args:
        directory: Pfad zum Verzeichnis
        
    Returns:
        Path-Objekt des Verzeichnisses
    """
    dir_path = Path(directory)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def format_filename(pattern: str, track_num: int, title: str, artist: str = "", 
                   album: str = "", extension: str = "") -> str:
    """
    Formatiert Dateinamen nach Pattern
    
    Args:
        pattern: Pattern-String (z.B. "{track:02d} - {title}")
        track_num: Track-Nummer
        title: Track-Titel
        artist: Künstler (optional)
        album: Album (optional)
        extension: Dateiendung (optional)
        
    Returns:
        Formatierter Dateiname
    """
    # Sanitize alle Eingaben
    title = sanitize_filename(title)
    artist = sanitize_filename(artist)
    album = sanitize_filename(album)
    
    # Format mit verfügbaren Variablen
    filename = pattern.format(
        track=track_num,
        title=title,
        artist=artist,
        album=album
    )
    
    # Extension hinzufügen falls vorhanden
    if extension:
        if not extension.startswith('.'):
            extension = f".{extension}"
        filename += extension
    
    return filename


def get_category_remote_path(config: Dict[str, Any], category: int) -> str:
    """
    Gibt den Remote-Pfad für eine Kategorie zurück
    
    Args:
        config: Konfigurations-Dictionary
        category: Kategorie-Nummer (1, 2, oder 3)
        
    Returns:
        Remote-Pfad für die Kategorie
    """
    remote_paths = config.get('sync', {}).get('remote_paths', {})
    category_key = f"category_{category}"
    
    return remote_paths.get(category_key, remote_paths.get('category_3'))


def bytes_to_human(num_bytes: int) -> str:
    """
    Konvertiert Bytes in menschenlesbare Größe
    
    Args:
        num_bytes: Anzahl Bytes
        
    Returns:
        Formatierter String (z.B. "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if num_bytes < 1024.0:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024.0
    return f"{num_bytes:.1f} PB"


def seconds_to_mmss(seconds: int) -> str:
    """
    Konvertiert Sekunden in MM:SS Format
    
    Args:
        seconds: Anzahl Sekunden
        
    Returns:
        Formatierter String (z.B. "03:45")
    """
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


if __name__ == "__main__":
    # Test der Utility-Funktionen
    print("Testing Utility Functions...")
    
    # Test Config Loading
    try:
        config = load_config()
        print(f"✅ Config geladen: {len(config)} Hauptschlüssel")
    except Exception as e:
        print(f"❌ Config-Fehler: {e}")
    
    # Test Logging
    logger = setup_logging(config)
    logger.info("Test-Log-Nachricht")
    logger.debug("Debug-Nachricht (sollte nur bei DEBUG-Level sichtbar sein)")
    print("✅ Logging konfiguriert")
    
    # Test Filename Sanitization
    test_filenames = [
        "Track 01: Hello/World?.mp3",
        "Artist <Unknown> - Album.flac",
        "../../escape/attempt.wav",
        ""
    ]
    for fn in test_filenames:
        sanitized = sanitize_filename(fn)
        print(f"  '{fn}' -> '{sanitized}'")
    print("✅ Filename Sanitization")
    
    # Test Format
    formatted = format_filename(
        "{track:02d} - {title}",
        track_num=5,
        title="Test Song",
        extension="flac"
    )
    print(f"✅ Format: {formatted}")
    
    # Test Human Readable
    print(f"✅ Bytes: {bytes_to_human(1536000)} = 1.5 MB")
    print(f"✅ Time: {seconds_to_mmss(225)} = 3:45")
    
    print("\n🎉 Alle Tests erfolgreich!")
