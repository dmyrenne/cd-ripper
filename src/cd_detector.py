#!/usr/bin/env python3
"""
CD Detection Module
Erkennt das Einlegen von Audio-CDs via Polling
"""

import logging
import time
import os
import subprocess
from pathlib import Path
from typing import Optional, Callable
from dataclasses import dataclass


@dataclass
class CDInfo:
    """Informationen über eine erkannte CD"""
    device: str
    present: bool
    is_audio: bool = False
    disc_id: Optional[str] = None


class CDDetector:
    """
    Erkennt Audio-CDs durch Polling des CD-ROM Devices
    """
    
    def __init__(self, device: str = "/dev/sr0", poll_interval: int = 5):
        """
        Initialisiert den CD-Detector
        
        Args:
            device: CD-ROM Device-Pfad
            poll_interval: Polling-Intervall in Sekunden
        """
        self.device = device
        self.poll_interval = poll_interval
        self.logger = logging.getLogger('cd_ripper.detector')
        self._last_state = None
        self._running = False
        
    def check_device_exists(self) -> bool:
        """
        Prüft, ob das CD-ROM Device existiert
        
        Returns:
            True wenn Device existiert
        """
        return Path(self.device).exists()
    
    def is_cd_present(self) -> bool:
        """
        Prüft, ob eine CD im Laufwerk ist
        
        Returns:
            True wenn CD vorhanden
        """
        if not self.check_device_exists():
            return False
        
        try:
            # Versuche Disc-Status zu lesen
            result = subprocess.run(
                ['cdparanoia', '-vsQ'],
                env={'CDDA_DEVICE': self.device},
                capture_output=True,
                text=True,
                timeout=5
            )
            
            # cdparanoia gibt Exit-Code 0 wenn Audio-CD erkannt
            # Exit-Code 1 wenn keine CD oder keine Audio-CD
            return result.returncode == 0
            
        except subprocess.TimeoutExpired:
            self.logger.warning(f"Timeout beim Prüfen von {self.device}")
            return False
        except FileNotFoundError:
            self.logger.error("cdparanoia nicht gefunden!")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim CD-Check: {e}")
            return False
    
    def get_cd_info(self) -> CDInfo:
        """
        Sammelt Informationen über die eingelegte CD
        
        Returns:
            CDInfo-Objekt mit CD-Details
        """
        cd_info = CDInfo(
            device=self.device,
            present=False,
            is_audio=False
        )
        
        if not self.check_device_exists():
            self.logger.debug(f"Device {self.device} existiert nicht")
            return cd_info
        
        try:
            # Prüfe mit cdparanoia ob Audio-CD vorhanden
            result = subprocess.run(
                ['cdparanoia', '-vsQ'],
                env={'CDDA_DEVICE': self.device},
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                cd_info.present = True
                cd_info.is_audio = True
                self.logger.debug("Audio-CD erkannt")
            else:
                # Prüfe ob irgendeine Disc vorhanden ist
                # (könnte Daten-CD sein)
                try:
                    with open(self.device, 'rb') as f:
                        f.read(1)
                    cd_info.present = True
                    cd_info.is_audio = False
                    self.logger.debug("Nicht-Audio Medium erkannt")
                except:
                    cd_info.present = False
                    
        except subprocess.TimeoutExpired:
            self.logger.warning("Timeout beim CD-Info Abruf")
        except Exception as e:
            self.logger.error(f"Fehler beim CD-Info Abruf: {e}")
        
        return cd_info
    
    def wait_for_cd(self, timeout: Optional[int] = None) -> CDInfo:
        """
        Wartet auf das Einlegen einer Audio-CD
        
        Args:
            timeout: Optional Timeout in Sekunden
            
        Returns:
            CDInfo wenn Audio-CD erkannt, sonst None bei Timeout
        """
        self.logger.info(f"Warte auf Audio-CD in {self.device}...")
        start_time = time.time()
        
        while True:
            cd_info = self.get_cd_info()
            
            if cd_info.present and cd_info.is_audio:
                self.logger.info("✅ Audio-CD erkannt!")
                return cd_info
            
            # Timeout-Check
            if timeout and (time.time() - start_time) > timeout:
                self.logger.warning(f"Timeout nach {timeout}s erreicht")
                return None
            
            time.sleep(self.poll_interval)
    
    def start_monitoring(self, on_cd_insert: Callable[[CDInfo], None],
                        on_cd_eject: Optional[Callable[[], None]] = None):
        """
        Startet kontinuierliches Monitoring
        
        Args:
            on_cd_insert: Callback wenn Audio-CD eingelegt wird
            on_cd_eject: Optional Callback wenn CD ausgeworfen wird
        """
        self.logger.info("Starte CD-Monitoring...")
        self._running = True
        self._last_state = False
        
        try:
            while self._running:
                cd_info = self.get_cd_info()
                current_state = cd_info.present and cd_info.is_audio
                
                # State-Change Detection
                if current_state and not self._last_state:
                    # CD eingelegt
                    self.logger.info("🎵 Audio-CD eingelegt!")
                    on_cd_insert(cd_info)
                    
                elif not current_state and self._last_state:
                    # CD ausgeworfen
                    self.logger.info("📤 CD ausgeworfen")
                    if on_cd_eject:
                        on_cd_eject()
                
                self._last_state = current_state
                time.sleep(self.poll_interval)
                
        except KeyboardInterrupt:
            self.logger.info("Monitoring durch User beendet")
        finally:
            self._running = False
    
    def stop_monitoring(self):
        """Stoppt das Monitoring"""
        self.logger.info("Stoppe CD-Monitoring...")
        self._running = False
    
    def eject_cd(self) -> bool:
        """
        Wirft die CD aus
        
        Returns:
            True bei Erfolg
        """
        try:
            result = subprocess.run(
                ['eject', self.device],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info(f"CD aus {self.device} ausgeworfen")
                return True
            else:
                self.logger.error(f"Eject fehlgeschlagen: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout beim Auswerfen")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Auswerfen: {e}")
            return False


if __name__ == "__main__":
    # Test des CD-Detectors
    import sys
    sys.path.insert(0, '/root/projects/cd-ripper/src')
    from utils import load_config, setup_logging
    
    print("Testing CD Detector...")
    
    # Setup
    config = load_config()
    logger = setup_logging(config)
    
    device = config.get('ripper', {}).get('device', '/dev/sr0')
    detector = CDDetector(device=device, poll_interval=2)
    
    # Test Device-Existenz
    if detector.check_device_exists():
        print(f"✅ Device {device} existiert")
    else:
        print(f"❌ Device {device} nicht gefunden")
        sys.exit(1)
    
    # Test CD-Info
    cd_info = detector.get_cd_info()
    print(f"CD vorhanden: {cd_info.present}")
    print(f"Audio-CD: {cd_info.is_audio}")
    
    if cd_info.present and cd_info.is_audio:
        print("✅ Audio-CD bereits eingelegt!")
    else:
        print("\n⏳ Warte 10 Sekunden auf CD-Einlage (Test-Modus)...")
        cd_info = detector.wait_for_cd(timeout=10)
        
        if cd_info:
            print("✅ Audio-CD erkannt im Test-Modus!")
        else:
            print("ℹ️  Keine CD eingelegt im Test-Zeitraum (normal für Tests)")
    
    print("\n🎉 CD-Detector Tests abgeschlossen!")
