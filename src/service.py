#!/usr/bin/env python3
"""
CD-Ripper Service Launcher
Startet Main Service und Web Interface in separaten Threads
"""

import sys
import logging
import threading
import signal
from pathlib import Path

# Service-Module importieren
from main import CDRipperService
from web_interface import start_web_interface


class ServiceLauncher:
    """
    Startet und verwaltet beide Services
    """
    
    def __init__(self, config_path: str):
        self.config_path = config_path
        self.main_service = None
        self.web_thread = None
        self.running = True
        
        # Signal-Handler
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)
        
    def _signal_handler(self, signum, frame):
        """Handler für Shutdown-Signale"""
        print(f"\n⚠️  Signal {signum} empfangen, fahre Services herunter...")
        self.shutdown()
        
    def start_web_interface(self):
        """Startet Web-Interface in separatem Thread"""
        try:
            print("🌐 Starte Web-Interface...")
            # Web-Interface aus config lesen
            import yaml
            with open(self.config_path) as f:
                config = yaml.safe_load(f)
            
            web_config = config.get('web_interface', {})
            host = web_config.get('host', '0.0.0.0')
            port = web_config.get('port', 5000)
            
            start_web_interface(host=host, port=port)
        except Exception as e:
            print(f"❌ Web-Interface Fehler: {e}")
            
    def start_main_service(self):
        """Startet Main CD-Ripper Service"""
        try:
            print("💿 Starte CD-Ripper Service...")
            self.main_service = CDRipperService(self.config_path)
            self.main_service.run()
        except Exception as e:
            print(f"❌ Main Service Fehler: {e}")
            
    def run(self):
        """Startet beide Services"""
        print("=" * 60)
        print("🎵 CD-RIPPER SERVICE")
        print("=" * 60)
        
        # Web-Interface in separatem Thread starten
        self.web_thread = threading.Thread(
            target=self.start_web_interface,
            daemon=True,
            name="WebInterface"
        )
        self.web_thread.start()
        
        # Kurz warten bis Web-Interface läuft
        import time
        time.sleep(2)
        
        print("✅ Alle Services gestartet")
        print("=" * 60)
        print("Web-Interface: http://0.0.0.0:5000")
        print("Drücke Ctrl+C zum Beenden")
        print("=" * 60)
        
        # Main Service im Hauptthread (blockiert)
        try:
            self.start_main_service()
        except KeyboardInterrupt:
            print("\n⚠️  Keyboard Interrupt empfangen")
        finally:
            self.shutdown()
            
    def shutdown(self):
        """Sauberes Herunterfahren"""
        if not self.running:
            return
            
        self.running = False
        print("\n🛑 Fahre Services herunter...")
        
        if self.main_service:
            print("   - Stoppe CD-Ripper Service...")
            self.main_service.shutdown()
            
        print("✅ Services beendet")
        sys.exit(0)


def main():
    """Haupteinstiegspunkt"""
    # Konfigurationsdatei
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    
    if not config_path.exists():
        print(f"❌ Fehler: Konfigurationsdatei nicht gefunden: {config_path}")
        print("   Erstelle config/config.yaml aus config/config.yaml.example")
        sys.exit(1)
    
    # Service Launcher starten
    launcher = ServiceLauncher(str(config_path))
    
    try:
        launcher.run()
    except Exception as e:
        print(f"❌ Fataler Fehler: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
