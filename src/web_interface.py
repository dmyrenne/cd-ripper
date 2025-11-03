#!/usr/bin/env python3
"""
CD-Ripper Web Interface
Status-Anzeige und Konfigurations-Editor
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
import yaml
import logging
import os
from pathlib import Path
from typing import Dict, Any, Optional
import threading
import time
from datetime import datetime

app = Flask(__name__, 
            template_folder='../web/templates',
            static_folder='../web/static')
CORS(app)

# Globaler Status
class ServiceStatus:
    def __init__(self):
        self.current_cd = None
        self.processing = False
        self.current_step = None
        self.progress = 0
        self.total_tracks = 0
        self.current_track = 0
        self.last_update = None
        self.logs = []
        self.max_logs = 100
        
    def update_cd(self, cd_info):
        self.current_cd = cd_info
        self.last_update = datetime.now()
        
    def update_progress(self, step, progress, current_track=None, total_tracks=None):
        self.current_step = step
        self.progress = progress
        if current_track is not None:
            self.current_track = current_track
        if total_tracks is not None:
            self.total_tracks = total_tracks
        self.last_update = datetime.now()
        
    def add_log(self, level, message):
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'level': level,
            'message': message
        }
        self.logs.insert(0, log_entry)
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[:self.max_logs]
    
    def reset(self):
        self.current_cd = None
        self.processing = False
        self.current_step = None
        self.progress = 0
        self.current_track = 0
        self.total_tracks = 0
        self.last_update = datetime.now()

status = ServiceStatus()

# Konfigurationspfad
CONFIG_PATH = Path(__file__).parent.parent / "config" / "config.yaml"
LOG_FILE = Path(__file__).parent.parent / "logs" / "ripper.log"


@app.route('/')
def index():
    """Hauptseite"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """API: Aktueller Service-Status"""
    return jsonify({
        'current_cd': status.current_cd,
        'processing': status.processing,
        'current_step': status.current_step,
        'progress': status.progress,
        'current_track': status.current_track,
        'total_tracks': status.total_tracks,
        'last_update': status.last_update.isoformat() if status.last_update else None
    })


@app.route('/api/logs')
def get_logs():
    """API: Letzte Log-Einträge"""
    limit = request.args.get('limit', 50, type=int)
    return jsonify({
        'logs': status.logs[:limit]
    })


@app.route('/api/logs/tail')
def get_logs_tail():
    """API: Letzte Zeilen aus Log-Datei"""
    lines = request.args.get('lines', 50, type=int)
    
    if not LOG_FILE.exists():
        return jsonify({'logs': []})
    
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            all_lines = f.readlines()
            tail_lines = all_lines[-lines:]
            
            logs = []
            for line in tail_lines:
                # Parse Log-Zeile: 2025-11-03 00:15:52 - cd_ripper - INFO - Message
                parts = line.split(' - ', 3)
                if len(parts) >= 4:
                    logs.append({
                        'timestamp': parts[0].strip(),
                        'logger': parts[1].strip(),
                        'level': parts[2].strip(),
                        'message': parts[3].strip()
                    })
                else:
                    logs.append({
                        'timestamp': '',
                        'logger': '',
                        'level': 'INFO',
                        'message': line.strip()
                    })
            
            return jsonify({'logs': logs})
    except Exception as e:
        return jsonify({'error': str(e), 'logs': []}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """API: Aktuelle Konfiguration abrufen"""
    try:
        with open(CONFIG_PATH, 'r') as f:
            config = yaml.safe_load(f)
        return jsonify(config)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['POST'])
def update_config():
    """API: Konfiguration aktualisieren"""
    try:
        new_config = request.json
        
        # Backup erstellen
        backup_path = CONFIG_PATH.with_suffix('.yaml.backup')
        with open(CONFIG_PATH, 'r') as f:
            backup_content = f.read()
        with open(backup_path, 'w') as f:
            f.write(backup_content)
        
        # Neue Config speichern
        with open(CONFIG_PATH, 'w') as f:
            yaml.dump(new_config, f, default_flow_style=False, allow_unicode=True)
        
        status.add_log('INFO', 'Konfiguration aktualisiert')
        return jsonify({'success': True, 'message': 'Konfiguration gespeichert'})
    except Exception as e:
        status.add_log('ERROR', f'Fehler beim Speichern der Konfiguration: {e}')
        return jsonify({'error': str(e)}), 500


@app.route('/api/eject', methods=['POST'])
def eject_cd():
    """API: CD manuell auswerfen"""
    try:
        from cd_detector import CDDetector
        detector = CDDetector()
        success = detector.eject_cd()
        
        if success:
            status.reset()
            status.add_log('INFO', 'CD manuell ausgeworfen')
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'CD konnte nicht ausgeworfen werden'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Log-Datei-Watcher (für Echtzeit-Updates)
class LogWatcher(threading.Thread):
    def __init__(self, log_file):
        super().__init__(daemon=True)
        self.log_file = log_file
        self.running = True
        
    def run(self):
        """Überwacht Log-Datei für neue Einträge"""
        if not self.log_file.exists():
            return
            
        with open(self.log_file, 'r') as f:
            # Springe ans Ende
            f.seek(0, 2)
            
            while self.running:
                line = f.readline()
                if line:
                    # Parse und zu Status hinzufügen
                    parts = line.split(' - ', 3)
                    if len(parts) >= 4:
                        level = parts[2].strip()
                        message = parts[3].strip()
                        status.add_log(level, message)
                        
                        # Extrahiere Status-Informationen
                        if 'CD identifiziert:' in message:
                            # Extrahiere CD-Info
                            cd_name = message.split('CD identifiziert:')[1].strip()
                            status.update_cd({'name': cd_name})
                            status.processing = True
                        elif 'Starte CD-Verarbeitung' in message:
                            status.processing = True
                        elif 'CD-Verarbeitung erfolgreich abgeschlossen' in message:
                            status.processing = False
                            status.progress = 100
                        elif 'CD-Verarbeitung fehlgeschlagen' in message:
                            status.processing = False
                        elif 'Rippe Track' in message:
                            # Extrahiere Track-Info: "Rippe Track 1/8: Name"
                            if '/' in message:
                                parts = message.split('/')
                                if len(parts) >= 2:
                                    current = parts[0].split()[-1]
                                    total = parts[1].split(':')[0].strip()
                                    try:
                                        status.current_track = int(current)
                                        status.total_tracks = int(total)
                                        status.current_step = 'ripping'
                                        status.progress = int((status.current_track / status.total_tracks) * 100)
                                    except:
                                        pass
                        elif 'Encodiere Track' in message:
                            status.current_step = 'encoding'
                        elif 'Tagge Track' in message:
                            status.current_step = 'tagging'
                        elif 'Sync Progress:' in message:
                            status.current_step = 'syncing'
                            try:
                                percent = message.split('Sync Progress:')[1].strip().rstrip('%')
                                status.progress = int(percent)
                            except:
                                pass
                else:
                    time.sleep(0.5)


def start_web_interface(host='0.0.0.0', port=5000):
    """Startet das Web-Interface"""
    # Log-Watcher starten
    watcher = LogWatcher(LOG_FILE)
    watcher.start()
    
    # Flask-App starten
    app.run(host=host, port=port, debug=False, threaded=True)


if __name__ == '__main__':
    start_web_interface()
