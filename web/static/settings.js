// CD-Ripper Settings JavaScript

let currentConfig = null;

// Load configuration on page load
document.addEventListener('DOMContentLoaded', () => {
    loadConfig();
});

async function loadConfig() {
    try {
        const response = await fetch('/api/config');
        if (!response.ok) throw new Error('Fehler beim Laden der Konfiguration');
        
        currentConfig = await response.json();
        populateForm(currentConfig);
    } catch (error) {
        console.error('Error loading config:', error);
        showAlert('Fehler beim Laden der Konfiguration: ' + error.message, 'error');
    }
}

function populateForm(config) {
    // Ripper
    document.getElementById('device').value = config.ripper?.device || '/dev/sr0';
    document.getElementById('quality').value = config.ripper?.quality || 'paranoia';
    
    // Encoder - Category 1+2
    const cat12 = config.encoder?.profiles?.category_1_2 || {};
    document.getElementById('cat12_format').value = cat12.format || 'mp3';
    document.getElementById('cat12_bitrate').value = cat12.bitrate || 320;
    
    // Encoder - Category 3
    const cat3 = config.encoder?.profiles?.category_3 || {};
    document.getElementById('cat3_format').value = cat3.format || 'flac';
    document.getElementById('cat3_compression').value = cat3.compression_level || 8;
    
    // Output
    document.getElementById('local_path').value = config.output?.local_path || '/mnt/dietpi_userdata/rips';
    
    // Sync
    const sync = config.sync || {};
    document.getElementById('sync_enabled').checked = sync.enabled !== false;
    document.getElementById('sync_host').value = sync.host || '';
    document.getElementById('sync_user').value = sync.user || '';
    document.getElementById('sync_password').value = sync.password || '';
    
    // Remote paths
    const remotePaths = sync.remote_paths || {};
    document.getElementById('remote_cat1').value = remotePaths.category_1 || '';
    document.getElementById('remote_cat2').value = remotePaths.category_2 || '';
    document.getElementById('remote_cat3').value = remotePaths.category_3 || '';
    
    document.getElementById('cleanup').checked = sync.cleanup !== false;
    document.getElementById('auto_eject').checked = sync.auto_eject !== false;
    
    // Logging
    const logging = config.logging || {};
    document.getElementById('log_level').value = logging.level || 'INFO';
    document.getElementById('log_file').value = logging.file || '/root/projects/cd-ripper/logs/ripper.log';
}

function buildConfigFromForm() {
    const config = {
        ripper: {
            device: document.getElementById('device').value,
            quality: document.getElementById('quality').value
        },
        encoder: {
            profiles: {
                category_1_2: {
                    format: document.getElementById('cat12_format').value,
                    bitrate: parseInt(document.getElementById('cat12_bitrate').value) || 320
                },
                category_3: {
                    format: document.getElementById('cat3_format').value,
                    compression_level: parseInt(document.getElementById('cat3_compression').value) || 8
                }
            }
        },
        output: {
            local_path: document.getElementById('local_path').value
        },
        sync: {
            enabled: document.getElementById('sync_enabled').checked,
            host: document.getElementById('sync_host').value,
            user: document.getElementById('sync_user').value,
            password: document.getElementById('sync_password').value,
            remote_paths: {
                category_1: document.getElementById('remote_cat1').value,
                category_2: document.getElementById('remote_cat2').value,
                category_3: document.getElementById('remote_cat3').value
            },
            cleanup: document.getElementById('cleanup').checked,
            auto_eject: document.getElementById('auto_eject').checked
        },
        logging: {
            level: document.getElementById('log_level').value,
            file: document.getElementById('log_file').value,
            format: currentConfig?.logging?.format || '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        web_interface: currentConfig?.web_interface || {
            host: '0.0.0.0',
            port: 5000
        }
    };
    
    return config;
}

async function saveConfig() {
    try {
        const config = buildConfigFromForm();
        
        const response = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Fehler beim Speichern');
        }
        
        const result = await response.json();
        showAlert('✅ ' + result.message, 'success');
        
        // Config neu laden
        setTimeout(() => loadConfig(), 1000);
        
    } catch (error) {
        console.error('Error saving config:', error);
        showAlert('❌ Fehler beim Speichern: ' + error.message, 'error');
    }
}

async function saveAndRestart() {
    if (!confirm('Service wird neu gestartet. Läuft gerade ein Ripping-Vorgang?')) {
        return;
    }
    
    try {
        // Erst Config speichern
        const config = buildConfigFromForm();
        
        const saveResponse = await fetch('/api/config', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(config)
        });
        
        if (!saveResponse.ok) {
            const error = await saveResponse.json();
            throw new Error(error.error || 'Fehler beim Speichern');
        }
        
        showAlert('✅ Konfiguration gespeichert. Service wird neu gestartet...', 'warning');
        
        // Dann Service neu starten
        setTimeout(async () => {
            try {
                const restartResponse = await fetch('/api/restart', {
                    method: 'POST'
                });
                
                if (restartResponse.ok) {
                    showAlert('✅ Service wird neu gestartet. Bitte warten...', 'success');
                    
                    // Zurück zur Hauptseite nach 3 Sekunden
                    setTimeout(() => {
                        window.location.href = '/';
                    }, 3000);
                } else {
                    const error = await restartResponse.json();
                    showAlert('⚠️ Service-Neustart fehlgeschlagen: ' + error.error, 'error');
                }
            } catch (error) {
                showAlert('⚠️ Service-Neustart fehlgeschlagen: ' + error.message, 'error');
            }
        }, 1000);
        
    } catch (error) {
        console.error('Error:', error);
        showAlert('❌ Fehler: ' + error.message, 'error');
    }
}

function showAlert(message, type) {
    const container = document.getElementById('alertContainer');
    
    const alertClass = type === 'success' ? 'alert-success' : 
                      type === 'error' ? 'alert-error' : 
                      'alert-warning';
    
    const alert = document.createElement('div');
    alert.className = `alert ${alertClass}`;
    alert.textContent = message;
    
    container.innerHTML = '';
    container.appendChild(alert);
    
    // Auto-hide nach 5 Sekunden
    setTimeout(() => {
        alert.style.transition = 'opacity 0.5s';
        alert.style.opacity = '0';
        setTimeout(() => alert.remove(), 500);
    }, 5000);
}
