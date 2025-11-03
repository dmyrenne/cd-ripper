#!/usr/bin/env python3
"""
Audio Encoder Module
Konvertiert WAV zu FLAC/MP3 basierend auf Profilen
"""

import logging
import subprocess
import os
from pathlib import Path
from typing import Optional, Callable, Dict, Any


class AudioEncoder:
    """
    Konvertiert Audio-Dateien zu verschiedenen Formaten
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialisiert den Encoder
        
        Args:
            config: Konfigurations-Dictionary mit Profilen
        """
        self.config = config
        self.logger = logging.getLogger('cd_ripper.encoder')
        self.profiles = config.get('ripper', {}).get('profiles', {})
    
    def get_profile(self, category: int) -> Dict[str, Any]:
        """
        Gibt Encoding-Profil für Kategorie zurück
        
        Args:
            category: Kategorie-Nummer (1, 2, oder 3)
            
        Returns:
            Profil-Dictionary
        """
        category_key = f"category_{category}"
        profile = self.profiles.get(category_key, self.profiles.get('category_3'))
        self.logger.debug(f"Profil für Kategorie {category}: {profile}")
        return profile
    
    def encode_to_mp3(self, input_file: str, output_file: str,
                      bitrate: int = 320, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Konvertiert WAV zu MP3
        
        Args:
            input_file: Eingabe-WAV-Datei
            output_file: Ausgabe-MP3-Datei
            bitrate: Bitrate in kbps
            progress_callback: Optional Callback für Progress
            
        Returns:
            True bei Erfolg
        """
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        if not input_path.exists():
            self.logger.error(f"Eingabedatei nicht gefunden: {input_file}")
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Konvertiere zu MP3 ({bitrate} kbps): {output_path.name}")
        
        # lame-Kommando
        cmd = [
            'lame',
            '--preset', 'cbr', str(bitrate),  # Constant Bitrate
            '-h',  # High quality
            '--quiet',  # Weniger Output
            str(input_path),
            str(output_path)
        ]
        
        self.logger.debug(f"Kommando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 Minuten Timeout
            )
            
            if result.returncode == 0:
                if output_path.exists() and output_path.stat().st_size > 0:
                    size_mb = output_path.stat().st_size / (1024 * 1024)
                    self.logger.info(f"✅ MP3 erstellt ({size_mb:.1f} MB)")
                    return True
                else:
                    self.logger.error("MP3-Datei fehlt oder leer")
                    return False
            else:
                self.logger.error(f"lame Exit-Code {result.returncode}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout beim MP3-Encoding")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim MP3-Encoding: {e}")
            return False
    
    def encode_to_flac(self, input_file: str, output_file: str,
                       compression: int = 8, progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Konvertiert WAV zu FLAC
        
        Args:
            input_file: Eingabe-WAV-Datei
            output_file: Ausgabe-FLAC-Datei
            compression: Compression-Level (0-8)
            progress_callback: Optional Callback für Progress
            
        Returns:
            True bei Erfolg
        """
        input_path = Path(input_file)
        output_path = Path(output_file)
        
        if not input_path.exists():
            self.logger.error(f"Eingabedatei nicht gefunden: {input_file}")
            return False
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.logger.info(f"Konvertiere zu FLAC (Compression {compression}): {output_path.name}")
        
        # flac-Kommando
        cmd = [
            'flac',
            f'-{compression}',  # Compression-Level
            '--totally-silent',  # Kein Output
            '-f',  # Force overwrite
            '-o', str(output_path),
            str(input_path)
        ]
        
        self.logger.debug(f"Kommando: {' '.join(cmd)}")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 Minuten Timeout
            )
            
            if result.returncode == 0:
                if output_path.exists() and output_path.stat().st_size > 0:
                    size_mb = output_path.stat().st_size / (1024 * 1024)
                    input_size_mb = input_path.stat().st_size / (1024 * 1024)
                    ratio = (size_mb / input_size_mb) * 100 if input_size_mb > 0 else 0
                    self.logger.info(f"✅ FLAC erstellt ({size_mb:.1f} MB, {ratio:.0f}% vom Original)")
                    return True
                else:
                    self.logger.error("FLAC-Datei fehlt oder leer")
                    return False
            else:
                self.logger.error(f"flac Exit-Code {result.returncode}: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout beim FLAC-Encoding")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim FLAC-Encoding: {e}")
            return False
    
    def encode(self, input_file: str, output_file: str, category: int,
               progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Konvertiert Audio-Datei basierend auf Kategorie
        
        Args:
            input_file: Eingabe-Datei (WAV)
            output_file: Ausgabe-Datei (Endung bestimmt Format)
            category: Kategorie-Nummer (1, 2, oder 3)
            progress_callback: Optional Callback für Progress
            
        Returns:
            True bei Erfolg
        """
        profile = self.get_profile(category)
        format_type = profile.get('format', 'flac').lower()
        
        self.logger.info(f"Encode mit Profil: Kategorie {category} → {format_type.upper()}")
        
        if format_type == 'mp3':
            bitrate = profile.get('bitrate', 320)
            return self.encode_to_mp3(input_file, output_file, bitrate, progress_callback)
        
        elif format_type == 'flac':
            compression = profile.get('compression', 8)
            return self.encode_to_flac(input_file, output_file, compression, progress_callback)
        
        else:
            self.logger.error(f"Unbekanntes Format: {format_type}")
            return False
    
    def get_output_extension(self, category: int) -> str:
        """
        Gibt Dateiendung für Kategorie zurück
        
        Args:
            category: Kategorie-Nummer
            
        Returns:
            Dateiendung (z.B. "mp3" oder "flac")
        """
        profile = self.get_profile(category)
        return profile.get('format', 'flac').lower()
    
    def cleanup_wav(self, wav_file: str) -> bool:
        """
        Löscht temporäre WAV-Datei
        
        Args:
            wav_file: Pfad zur WAV-Datei
            
        Returns:
            True bei Erfolg
        """
        try:
            wav_path = Path(wav_file)
            if wav_path.exists():
                wav_path.unlink()
                self.logger.debug(f"WAV-Datei gelöscht: {wav_file}")
                return True
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Löschen von {wav_file}: {e}")
            return False


if __name__ == "__main__":
    # Test des Encoders
    import sys
    sys.path.insert(0, '/root/projects/cd-ripper/src')
    from utils import load_config, setup_logging
    
    print("Testing Audio Encoder...")
    
    # Setup
    config = load_config()
    logger = setup_logging(config)
    
    encoder = AudioEncoder(config)
    
    # Test-Datei (muss existieren vom Ripper-Test)
    test_wav = "/root/projects/cd-ripper/output/test_rip_track01.wav"
    
    if not Path(test_wav).exists():
        print(f"❌ Test-WAV nicht gefunden: {test_wav}")
        print("   Bitte zuerst ripper.py ausführen!")
        sys.exit(1)
    
    print(f"✅ Test-WAV gefunden: {test_wav}")
    
    # Test 1: MP3-Encoding (Kategorie 1)
    print("\n⏳ Test 1: Konvertiere zu MP3 (Kategorie 1 - Kinderinhalte)...")
    test_mp3 = "/root/projects/cd-ripper/output/test_encode_track01.mp3"
    success_mp3 = encoder.encode(test_wav, test_mp3, category=1)
    
    if success_mp3:
        size_mb = Path(test_mp3).stat().st_size / (1024 * 1024)
        print(f"✅ MP3 erstellt: {test_mp3} ({size_mb:.1f} MB)")
    else:
        print("❌ MP3-Encoding fehlgeschlagen")
    
    # Test 2: FLAC-Encoding (Kategorie 3)
    print("\n⏳ Test 2: Konvertiere zu FLAC (Kategorie 3 - Musik)...")
    test_flac = "/root/projects/cd-ripper/output/test_encode_track01.flac"
    success_flac = encoder.encode(test_wav, test_flac, category=3)
    
    if success_flac:
        size_mb = Path(test_flac).stat().st_size / (1024 * 1024)
        print(f"✅ FLAC erstellt: {test_flac} ({size_mb:.1f} MB)")
    else:
        print("❌ FLAC-Encoding fehlgeschlagen")
    
    # Vergleich
    if success_mp3 and success_flac:
        wav_size = Path(test_wav).stat().st_size / (1024 * 1024)
        mp3_size = Path(test_mp3).stat().st_size / (1024 * 1024)
        flac_size = Path(test_flac).stat().st_size / (1024 * 1024)
        
        print(f"\n📊 Größenvergleich:")
        print(f"   WAV:  {wav_size:6.1f} MB (100%)")
        print(f"   MP3:  {mp3_size:6.1f} MB ({(mp3_size/wav_size)*100:5.1f}%)")
        print(f"   FLAC: {flac_size:6.1f} MB ({(flac_size/wav_size)*100:5.1f}%)")
    
    print("\n🎉 Encoder Tests abgeschlossen!")
    print("ℹ️  Test-Dateien bleiben zum Testen/Anhören erhalten")
