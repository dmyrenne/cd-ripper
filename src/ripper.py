#!/usr/bin/env python3
"""
CD Ripper Module
Extrahiert Audio-Tracks von CDs mit cdparanoia
"""

import logging
import subprocess
import re
from pathlib import Path
from typing import Optional, Callable, List
from dataclasses import dataclass


@dataclass
class RipProgress:
    """Progress-Info während des Rippings"""
    track_number: int
    track_total: int
    percent: int
    status: str


class CDRipper:
    """
    Rippt Audio-CDs zu WAV-Dateien
    """
    
    def __init__(self, device: str = "/dev/sr0", quality: str = "paranoia"):
        """
        Initialisiert den CD-Ripper
        
        Args:
            device: CD-ROM Device-Pfad
            quality: Ripping-Qualität (paranoia, fast, normal)
        """
        self.device = device
        self.quality = quality
        self.logger = logging.getLogger('cd_ripper.ripper')
        
        # Quality-Mapping zu cdparanoia-Flags
        self.quality_flags = {
            'paranoia': '-Z',  # Maximum paranoia/overlap
            'fast': '-Y',      # Disable extra paranoia
            'normal': ''       # Standard
        }
        
    def _parse_progress(self, line: str) -> Optional[int]:
        """
        Parst Progress aus cdparanoia-Output
        
        Args:
            line: Ausgabe-Zeile von cdparanoia
            
        Returns:
            Prozent-Wert oder None
        """
        # cdparanoia gibt Progress in verschiedenen Formaten aus
        # Beispiel: "  ##: 0 [read] 0 [wrote] 0.0%"
        match = re.search(r'(\d+\.?\d*)%', line)
        if match:
            try:
                return int(float(match.group(1)))
            except ValueError:
                pass
        return None
    
    def rip_track(self, track_number: int, output_file: str,
                  progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Rippt einen einzelnen Track
        
        Args:
            track_number: Track-Nummer (1-basiert)
            output_file: Ausgabe-Datei (WAV)
            progress_callback: Optional Callback für Progress-Updates
            
        Returns:
            True bei Erfolg
        """
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Rippe Track {track_number} → {output_path.name}")
        
        # cdparanoia-Kommando
        quality_flag = self.quality_flags.get(self.quality, '')
        cmd = ['cdparanoia']
        
        if quality_flag:
            cmd.append(quality_flag)
        
        cmd.extend([
            '-d', self.device,
            str(track_number),
            str(output_path)
        ])
        
        self.logger.debug(f"Kommando: {' '.join(cmd)}")
        
        try:
            # Prozess starten
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            last_percent = -1
            
            # Output lesen
            for line in process.stdout:
                line = line.strip()
                
                if line:
                    self.logger.debug(f"cdparanoia: {line}")
                    
                    # Progress parsen
                    percent = self._parse_progress(line)
                    if percent is not None and percent != last_percent:
                        last_percent = percent
                        if progress_callback:
                            progress_callback(percent)
                        
                        # Nur alle 10% loggen
                        if percent % 10 == 0:
                            self.logger.info(f"  Track {track_number}: {percent}%")
            
            # Auf Prozess-Ende warten
            returncode = process.wait()
            
            if returncode == 0:
                # Prüfe ob Datei existiert und Größe > 0
                if output_path.exists() and output_path.stat().st_size > 0:
                    size_mb = output_path.stat().st_size / (1024 * 1024)
                    self.logger.info(f"✅ Track {track_number} erfolgreich gerippt ({size_mb:.1f} MB)")
                    return True
                else:
                    self.logger.error(f"❌ Track {track_number}: Ausgabedatei fehlt oder leer")
                    return False
            else:
                self.logger.error(f"❌ Track {track_number}: cdparanoia Exit-Code {returncode}")
                return False
                
        except subprocess.SubprocessError as e:
            self.logger.error(f"❌ Fehler beim Rippen von Track {track_number}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"❌ Unerwarteter Fehler bei Track {track_number}: {e}")
            return False
    
    def rip_all_tracks(self, track_count: int, output_dir: str,
                       filename_pattern: str = "track_{:02d}.wav",
                       progress_callback: Optional[Callable[[RipProgress], None]] = None) -> List[str]:
        """
        Rippt alle Tracks einer CD
        
        Args:
            track_count: Anzahl Tracks
            output_dir: Ausgabe-Verzeichnis
            filename_pattern: Pattern für Dateinamen (mit {}-Platzhalter für Track-Nr)
            progress_callback: Optional Callback für Progress-Updates
            
        Returns:
            Liste der erfolgreich gerippten Dateien
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Starte Ripping von {track_count} Tracks...")
        
        ripped_files = []
        
        for track_num in range(1, track_count + 1):
            filename = filename_pattern.format(track_num)
            output_file = output_path / filename
            
            # Progress-Callback für einzelnen Track
            def track_progress(percent: int):
                if progress_callback:
                    progress = RipProgress(
                        track_number=track_num,
                        track_total=track_count,
                        percent=percent,
                        status=f"Ripping Track {track_num}/{track_count}"
                    )
                    progress_callback(progress)
            
            # Track rippen
            success = self.rip_track(track_num, str(output_file), track_progress)
            
            if success:
                ripped_files.append(str(output_file))
            else:
                self.logger.warning(f"⚠️  Track {track_num} übersprungen")
                # Optional: Bei Fehler abbrechen oder weitermachen?
                # Hier: weitermachen
        
        self.logger.info(f"✅ Ripping abgeschlossen: {len(ripped_files)}/{track_count} Tracks erfolgreich")
        
        return ripped_files
    
    def verify_track(self, track_number: int) -> bool:
        """
        Verifiziert einen Track ohne zu rippen
        
        Args:
            track_number: Track-Nummer
            
        Returns:
            True wenn Track lesbar
        """
        try:
            cmd = [
                'cdparanoia',
                '-d', self.device,
                '-vQ'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Prüfe ob Track in Output erscheint
            if f"{track_number}." in result.stderr:
                return True
            
            return False
            
        except Exception as e:
            self.logger.error(f"Fehler beim Verifizieren von Track {track_number}: {e}")
            return False
    
    def get_track_count(self) -> Optional[int]:
        """
        Ermittelt Anzahl der Tracks auf der CD
        
        Returns:
            Anzahl Tracks oder None bei Fehler
        """
        try:
            cmd = ['cdparanoia', '-d', self.device, '-Q']
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            # Parse Output für Track-Count
            # cdparanoia gibt Zeilen wie "  1." für jeden Track aus
            track_lines = [line for line in result.stderr.split('\n') 
                          if re.match(r'^\s+\d+\.', line)]
            
            track_count = len(track_lines)
            
            if track_count > 0:
                self.logger.debug(f"Erkannte {track_count} Tracks")
                return track_count
            else:
                self.logger.warning("Keine Tracks erkannt")
                return None
                
        except Exception as e:
            self.logger.error(f"Fehler beim Ermitteln der Track-Anzahl: {e}")
            return None


if __name__ == "__main__":
    # Test des Rippers
    import sys
    sys.path.insert(0, '/root/projects/cd-ripper/src')
    from utils import load_config, setup_logging
    
    print("Testing CD Ripper...")
    
    # Setup
    config = load_config()
    logger = setup_logging(config)
    
    device = config.get('ripper', {}).get('device', '/dev/sr0')
    quality = config.get('ripper', {}).get('quality', 'paranoia')
    
    ripper = CDRipper(device=device, quality=quality)
    
    # Test Track-Count
    track_count = ripper.get_track_count()
    if track_count:
        print(f"✅ CD hat {track_count} Tracks")
    else:
        print("❌ Konnte Track-Anzahl nicht ermitteln")
        sys.exit(1)
    
    # Test: Rippe ersten Track als Test
    print(f"\n⏳ Rippe Track 1 als Test (Qualität: {quality})...")
    
    test_output = "/root/projects/cd-ripper/output/test_rip_track01.wav"
    
    def progress_callback(percent: int):
        if percent % 25 == 0:  # Nur alle 25% ausgeben
            print(f"  Progress: {percent}%")
    
    success = ripper.rip_track(1, test_output, progress_callback)
    
    if success:
        import os
        size_mb = os.path.getsize(test_output) / (1024 * 1024)
        print(f"✅ Track 1 erfolgreich gerippt!")
        print(f"   Datei: {test_output}")
        print(f"   Größe: {size_mb:.1f} MB")
        print(f"\n💡 Zum Anhören: aplay {test_output}")
    else:
        print("❌ Ripping fehlgeschlagen")
    
    print("\n🎉 Ripper Tests abgeschlossen!")
    print("ℹ️  Test-Datei wird nicht automatisch gelöscht zum Testen/Anhören")
