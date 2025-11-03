// Internationalization (i18n) for CD-Ripper Web Interface

const translations = {
    en: {
        // Header
        'app_title': 'CD-Ripper',
        'btn_eject': 'Eject',
        'btn_settings': 'Settings',
        
        // Status
        'no_cd': 'No CD inserted',
        'warning_banner': '<strong>Do not remove CD!</strong> Ripping in progress...',
        'waiting': 'Waiting...',
        
        // Steps
        'step_detecting': 'Detecting CD...',
        'step_identifying': 'Identifying...',
        'step_ripping': 'Ripping',
        'step_encoding': 'Encoding',
        'step_tagging': 'Tagging',
        'step_syncing': 'Syncing to server',
        'step_done': 'Done',
        
        // Track info
        'track_of': 'Track {current} of {total}',
        
        // Logs
        'logs_title': 'Live Logs',
        'logs_empty': 'No logs available yet...',
        
        // Settings Page
        'settings_title': 'Settings',
        'settings_save': 'Save',
        'settings_save_restart': 'Save & Restart',
        'settings_back': 'Back to Status',
        
        // Settings Tabs
        'tab_ripper': 'Ripper Settings',
        'tab_encoder': 'Encoder Settings',
        'tab_sync': 'Sync Settings',
        'tab_output': 'Output Settings',
        'tab_web': 'Web Interface',
        'tab_logging': 'Logging',
        
        // Settings Labels
        'label_device': 'CD Device',
        'label_quality': 'Ripping Quality',
        'label_language': 'Language',
        'label_host': 'Server Host',
        'label_user': 'SSH User',
        'label_password': 'SSH Password',
        'label_enabled': 'Enabled',
        'label_port': 'Port',
        
        // Messages
        'msg_config_saved': 'Configuration saved successfully!',
        'msg_config_error': 'Error saving configuration',
        'msg_restart_pending': 'Service will restart...',
        'msg_eject_confirm': 'Really eject CD?',
        'msg_eject_success': 'CD ejected',
        'msg_eject_error': 'Error ejecting CD',
    },
    
    de: {
        // Header
        'app_title': 'CD-Ripper',
        'btn_eject': 'Auswerfen',
        'btn_settings': 'Einstellungen',
        
        // Status
        'no_cd': 'Keine CD eingelegt',
        'warning_banner': '<strong>CD nicht entfernen!</strong> Ripping läuft...',
        'waiting': 'Warte...',
        
        // Steps
        'step_detecting': 'Erkenne CD...',
        'step_identifying': 'Identifiziere...',
        'step_ripping': 'Rippe',
        'step_encoding': 'Kodiere',
        'step_tagging': 'Tagge',
        'step_syncing': 'Synchronisiere zum Server',
        'step_done': 'Fertig',
        
        // Track info
        'track_of': 'Track {current} von {total}',
        
        // Logs
        'logs_title': 'Live-Logs',
        'logs_empty': 'Noch keine Logs verfügbar...',
        
        // Settings Page
        'settings_title': 'Einstellungen',
        'settings_save': 'Speichern',
        'settings_save_restart': 'Speichern & Neu starten',
        'settings_back': 'Zurück zum Status',
        
        // Settings Tabs
        'tab_ripper': 'Ripper-Einstellungen',
        'tab_encoder': 'Encoder-Einstellungen',
        'tab_sync': 'Sync-Einstellungen',
        'tab_output': 'Output-Einstellungen',
        'tab_web': 'Web-Interface',
        'tab_logging': 'Logging',
        
        // Settings Labels
        'label_device': 'CD-Laufwerk',
        'label_quality': 'Ripping-Qualität',
        'label_language': 'Sprache',
        'label_host': 'Server-Host',
        'label_user': 'SSH-Benutzer',
        'label_password': 'SSH-Passwort',
        'label_enabled': 'Aktiviert',
        'label_port': 'Port',
        
        // Messages
        'msg_config_saved': 'Konfiguration erfolgreich gespeichert!',
        'msg_config_error': 'Fehler beim Speichern der Konfiguration',
        'msg_restart_pending': 'Service wird neu gestartet...',
        'msg_eject_confirm': 'CD wirklich auswerfen?',
        'msg_eject_success': 'CD ausgeworfen',
        'msg_eject_error': 'Fehler beim Auswerfen der CD',
    }
};

// Current language (default: English)
let currentLanguage = 'en';

// Initialize language from localStorage or config
function initLanguage() {
    const saved = localStorage.getItem('cd-ripper-language');
    if (saved && translations[saved]) {
        currentLanguage = saved;
    }
    return currentLanguage;
}

// Get translation for key
function t(key, replacements = {}) {
    let text = translations[currentLanguage][key] || translations['en'][key] || key;
    
    // Replace placeholders like {current}, {total}
    Object.keys(replacements).forEach(placeholder => {
        text = text.replace(`{${placeholder}}`, replacements[placeholder]);
    });
    
    return text;
}

// Set language and update UI
function setLanguage(lang) {
    if (!translations[lang]) {
        console.error(`Language '${lang}' not available`);
        return;
    }
    
    currentLanguage = lang;
    localStorage.setItem('cd-ripper-language', lang);
    
    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        const isHtml = element.getAttribute('data-i18n-html') === 'true';
        
        if (isHtml) {
            element.innerHTML = t(key);
        } else {
            element.textContent = t(key);
        }
    });
    
    // Update placeholders
    document.querySelectorAll('[data-i18n-placeholder]').forEach(element => {
        const key = element.getAttribute('data-i18n-placeholder');
        element.placeholder = t(key);
    });
    
    // Update title
    document.title = t('app_title') + ' - Status';
    
    console.log(`Language changed to: ${lang}`);
}

// Export functions
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { initLanguage, setLanguage, t, translations };
}
