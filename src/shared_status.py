#!/usr/bin/env python3
"""
Shared Status Module
Ermöglicht Kommunikation zwischen Main Service und Web Interface via Datei
"""

import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import fcntl


class SharedStatus:
    """
    Thread-sicherer Status-Speicher via JSON-Datei
    """
    
    def __init__(self, status_file: str = "/tmp/cd-ripper-status.json"):
        self.status_file = Path(status_file)
        
    def _read_status(self) -> Dict[str, Any]:
        """Liest Status aus Datei"""
        if not self.status_file.exists():
            return {}
        
        try:
            with open(self.status_file, 'r') as f:
                fcntl.flock(f, fcntl.LOCK_SH)
                data = json.load(f)
                fcntl.flock(f, fcntl.LOCK_UN)
                return data
        except:
            return {}
    
    def _write_status(self, data: Dict[str, Any]):
        """Schreibt Status in Datei"""
        try:
            with open(self.status_file, 'w') as f:
                fcntl.flock(f, fcntl.LOCK_EX)
                json.dump(data, f)
                fcntl.flock(f, fcntl.LOCK_UN)
        except Exception as e:
            print(f"Fehler beim Status-Schreiben: {e}")
    
    def update_cd(self, name: str, artist: str, cover_path: Optional[str] = None):
        """Aktualisiert CD-Informationen"""
        status = self._read_status()
        status['current_cd'] = {
            'name': name,
            'artist': artist,
            'cover_path': cover_path,
            'cover_url': '/api/cover' if cover_path else None
        }
        status['last_update'] = datetime.now().isoformat()
        self._write_status(status)
    
    def update_progress(self, step: str, progress: int, current_track: int = 0, total_tracks: int = 0):
        """Aktualisiert Progress"""
        status = self._read_status()
        status['processing'] = True
        status['current_step'] = step
        status['progress'] = progress
        status['current_track'] = current_track
        status['total_tracks'] = total_tracks
        status['last_update'] = datetime.now().isoformat()
        self._write_status(status)
    
    def set_processing(self, processing: bool):
        """Setzt Processing-Status"""
        status = self._read_status()
        status['processing'] = processing
        status['last_update'] = datetime.now().isoformat()
        self._write_status(status)
    
    def get_status(self) -> Dict[str, Any]:
        """Liest kompletten Status"""
        return self._read_status()
    
    def clear(self):
        """Setzt Status zurück (löscht CD-Info und Progress)"""
        self._write_status({
            'current_cd': None,
            'processing': False,
            'current_step': None,
            'progress': 0,
            'current_track': 0,
            'total_tracks': 0,
            'last_update': datetime.now().isoformat()
        })
    
    def reset(self):
        """Alias für clear() - für Abwärtskompatibilität"""
        self.clear()
    
    def save_cover(self, cover_data: bytes, output_dir: str = "/tmp"):
        """Speichert Cover-Datei"""
        try:
            cover_path = Path(output_dir) / "current-cover.jpg"
            with open(cover_path, 'wb') as f:
                f.write(cover_data)
            return str(cover_path)
        except Exception as e:
            print(f"Fehler beim Cover-Speichern: {e}")
            return None
