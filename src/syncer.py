#!/usr/bin/env python3
"""
Server Sync Module
Synchronisiert gerippte Audio-Dateien mit Remote-Server via rsync
"""

import logging
import subprocess
import re
from pathlib import Path
from typing import Optional, Dict, Any, Callable


class ServerSyncer:
    """
    Synchronisiert Audio-Dateien mit Remote-Server
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialisiert den Syncer
        
        Args:
            config: Konfigurations-Dictionary
        """
        self.config = config
        self.logger = logging.getLogger('cd_ripper.syncer')
        
        # Sync-Konfiguration
        sync_config = config.get('sync', {})
        self.server = sync_config.get('host', sync_config.get('server', ''))
        self.user = sync_config.get('user', '')
        self.password = sync_config.get('password', '')
        self.method = sync_config.get('method', 'rsync')
        self.compression = sync_config.get('compression', True)
        self.delete_after_sync = sync_config.get('cleanup', sync_config.get('cleanup_temp', True))
        
        # Remote-Pfade pro Kategorie aus Config
        remote_paths_config = sync_config.get('remote_paths', {})
        self.remote_paths = {
            1: remote_paths_config.get('category_1', ''),
            2: remote_paths_config.get('category_2', ''),
            3: remote_paths_config.get('category_3', '')
        }
        
        # Validierung
        if not self.server:
            self.logger.warning("Kein Server-Host in Config angegeben")
        if not self.user:
            self.logger.warning("Kein SSH-User in Config angegeben")
        for cat, path in self.remote_paths.items():
            if not path:
                self.logger.warning(f"Kein Remote-Pfad für Kategorie {cat} in Config angegeben")
        
    def get_remote_path(self, category: int) -> str:
        """
        Gibt Remote-Pfad für Kategorie zurück
        
        Args:
            category: Kategorie-Nummer (1, 2, oder 3)
            
        Returns:
            Remote-Pfad
        """
        return self.remote_paths.get(category, self.remote_paths[3])
    
    def sync_directory(self, local_path: str, category: int,
                       progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Synchronisiert lokales Verzeichnis mit Remote-Server
        
        Args:
            local_path: Lokaler Pfad zum Verzeichnis
            category: Kategorie für Remote-Pfad-Auswahl
            progress_callback: Optional callback für Progress-Updates (0-100)
            
        Returns:
            True bei Erfolg, False bei Fehler
        """
        local_dir = Path(local_path)
        
        if not local_dir.exists():
            self.logger.error(f"Lokales Verzeichnis nicht gefunden: {local_path}")
            return False
        
        if not local_dir.is_dir():
            self.logger.error(f"Pfad ist kein Verzeichnis: {local_path}")
            return False
        
        # Remote-Pfad ermitteln
        remote_path = self.get_remote_path(category)
        remote_target = f"{self.user}@{self.server}:{remote_path}/"
        
        self.logger.info(f"Starte Sync von {local_path} nach {remote_target}")
        
        # rsync-Befehl zusammenbauen
        if self.method == 'rsync':
            success = self._sync_with_rsync(str(local_dir), remote_target, progress_callback)
            
            # Lokale Dateien nach erfolgreichem Sync löschen
            if success and self.delete_after_sync:
                self.logger.info("Sync erfolgreich, lösche lokale Dateien...")
                cleanup_success = self.cleanup_local(str(local_dir))
                if not cleanup_success:
                    self.logger.warning("Cleanup fehlgeschlagen, aber Sync war erfolgreich")
            
            return success
        else:
            self.logger.error(f"Unbekannte Sync-Methode: {self.method}")
            return False
    
    def _ensure_remote_directory(self, remote_target: str) -> bool:
        """
        Stellt sicher, dass das Remote-Verzeichnis existiert
        
        Args:
            remote_target: Remote-Ziel (user@host:path)
            
        Returns:
            True bei Erfolg
        """
        # Extrahiere Pfad aus user@host:path
        if ':' not in remote_target:
            self.logger.error(f"Ungültiges Remote-Target: {remote_target}")
            return False
        
        remote_host, remote_path = remote_target.rsplit(':', 1)
        # Entferne trailing slash
        remote_path = remote_path.rstrip('/')
        
        self.logger.debug(f"Erstelle Remote-Verzeichnis: {remote_path} auf {remote_host}")
        
        # SSH-Kommando zum Erstellen des Verzeichnisses
        ssh_cmd = []
        
        if self.password:
            ssh_cmd.extend(['sshpass', '-p', self.password])
        
        ssh_cmd.extend([
            'ssh',
            '-o', 'StrictHostKeyChecking=no',
            '-o', 'UserKnownHostsFile=/dev/null',
            '-o', 'LogLevel=ERROR',
            remote_host,
            f'mkdir -p "{remote_path}"'
        ])
        
        try:
            result = subprocess.run(
                ssh_cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                self.logger.debug(f"Remote-Verzeichnis bereit: {remote_path}")
                return True
            else:
                self.logger.error(f"Fehler beim Erstellen des Remote-Verzeichnisses: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("Timeout beim Erstellen des Remote-Verzeichnisses")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Erstellen des Remote-Verzeichnisses: {e}")
            return False
    
    def _sync_with_rsync(self, local_path: str, remote_target: str,
                         progress_callback: Optional[Callable[[int], None]] = None) -> bool:
        """
        Führt rsync-Sync durch
        
        Args:
            local_path: Lokaler Pfad
            remote_target: Remote-Ziel (user@host:path)
            progress_callback: Optional callback für Progress
            
        Returns:
            True bei Erfolg
        """
        # Remote-Verzeichnis erstellen, falls es nicht existiert
        if not self._ensure_remote_directory(remote_target):
            self.logger.error("Konnte Remote-Verzeichnis nicht erstellen")
            return False
        
        # rsync-Optionen
        rsync_cmd = []
        
        # sshpass für Passwort-Auth verwenden, falls Passwort gesetzt
        if self.password:
            rsync_cmd.extend(['sshpass', '-p', self.password])
        
        rsync_cmd.extend(['rsync', '-avh'])  # archive, verbose, human-readable
        
        # SSH-Optionen für rsync (wichtig für sshpass)
        ssh_opts = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=ERROR'
        rsync_cmd.extend(['-e', ssh_opts])
        
        if self.compression:
            rsync_cmd.append('-z')  # compression
        
        # Progress-Option
        rsync_cmd.append('--info=progress2')  # Gesamt-Progress statt per-File
        
        # Weitere Optionen
        rsync_cmd.extend([
            '--partial',  # Partielle Übertragungen fortsetzen
        ])
        
        # Quelle und Ziel
        # KEIN trailing slash - damit wird der Artist-Ordner selbst übertragen
        rsync_cmd.append(local_path)
        rsync_cmd.append(remote_target)
        
        # Maskiere Passwort im Log
        log_cmd = rsync_cmd.copy()
        if self.password and 'sshpass' in log_cmd:
            pwd_idx = log_cmd.index('-p') + 1
            log_cmd[pwd_idx] = '***'
        self.logger.info(f"rsync Befehl: {' '.join(log_cmd)}")
        
        try:
            # rsync ausführen
            result = subprocess.run(
                rsync_cmd,
                capture_output=True,
                text=True,
                timeout=300  # 5 Minuten Timeout
            )
            
            # Output loggen
            if result.stdout:
                for line in result.stdout.strip().split('\n'):
                    if line.strip():
                        self.logger.debug(f"rsync stdout: {line}")
                        
                        # Progress parsen
                        progress = self._parse_rsync_progress(line)
                        if progress is not None and progress_callback:
                            progress_callback(progress)
            
            if result.stderr:
                for line in result.stderr.strip().split('\n'):
                    if line.strip() and not line.startswith('Warning:'):
                        self.logger.warning(f"rsync stderr: {line}")
            
            # Return-Code prüfen
            if result.returncode == 0:
                self.logger.info(f"Sync erfolgreich abgeschlossen")
                return True
            else:
                self.logger.error(f"rsync fehlgeschlagen (Code {result.returncode})")
                return False
                
        except subprocess.TimeoutExpired:
            self.logger.error("rsync Timeout nach 5 Minuten")
            return False
        except FileNotFoundError as e:
            if 'sshpass' in str(e):
                self.logger.error("sshpass nicht gefunden. Bitte installieren: apt install sshpass")
            else:
                self.logger.error("rsync nicht gefunden. Bitte installieren: apt install rsync")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Sync: {e}", exc_info=True)
            return False
    
    def _parse_rsync_progress(self, line: str) -> Optional[int]:
        """
        Parst Progress aus rsync-Output
        
        Args:
            line: rsync-Output-Zeile
            
        Returns:
            Progress in Prozent (0-100) oder None
        """
        # rsync --info=progress2 Format: "1,234,567  45%  123.45kB/s    0:00:12"
        # Suche nach Prozent-Zeichen
        match = re.search(r'(\d+)%', line)
        if match:
            percent = int(match.group(1))
            return min(100, percent)  # Cap bei 100%
        return None
    
    def test_connection(self) -> bool:
        """
        Testet Verbindung zum Remote-Server
        
        Returns:
            True wenn erreichbar, False sonst
        """
        self.logger.info(f"Teste Verbindung zu {self.user}@{self.server}")
        
        try:
            # SSH-Test mit Timeout
            cmd = [
                'ssh',
                '-o', 'ConnectTimeout=5',
                '-o', 'BatchMode=yes',
                f"{self.user}@{self.server}",
                'echo "Connection OK"'
            ]
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                self.logger.info("Verbindung erfolgreich")
                return True
            else:
                self.logger.warning(f"Verbindung fehlgeschlagen: {result.stderr}")
                return False
                
        except FileNotFoundError:
            self.logger.warning("ssh nicht installiert - Connection-Test übersprungen")
            return False
        except subprocess.TimeoutExpired:
            self.logger.error("Verbindungstest timeout")
            return False
        except Exception as e:
            self.logger.error(f"Fehler beim Verbindungstest: {e}")
            return False
    
    def cleanup_local(self, local_path: str) -> bool:
        """
        Löscht lokale Dateien nach erfolgreichem Sync
        
        Args:
            local_path: Zu löschendes Verzeichnis oder dessen Inhalt
            
        Returns:
            True bei Erfolg
        """
        if not self.delete_after_sync:
            self.logger.debug("Lokales Cleanup deaktiviert")
            return True
        
        local_dir = Path(local_path)
        
        if not local_dir.exists():
            self.logger.warning(f"Verzeichnis existiert nicht: {local_path}")
            return True
        
        try:
            # Lösche nur den Inhalt, nicht das Verzeichnis selbst
            import shutil
            file_count = 0
            for item in local_dir.iterdir():
                if item.is_file():
                    item.unlink()
                    file_count += 1
                    self.logger.debug(f"Gelöscht: {item.name}")
                elif item.is_dir():
                    shutil.rmtree(item)
                    file_count += 1
                    self.logger.debug(f"Verzeichnis gelöscht: {item.name}")
            
            self.logger.info(f"Lokales Cleanup abgeschlossen: {file_count} Einträge gelöscht")
            return True
        except Exception as e:
            self.logger.error(f"Fehler beim Cleanup: {e}")
            return False


def main():
    """Test-Funktion"""
    import yaml
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Config laden
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    
    # Syncer testen
    syncer = ServerSyncer(config)
    
    print("=" * 60)
    print("CD-Ripper Server Sync Test")
    print("=" * 60)
    
    # Connection-Test
    print("\n=== Testing Connection ===")
    connected = syncer.test_connection()
    print(f"Connection: {'OK' if connected else 'FAILED (ssh not installed or no access)'}")
    
    # Test Remote-Pfad-Mapping
    print("\n=== Testing Remote Path Mapping ===")
    for category in [1, 2, 3]:
        remote_path = syncer.get_remote_path(category)
        print(f"Category {category}: {remote_path}")
    
    # Test-Verzeichnis
    test_dir = "/root/projects/cd-ripper/output"
    
    # Prüfe ob Test-Dateien existieren
    if not Path(test_dir).exists() or not list(Path(test_dir).glob('*')):
        print("\n⚠️  Keine Test-Dateien gefunden in:", test_dir)
        print("Bitte zuerst Audio-Dateien zum Testen erstellen.")
        return
    
    # Zeige Test-Dateien
    print(f"\n=== Test-Dateien in {test_dir} ===")
    for file in Path(test_dir).glob('*'):
        if file.is_file():
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"  - {file.name} ({size_mb:.1f} MB)")
    
    # Test-Sync durchführen?
    print("\n=== Test-Sync vorbereitet ===")
    print("Führe echten Sync durch für Kategorie 3 (Musik)")
    print(f"Quelle: {test_dir}")
    print(f"Ziel: {syncer.user}@{syncer.server}:{syncer.get_remote_path(3)}")
    
    # Progress-Callback
    last_progress = [0]
    def progress_callback(percent):
        if percent != last_progress[0]:
            print(f"  Progress: {percent}%")
            last_progress[0] = percent
    
    # Sync ausführen
    success = syncer.sync_directory(test_dir, 3, progress_callback)
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Sync erfolgreich abgeschlossen!")
    else:
        print("❌ Sync fehlgeschlagen!")
        print("\nMögliche Ursachen:")
        print("  - Passwort in config.yaml falsch")
        print("  - Netzwerkproblem")
        print("  - Zielverzeichnis existiert nicht")
        print("  - sshpass nicht installiert")
    print("=" * 60)


if __name__ == "__main__":
    main()
