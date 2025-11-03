# Internationalization (i18n) Documentation

## Overview

The CD-Ripper web interface supports multiple languages through a simple JavaScript-based internationalization system.

## Supported Languages

- **English (en)** - Default
- **Deutsch (de)** - German

## Configuration

### Setting the Default Language

Edit `config/config.yaml`:

```yaml
web_interface:
  enabled: true
  host: "0.0.0.0"
  port: 5000
  language: "en"    # en or de
```

### Changing Language via Web Interface

1. Open Settings page (`⚙️` button)
2. Navigate to "Web Interface" section
3. Select language from dropdown
4. Click "Save & Restart"

## For Developers

### Adding New Languages

1. Edit `web/static/i18n.js`
2. Add new language object to `translations`:

```javascript
const translations = {
    en: { /* English translations */ },
    de: { /* German translations */ },
    fr: {  // New language
        'app_title': 'CD-Ripper',
        'btn_eject': 'Éjecter',
        'btn_settings': 'Paramètres',
        // ... more translations
    }
};
```

3. Update language selector in settings:

```html
<select id="web_language">
    <option value="en">English</option>
    <option value="de">Deutsch</option>
    <option value="fr">Français</option>  <!-- New option -->
</select>
```

### Using Translations in HTML

#### Static Text

Add `data-i18n` attribute:

```html
<h1 data-i18n="app_title">CD-Ripper</h1>
<button data-i18n="btn_eject">Eject</button>
```

#### HTML Content

For translations containing HTML tags, use `data-i18n-html="true"`:

```html
<div data-i18n="warning_banner" data-i18n-html="true">
    <strong>Do not remove CD!</strong> Ripping in progress...
</div>
```

#### Placeholders

For input placeholders:

```html
<input type="text" data-i18n-placeholder="label_device" placeholder="CD Device">
```

### Using Translations in JavaScript

```javascript
// Simple translation
const message = t('msg_eject_success');

// Translation with replacements
const trackInfo = t('track_of', {
    current: 5,
    total: 12
});
// Result: "Track 5 of 12" (en) or "Track 5 von 12" (de)
```

### Available Functions

#### `initLanguage()`
Initializes language from localStorage or defaults to English.

```javascript
document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
});
```

#### `setLanguage(lang)`
Changes current language and updates all UI elements.

```javascript
setLanguage('de');  // Switch to German
```

#### `t(key, replacements)`
Returns translated string for given key.

```javascript
// Simple
t('btn_eject')  // "Eject" or "Auswerfen"

// With placeholders
t('track_of', { current: 3, total: 10 })
```

## Translation Keys

### Main Interface

| Key | English | Deutsch |
|-----|---------|---------|
| `app_title` | CD-Ripper | CD-Ripper |
| `btn_eject` | Eject | Auswerfen |
| `btn_settings` | Settings | Einstellungen |
| `no_cd` | No CD inserted | Keine CD eingelegt |

### Processing Steps

| Key | English | Deutsch |
|-----|---------|---------|
| `step_detecting` | Detecting CD... | Erkenne CD... |
| `step_identifying` | Identifying... | Identifiziere... |
| `step_ripping` | Ripping | Rippe |
| `step_encoding` | Encoding | Kodiere |
| `step_tagging` | Tagging | Tagge |
| `step_syncing` | Syncing to server | Synchronisiere zum Server |
| `step_done` | Done | Fertig |

### Messages

| Key | English | Deutsch |
|-----|---------|---------|
| `msg_eject_confirm` | Really eject CD? | CD wirklich auswerfen? |
| `msg_eject_success` | CD ejected | CD ausgeworfen |
| `msg_eject_error` | Error ejecting CD | Fehler beim Auswerfen der CD |
| `msg_config_saved` | Configuration saved! | Konfiguration gespeichert! |

For a complete list of keys, see `web/static/i18n.js`.

## Persistence

- **Config file**: Stores default language for service
- **localStorage**: Browser remembers user's language choice
- **Priority**: localStorage > config.yaml > default (en)

## Best Practices

1. **Always provide English fallback** - English translations should be complete
2. **Use descriptive keys** - `btn_eject` not `button1`
3. **Keep translations consistent** - Same terminology throughout
4. **Test both languages** - Ensure UI doesn't break with longer translations
5. **Document new keys** - Add to this file when adding translations

## Testing

### Manual Testing

1. Change language in settings
2. Verify all text updates correctly
3. Check responsiveness with longer translations
4. Test all buttons and messages

### Browser Console

```javascript
// Check current language
console.log(currentLanguage);

// List all translations
console.log(translations);

// Test specific translation
console.log(t('btn_eject'));

// Switch language
setLanguage('de');
```

## Troubleshooting

### Translations not updating

1. Check browser console for JavaScript errors
2. Verify `i18n.js` is loaded before `app.js`
3. Clear browser cache
4. Check `data-i18n` attributes are correct

### New language not appearing

1. Ensure language code added to `translations` object
2. Add option to language selector in settings
3. Restart service after config change

### Mixed languages

1. Clear localStorage: `localStorage.clear()`
2. Reload page
3. Set language in settings

## Future Enhancements

- [ ] Add more languages (French, Spanish, etc.)
- [ ] Backend translation for log messages
- [ ] Date/time localization
- [ ] Number formatting (1,234.56 vs 1.234,56)
- [ ] Translation management UI
- [ ] Export/import translation files
