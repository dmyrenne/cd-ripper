// CD-Ripper Web Interface JavaScript

let currentConfig = null;
let autoScroll = true;
let logsExpanded = false;

// Initialize i18n on page load
document.addEventListener('DOMContentLoaded', async () => {
    // Load language from config
    try {
        const response = await fetch('/api/config');
        const config = await response.json();
        const lang = config?.web_interface?.language || 'en';
        initLanguage();
        setLanguage(lang);
    } catch (error) {
        console.error('Error loading config:', error);
        initLanguage();
        setLanguage('en'); // fallback
    }
    
    // Start status polling
    fetchStatus();
    fetchLogs();
    setInterval(fetchStatus, 2000);
    setInterval(fetchLogs, 3000);
});

// API Calls
async function fetchStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        updateStatus(data);
    } catch (error) {
        console.error('Error loading status:', error);
    }
}

async function fetchLogs() {
    try {
        const response = await fetch('/api/logs/tail?lines=100');
        const data = await response.json();
        updateLogs(data.logs);
    } catch (error) {
        console.error('Error loading logs:', error);
    }
}

async function ejectCD() {
    if (!confirm(t('msg_eject_confirm') || 'Really eject CD?')) return;
    
    try {
        const response = await fetch('/api/eject', { method: 'POST' });
        if (response.ok) {
            alert(t('msg_eject_success'));
        } else {
            alert(t('msg_eject_error'));
        }
    } catch (error) {
        console.error('Error:', error);
        alert(t('msg_eject_error'));
    }
}

// UI Updates
function updateStatus(data) {
    const albumTitle = document.getElementById('albumTitle');
    const albumArtist = document.getElementById('albumArtist');
    const coverPlaceholder = document.getElementById('coverPlaceholder');
    const coverImage = document.getElementById('coverImage');
    const progressSection = document.getElementById('progressSection');
    const warningBanner = document.getElementById('warningBanner');
    
    if (data.current_cd && data.processing) {
        // CD aktiv und wird verarbeitet
        const cdName = data.current_cd.name || 'Unbekannte CD';
        const artist = data.current_cd.artist || '';
        const coverUrl = data.current_cd.cover_url || '';
        
        albumTitle.textContent = cdName;
        albumArtist.textContent = artist;
        albumArtist.style.color = '';
        
        // Album Cover aktualisieren
        if (coverUrl) {
            coverImage.src = coverUrl;
            coverImage.style.display = 'block';
            coverPlaceholder.style.display = 'none';
        } else {
            coverImage.style.display = 'none';
            coverPlaceholder.style.display = 'flex';
        }
        
        // Warnung anzeigen
        warningBanner.style.display = 'flex';
        
        // Progress anzeigen
        progressSection.style.display = 'block';
        document.getElementById('stepName').textContent = getStepName(data.current_step);
        
        let trackInfo = '';
        if (data.current_track && data.total_tracks) {
            trackInfo = `Track ${data.current_track} von ${data.total_tracks}`;
        }
        document.getElementById('trackInfo').textContent = trackInfo;
        
        const progress = data.progress || 0;
        document.getElementById('progressFill').style.width = progress + '%';
        document.getElementById('progressText').textContent = progress + '%';
        
    } else if (data.current_cd) {
        // CD eingelegt aber nicht in Verarbeitung
        const cdName = data.current_cd.name || 'CD erkannt';
        const artist = data.current_cd.artist || '';
        const coverUrl = data.current_cd.cover_url || '';
        
        albumTitle.textContent = cdName;
        albumArtist.textContent = artist;
        albumArtist.style.color = 'var(--success-color)';
        
        if (coverUrl) {
            coverImage.src = coverUrl;
            coverImage.style.display = 'block';
            coverPlaceholder.style.display = 'none';
        } else {
            coverImage.style.display = 'none';
            coverPlaceholder.style.display = 'flex';
        }
        
        warningBanner.style.display = 'none';
        progressSection.style.display = 'none';
        
    } else {
        // Keine CD
        albumTitle.textContent = 'Keine CD eingelegt';
        albumArtist.textContent = '';
        
        coverImage.style.display = 'none';
        coverPlaceholder.style.display = 'flex';
        
        warningBanner.style.display = 'none';
        progressSection.style.display = 'none';
    }
}

function updateLogs(logs) {
    const container = document.getElementById('logContainer');
    
    if (!logs || logs.length === 0) {
        container.innerHTML = '<div class="log-placeholder">Keine Logs verfügbar</div>';
        return;
    }
    
    const shouldScroll = autoScroll && (container.scrollTop + container.clientHeight >= container.scrollHeight - 20);
    
    container.innerHTML = logs.map(log => {
        const level = log.level || 'INFO';
        const levelClass = level.includes('✅') || level.includes('✓') ? 'SUCCESS' : level;
        
        return `
            <div class="log-entry">
                <span class="log-timestamp">${log.timestamp.split(' ')[1] || log.timestamp}</span>
                <span class="log-level ${levelClass}">${level}</span>
                <span class="log-message">${escapeHtml(log.message)}</span>
            </div>
        `;
    }).join('');
    
    if (shouldScroll) {
        container.scrollTop = container.scrollHeight;
    }
}

function getStepName(step) {
    const steps = {
        'ripping': '🎵 Rippe CD',
        'encoding': '🔄 Encodiere Audio',
        'tagging': '🏷️ Schreibe Metadaten',
        'syncing': '☁️ Synchronisiere',
        null: 'Warte...'
    };
    return steps[step] || 'Verarbeite...';
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Log Toggle
function toggleLogs() {
    logsExpanded = !logsExpanded;
    const logContent = document.getElementById('logContent');
    const toggleBtn = document.getElementById('toggleLogs');
    
    if (logsExpanded) {
        logContent.classList.remove('collapsed');
        toggleBtn.textContent = '▼';
        toggleBtn.classList.remove('rotated');
    } else {
        logContent.classList.add('collapsed');
        toggleBtn.textContent = '▶';
        toggleBtn.classList.add('rotated');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Initial load
    fetchStatus();
    fetchLogs();
    
    // Auto-refresh
    setInterval(fetchStatus, 2000);
    setInterval(fetchLogs, 3000);
    
    // Buttons
    document.getElementById('ejectBtn').addEventListener('click', ejectCD);
    document.getElementById('configBtn').addEventListener('click', () => {
        window.location.href = '/settings';
    });
    
    // Log Toggle
    document.getElementById('logHeader').addEventListener('click', toggleLogs);
    document.getElementById('toggleLogs').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleLogs();
    });
    
    // Auto-scroll checkbox
    document.getElementById('autoScroll').addEventListener('change', (e) => {
        autoScroll = e.target.checked;
    });
    
    // Clear logs
    document.getElementById('clearLogs').addEventListener('click', () => {
        document.getElementById('logContainer').innerHTML = '<div class="log-placeholder">Logs gelöscht</div>';
    });
});
