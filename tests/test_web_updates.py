#!/usr/bin/env python3
"""
Test-Script für Web-Interface Updates
Simuliert verschiedene CDs und deren Verarbeitung
"""

import time
import random
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from shared_status import SharedStatus
from PIL import Image, ImageDraw, ImageFont
import io

# Test-CDs mit unterschiedlichen Daten
TEST_CDS = [
    {
        'name': 'The Dark Side of the Moon',
        'artist': 'Pink Floyd',
        'tracks': 10,
        'color': '#1a1a1a'  # Schwarz
    },
    {
        'name': 'Abbey Road',
        'artist': 'The Beatles',
        'tracks': 17,
        'color': '#4a90e2'  # Blau
    },
    {
        'name': 'Thriller',
        'artist': 'Michael Jackson',
        'tracks': 9,
        'color': '#e74c3c'  # Rot
    },
    {
        'name': 'Back in Black',
        'artist': 'AC/DC',
        'tracks': 10,
        'color': '#2c3e50'  # Dunkelgrau
    },
    {
        'name': 'Rumours',
        'artist': 'Fleetwood Mac',
        'tracks': 11,
        'color': '#8e44ad'  # Lila
    }
]


def generate_test_cover(album_name: str, artist_name: str, color: str) -> bytes:
    """
    Generiert ein einfaches Test-Cover als Bilddaten
    """
    # 500x500 Cover erstellen
    img = Image.new('RGB', (500, 500), color=color)
    draw = ImageDraw.Draw(img)
    
    # Versuche eine Schriftart zu laden, sonst Default
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 30)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Weißer Rahmen
    draw.rectangle([20, 20, 480, 480], outline='white', width=5)
    
    # Text zentrieren
    # Album-Name
    bbox = draw.textbbox((0, 0), album_name, font=font_large)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (500 - text_width) / 2
    y = 200
    
    # Mehrzeiliger Text für lange Album-Namen
    words = album_name.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        bbox = draw.textbbox((0, 0), test_line, font=font_large)
        if bbox[2] - bbox[0] > 460:  # Max Breite
            if current_line:
                lines.append(current_line)
            current_line = word
        else:
            current_line = test_line
    
    if current_line:
        lines.append(current_line)
    
    # Album-Name zeichnen
    y = 180
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        x = (500 - text_width) / 2
        draw.text((x, y), line, fill='white', font=font_large)
        y += 50
    
    # Künstler-Name
    bbox = draw.textbbox((0, 0), artist_name, font=font_small)
    text_width = bbox[2] - bbox[0]
    x = (500 - text_width) / 2
    y = y + 20
    draw.text((x, y), artist_name, fill='lightgray', font=font_small)
    
    # CD-Icon
    draw.ellipse([220, 80, 280, 140], outline='white', width=3)
    draw.ellipse([240, 100, 260, 120], outline='white', width=2)
    
    # Als Bytes speichern
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85)
    return buffer.getvalue()


def simulate_cd_processing(cd_data: dict, shared_status: SharedStatus):
    """
    Simuliert die Verarbeitung einer CD mit allen Phasen
    """
    print(f"\n{'='*60}")
    print(f"🎵 Simuliere: {cd_data['artist']} - {cd_data['name']}")
    print(f"{'='*60}\n")
    
    # 1. CD erkannt - Cover generieren und Status aktualisieren
    print("📀 CD wird erkannt...")
    print("🎨 Generiere Test-Cover...")
    
    cover_data = generate_test_cover(
        cd_data['name'],
        cd_data['artist'],
        cd_data['color']
    )
    
    cover_path = shared_status.save_cover(cover_data, "/tmp")
    print(f"✅ Cover gespeichert: {cover_path}")
    
    shared_status.update_cd(
        name=cd_data['name'],
        artist=cd_data['artist'],
        cover_path=cover_path
    )
    shared_status.set_processing(True)
    time.sleep(2)
    
    # 2. Ripping-Phase
    print("🎧 Ripping startet...")
    total_tracks = cd_data['tracks']
    
    for track in range(1, total_tracks + 1):
        # Simuliere Ripping-Dauer (1-3 Sekunden pro Track)
        rip_time = random.uniform(1.0, 3.0)
        
        # Start Track
        progress = int((track - 1) / total_tracks * 100)
        shared_status.update_progress('ripping', progress, track, total_tracks)
        print(f"  🔵 Rippe Track {track}/{total_tracks} ({progress}%)")
        
        time.sleep(rip_time / 2)  # Erste Hälfte
        
        # Track fertig
        progress = int(track / total_tracks * 100)
        shared_status.update_progress('ripping', progress, track, total_tracks)
        print(f"  ✅ Track {track}/{total_tracks} fertig ({progress}%)")
        
        time.sleep(rip_time / 2)  # Zweite Hälfte
    
    time.sleep(1)
    
    # 3. Encoding-Phase
    print("🔄 Encoding startet...")
    for track in range(1, total_tracks + 1):
        encode_time = random.uniform(0.5, 1.5)
        
        progress = int((track - 1) / total_tracks * 100)
        shared_status.update_progress('encoding', progress, track, total_tracks)
        print(f"  🔵 Encodiere Track {track}/{total_tracks} ({progress}%)")
        
        time.sleep(encode_time / 2)
        
        progress = int(track / total_tracks * 100)
        shared_status.update_progress('encoding', progress, track, total_tracks)
        print(f"  ✅ Track {track}/{total_tracks} encodiert ({progress}%)")
        
        time.sleep(encode_time / 2)
    
    time.sleep(1)
    
    # 4. Tagging-Phase
    print("🏷️  Tagging startet...")
    for track in range(1, total_tracks + 1):
        tag_time = random.uniform(0.2, 0.5)
        
        progress = int(track / total_tracks * 100)
        shared_status.update_progress('tagging', progress, track, total_tracks)
        print(f"  🏷️  Tagge Track {track}/{total_tracks} ({progress}%)")
        
        time.sleep(tag_time)
    
    time.sleep(1)
    
    # 5. Sync-Phase
    print("📤 Server-Sync startet...")
    for sync_progress in range(0, 101, 10):
        shared_status.update_progress('syncing', sync_progress, 0, 0)
        print(f"  📤 Sync-Fortschritt: {sync_progress}%")
        time.sleep(0.3)
    
    time.sleep(1)
    
    # 6. Fertig
    print("✅ CD-Verarbeitung abgeschlossen!")
    shared_status.update_progress('complete', 100, 0, 0)
    shared_status.set_processing(False)
    
    time.sleep(3)
    
    # 7. CD entfernt
    print("💿 CD wird entfernt...")
    shared_status.reset()
    time.sleep(2)


def main():
    """
    Hauptfunktion - läuft durch alle Test-CDs
    """
    print("\n" + "="*60)
    print("🧪 CD-Ripper Web-Interface Test")
    print("="*60)
    print("\n⚠️  Dieser Test simuliert verschiedene CDs mit allen Phasen")
    print("⚠️  Öffnen Sie http://localhost:5000 im Browser")
    print("⚠️  Web-Interface muss separat gestartet sein!")
    print("\nDrücken Sie ENTER um zu starten...")
    input()
    
    shared_status = SharedStatus()
    
    # Initiale Wartezeit
    print("\n⏳ Starte in 3 Sekunden...\n")
    time.sleep(3)
    
    try:
        # Durchlaufe alle Test-CDs
        for i, cd_data in enumerate(TEST_CDS, 1):
            print(f"\n📀 Test-CD {i}/{len(TEST_CDS)}")
            simulate_cd_processing(cd_data, shared_status)
            
            if i < len(TEST_CDS):
                print(f"\n⏸️  Pause 5 Sekunden bis zur nächsten CD...\n")
                time.sleep(5)
        
        print("\n" + "="*60)
        print("✅ Alle Test-CDs erfolgreich durchlaufen!")
        print("="*60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Test abgebrochen durch Benutzer")
        shared_status.reset()


if __name__ == '__main__':
    main()
