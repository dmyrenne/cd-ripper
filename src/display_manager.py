#!/usr/bin/env python3
"""
ST7789 Display Module für CD-Ripper - Neue vereinfachte Version
Basiert auf: https://learn.adafruit.com/2-0-inch-320-x-240-color-ips-tft-display/python-usage
"""

import logging
import requests
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont
import os

logger = logging.getLogger('cd_ripper.display')

class DisplayManager:
    """Verwaltet das ST7789 Display (2.0" 240x320)"""
    
    def __init__(self, config):
        """
        Initialisiert das Display
        
        Args:
            config: Komplette Config oder nur Display-Sektion aus config.yaml
        """
        # Falls die komplette Config übergeben wurde, extrahiere display-Sektion
        if 'display' in config:
            self.config = config['display']
        else:
            self.config = config
        
        self.enabled = self.config.get('enabled', False)
        self.rotation = self.config.get('rotation', 0)
        
        self.display = None
        
        if self.enabled:
            try:
                self._init_display()
                logger.info("Display erfolgreich initialisiert")
            except Exception as e:
                logger.error(f"Display-Initialisierung fehlgeschlagen: {e}")
                self.enabled = False
    
    def _init_display(self):
        """Initialisiert die ST7789 Hardware"""
        try:
            import board
            import digitalio
            from adafruit_rgb_display import st7789
            
            # Pins konfigurieren (Adafruit Standard)
            cs_pin = digitalio.DigitalInOut(board.CE0)
            dc_pin = digitalio.DigitalInOut(board.D25)
            reset_pin = digitalio.DigitalInOut(board.D24)
            
            # SPI Bus
            spi = board.SPI()
            
            # Display erstellen (2.0" ST7789)
            self.display = st7789.ST7789(
                spi,
                cs=cs_pin,
                dc=dc_pin,
                rst=reset_pin,
                rotation=self.rotation,
                baudrate=24000000
            )
            
            # Bildgröße basierend auf Rotation
            if self.display.rotation % 180 == 90:
                # Landscape
                self.width = self.display.height
                self.height = self.display.width
            else:
                # Portrait
                self.width = self.display.width
                self.height = self.display.height
            
            logger.info(f"Display: {self.width}x{self.height}, Rotation: {self.rotation}°")
            
            # Zeige initialen schwarzen Screen
            self._show_black_screen()
            
        except ImportError as e:
            logger.error(f"Adafruit Bibliothek nicht installiert: {e}")
            raise
        except Exception as e:
            logger.error(f"Hardware-Fehler: {e}")
            raise
    
    def _show_black_screen(self):
        """Zeigt einen schwarzen Screen"""
        if not self.display:
            return
        img = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
        self.display.image(img)
    
    def show_idle(self):
        """
        SCHRITT 1: Zeigt statischen Screen mit CD-Icon und Text
        """
        if not self.enabled or not self.display:
            return
        
        try:
            # Dunkler, eleganter Hintergrund (sehr dunkles Blau-Grau)
            img = Image.new('RGB', (self.width, self.height), color=(18, 22, 32))
            draw = ImageDraw.Draw(img)
            
            # Fonts laden
            try:
                font_main = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
                font_sub = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font_main = ImageFont.load_default()
                font_sub = ImageFont.load_default()
            
            # CD-Icon zeichnen (größer, zentriert oben)
            center_x = self.width // 2
            icon_y = 80
            icon_size = 80
            
            # Äußerer Kreis (CD-Rand) - helles Grau/Blau
            draw.ellipse(
                [center_x - icon_size//2, icon_y - icon_size//2, 
                 center_x + icon_size//2, icon_y + icon_size//2],
                outline=(100, 120, 180), width=3
            )
            
            # Innerer Kreis (CD-Loch) - gefüllt
            inner_size = 20
            draw.ellipse(
                [center_x - inner_size//2, icon_y - inner_size//2,
                 center_x + inner_size//2, icon_y + inner_size//2],
                fill=(100, 120, 180), outline=(100, 120, 180), width=2
            )
            
            # Reflektions-Arcs (CD-Glanz-Effekt)
            arc_width = 2
            draw.arc(
                [center_x - icon_size//2 + 10, icon_y - icon_size//2 + 10,
                 center_x + icon_size//2 - 10, icon_y + icon_size//2 - 10],
                start=45, end=135, fill=(140, 160, 220), width=arc_width
            )
            draw.arc(
                [center_x - icon_size//2 + 10, icon_y - icon_size//2 + 10,
                 center_x + icon_size//2 - 10, icon_y + icon_size//2 - 10],
                start=225, end=315, fill=(140, 160, 220), width=arc_width
            )
            
            # Haupttext (direkt unter Icon)
            text_y = icon_y + icon_size//2 + 40
            text = "Bereit"
            bbox = draw.textbbox((0, 0), text, font=font_main)
            text_width = bbox[2] - bbox[0]
            draw.text((center_x - text_width//2, text_y), text, fill=(180, 190, 220), font=font_main)
            
            # Subtext (darunter, etwas heller)
            subtext = "Lege eine CD ein"
            bbox_sub = draw.textbbox((0, 0), subtext, font=font_sub)
            subtext_width = bbox_sub[2] - bbox_sub[0]
            draw.text((center_x - subtext_width//2, text_y + 35), subtext, fill=(120, 140, 180), font=font_sub)
            
            # Auf Display anzeigen
            self.display.image(img)
            logger.info("Idle-Screen angezeigt")
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen des Idle-Screens: {e}")
    
    def _draw_text_wrapped(self, draw, text, font, y_pos, color, max_width):
        """
        Zeichnet Text mit automatischem Zeilenumbruch
        
        Args:
            draw: ImageDraw Objekt
            text: Der zu zeichnende Text
            font: Font-Objekt
            y_pos: Y-Position für den Text
            color: Textfarbe
            max_width: Maximale Breite in Pixeln
            
        Returns:
            Die neue Y-Position nach dem Text
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            width = bbox[2] - bbox[0]
            
            if width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Wort ist zu lang, muss gekürzt werden
                    lines.append(word[:20] + '...')
                    current_line = []
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Zeichne alle Zeilen zentriert
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), line, fill=color, font=font)
            y_pos += bbox[3] - bbox[1] + 5  # Zeilenhöhe + kleiner Abstand
        
        return y_pos
    
    def show_cd_info(self, cd_info, cover_path=None):
        """
        Kompatibilitäts-Wrapper für main.py - zeigt CD mit Cover
        
        Args:
            cd_info: Dict mit 'name' (Album) und 'artist'
            cover_path: Pfad zum Cover-Bild (optional)
        """
        if isinstance(cd_info, dict):
            artist = cd_info.get('artist', 'Unknown Artist')
            album = cd_info.get('name', 'Unknown Album')
            self.show_cd_with_cover(artist, album, cover_path=cover_path)
        else:
            # Fallback für alten Aufruf
            logger.warning("show_cd_info mit unbekanntem Format aufgerufen")
    
    def show_cd_with_cover(self, artist, album, cover_path=None, year=None):
        """
        SCHRITT 3: Zeigt CD-Info mit Cover-Bild
        
        Args:
            artist: Künstlername
            album: Albumname
            cover_path: Lokaler Pfad oder URL zum Cover-Bild (optional)
            year: Jahr (optional)
        """
        if not self.enabled or not self.display:
            return
        
        try:
            # Weißer Hintergrund
            img = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Fonts laden
            try:
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
            except:
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # Cover laden und skalieren - 220px mit 10px Rand
            cover_img = None
            cover_size = 220  # 220px, lässt 10px Rand auf jeder Seite
            cover_x = 10
            cover_y = 10
            
            # Schatten zeichnen (leicht versetzt, dunkler)
            shadow_offset = 3
            draw.rectangle(
                [(cover_x + shadow_offset, cover_y + shadow_offset), 
                 (cover_x + cover_size + shadow_offset, cover_y + cover_size + shadow_offset)],
                fill=(200, 200, 200)
            )
            
            if cover_path:
                try:
                    if cover_path.startswith('http'):
                        # Von URL laden
                        response = requests.get(cover_path, timeout=5)
                        cover_img = Image.open(BytesIO(response.content))
                    else:
                        # Von lokalem Pfad laden
                        cover_img = Image.open(cover_path)
                    
                    # Cover auf quadratische Größe skalieren
                    cover_img = cover_img.resize((cover_size, cover_size), Image.Resampling.LANCZOS)
                    
                    # Cover mit 10px Rand einfügen
                    img.paste(cover_img, (cover_x, cover_y))
                    
                    # Border um das Cover zeichnen
                    draw.rectangle(
                        [(cover_x, cover_y), (cover_x + cover_size - 1, cover_y + cover_size - 1)],
                        outline=(200, 200, 200),
                        width=1
                    )
                    
                    logger.info(f"Cover geladen: {cover_path[:50]}")
                    
                except Exception as e:
                    logger.warning(f"Cover konnte nicht geladen werden: {e}")
                    cover_path = None  # Fallback zu Platzhalter
            
            # Platzhalter zeichnen, wenn kein Cover
            if not cover_path or not cover_img:
                # Weißer Hintergrund für Platzhalter
                draw.rectangle(
                    [(cover_x, cover_y), (cover_x + cover_size, cover_y + cover_size)],
                    fill=(255, 255, 255),
                    outline=(150, 150, 150),
                    width=2
                )
                # Platzhalter-Text (zentriert)
                draw.text((cover_x + 75, cover_y + 95), "NO", fill=(120, 120, 120), font=font_medium)
                draw.text((cover_x + 60, cover_y + 120), "COVER", fill=(120, 120, 120), font=font_medium)
            
            # Auf Display anzeigen
            self.display.image(img)
            logger.info(f"CD mit Cover angezeigt: {artist} - {album}")
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen von CD mit Cover: {e}")
    
    def show_progress(self, step, progress, current_track=None, total_tracks=None, cover_path=None):
        """
        SCHRITT 4: Zeigt Cover mit Fortschrittsbalken
        
        Args:
            step: Phase (ripping, encoding, tagging, syncing)
            progress: Fortschritt in Prozent (0-100)
            current_track: Aktueller Track (optional)
            total_tracks: Gesamt-Tracks (optional)
            cover_path: Pfad zum Cover-Bild (optional)
        """
        if not self.enabled or not self.display:
            return
        
        try:
            # Weißer Hintergrund
            img = Image.new('RGB', (self.width, self.height), color=(255, 255, 255))
            draw = ImageDraw.Draw(img)
            
            # Fonts laden
            try:
                font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 18)
                font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
            except:
                font_medium = ImageFont.load_default()
                font_small = ImageFont.load_default()
            
            # === COVER BEREICH (wie in show_cd_with_cover) ===
            cover_size = 220
            cover_x = 10
            cover_y = 10
            
            # Schatten zeichnen
            shadow_offset = 3
            draw.rectangle(
                [(cover_x + shadow_offset, cover_y + shadow_offset), 
                 (cover_x + cover_size + shadow_offset, cover_y + cover_size + shadow_offset)],
                fill=(180, 180, 180)
            )
            
            # Cover laden (falls vorhanden)
            if cover_path:
                try:
                    if cover_path.startswith('http'):
                        response = requests.get(cover_path, timeout=5)
                        cover_img = Image.open(BytesIO(response.content))
                    else:
                        cover_img = Image.open(cover_path)
                    
                    cover_img = cover_img.resize((cover_size, cover_size), Image.Resampling.LANCZOS)
                    img.paste(cover_img, (cover_x, cover_y))
                    
                    # Border um das Cover
                    draw.rectangle(
                        [(cover_x, cover_y), (cover_x + cover_size - 1, cover_y + cover_size - 1)],
                        outline=(200, 200, 200),
                        width=1
                    )
                except Exception as e:
                    logger.warning(f"Cover konnte nicht geladen werden: {e}")
                    cover_path = None
            
            # Platzhalter, wenn kein Cover
            if not cover_path:
                draw.rectangle(
                    [(cover_x, cover_y), (cover_x + cover_size, cover_y + cover_size)],
                    fill=(255, 255, 255),
                    outline=(150, 150, 150),
                    width=2
                )
            
            # === PROGRESS BEREICH (unterhalb des Covers) ===
            progress_y = cover_y + cover_size + 20  # Mehr Abstand
            
            # Farben für verschiedene Steps
            step_colors = {
                'detecting': (100, 100, 200),
                'identifying': (100, 100, 200),
                'ripping': (100, 200, 100),     # Grün
                'encoding': (100, 150, 255),    # Blau
                'tagging': (200, 150, 100),
                'syncing': (200, 100, 200)      # Violett
            }
            
            # Icons für verschiedene Steps (Unicode Emojis)
            step_icons = {
                'detecting': '💿',
                'identifying': '🔍',
                'ripping': '💿',      # CD Icon
                'encoding': '⚙️',     # Zahnrad/Encoding Icon
                'tagging': '🏷️',
                'syncing': '📤'       # Upload/Transfer Icon
            }
            
            bar_color = step_colors.get(step, (100, 200, 100))
            
            # --- Vektor-Icon zeichnen (statt Emoji) ---
            def _draw_vector_icon(step, x, y, size, color):
                """Zeichnet einfache Vektor-Icons direkt auf das Haupt-Image"""
                center_x = x + size // 2
                center_y = y + size // 2
                
                if step in ['detecting', 'identifying', 'ripping']:
                    # CD Icon
                    # Äußerer Kreis
                    draw.ellipse([x + 3, y + 3, x + size - 3, y + size - 3], outline=color, width=3)
                    # Innerer Kreis (Loch)
                    hole_size = size // 4
                    hole_x = center_x - hole_size // 2
                    hole_y = center_y - hole_size // 2
                    draw.ellipse([hole_x, hole_y, hole_x + hole_size, hole_y + hole_size], fill=color)
                    # Glanz-Effekt (kleine Bögen)
                    draw.arc([x + 8, y + 8, x + size - 8, y + size - 8], 30, 60, fill=color, width=2)
                    draw.arc([x + 8, y + 8, x + size - 8, y + size - 8], 130, 160, fill=color, width=2)
                    
                elif step in ['encoding', 'tagging']:
                    # Zahnrad Icon
                    import math
                    radius = size // 3
                    
                    # 8 Zähne
                    for i in range(8):
                        angle = i * 45
                        rad = math.radians(angle)
                        
                        # Äußere Punkte
                        x1 = center_x + int((radius + 6) * math.cos(rad))
                        y1 = center_y + int((radius + 6) * math.sin(rad))
                        
                        # Innere Punkte
                        rad_left = math.radians(angle - 12)
                        rad_right = math.radians(angle + 12)
                        x2 = center_x + int(radius * math.cos(rad_left))
                        y2 = center_y + int(radius * math.sin(rad_left))
                        x3 = center_x + int(radius * math.cos(rad_right))
                        y3 = center_y + int(radius * math.sin(rad_right))
                        
                        draw.polygon([x1, y1, x2, y2, x3, y3], fill=color)
                    
                    # Hauptkreis
                    draw.ellipse([center_x - radius, center_y - radius, 
                                 center_x + radius, center_y + radius], 
                                outline=color, width=2)
                    
                    # Inneres Loch
                    hole_radius = radius // 3
                    draw.ellipse([center_x - hole_radius, center_y - hole_radius,
                                 center_x + hole_radius, center_y + hole_radius],
                                fill=color)
                    
                elif step == 'syncing':
                    # Upload/Transfer Icon
                    arrow_width = size // 3
                    
                    # Pfeilspitze (Dreieck nach oben)
                    draw.polygon([
                        center_x, y + 6,  # Spitze
                        center_x - arrow_width, y + 18,  # Links
                        center_x + arrow_width, y + 18   # Rechts
                    ], fill=color)
                    
                    # Pfeilschaft
                    shaft_width = arrow_width // 2
                    draw.rectangle([
                        center_x - shaft_width, y + 16,
                        center_x + shaft_width, y + size - 10
                    ], fill=color)
                    
                    # Basis-Linie
                    draw.line([x + 6, y + size - 6, x + size - 6, y + size - 6], 
                             fill=color, width=3)
            
            # Icon links neben der Progress Bar zeichnen
            icon_size = 36
            icon_x = 10
            icon_y = progress_y + 4
            _draw_vector_icon(step, icon_x, icon_y, icon_size, bar_color)

            # Progress Bar - gleiche Höhe wie Icon, leicht abgerundete Ecken, mit Rahmen
            bar_width = 220 - (icon_size + 8)
            bar_height = 36  # Gleiche Höhe wie Icon
            bar_x = icon_x + icon_size + 8
            bar_y = progress_y + 4  # Gleiche Y-Position wie Icon
            corner_radius = 4  # Kleine Rundung statt Pille
            
            # Funktion für abgerundetes Rechteck
            def draw_rounded_rectangle(draw, coords, radius, fill=None, outline=None, width=1):
                """Zeichnet ein Rechteck mit abgerundeten Ecken"""
                x1, y1, x2, y2 = coords
                
                # Hauptrechtecke (ohne Ecken)
                if fill:
                    draw.rectangle([x1 + radius, y1, x2 - radius, y2], fill=fill)
                    draw.rectangle([x1, y1 + radius, x2, y2 - radius], fill=fill)
                    
                    # Ecken (Kreise)
                    draw.ellipse([x1, y1, x1 + radius * 2, y1 + radius * 2], fill=fill)
                    draw.ellipse([x2 - radius * 2, y1, x2, y1 + radius * 2], fill=fill)
                    draw.ellipse([x1, y2 - radius * 2, x1 + radius * 2, y2], fill=fill)
                    draw.ellipse([x2 - radius * 2, y2 - radius * 2, x2, y2], fill=fill)
                
                if outline:
                    # Outline mit Linien
                    draw.arc([x1, y1, x1 + radius * 2, y1 + radius * 2], 180, 270, fill=outline, width=width)
                    draw.arc([x2 - radius * 2, y1, x2, y1 + radius * 2], 270, 360, fill=outline, width=width)
                    draw.arc([x1, y2 - radius * 2, x1 + radius * 2, y2], 90, 180, fill=outline, width=width)
                    draw.arc([x2 - radius * 2, y2 - radius * 2, x2, y2], 0, 90, fill=outline, width=width)
                    
                    draw.line([x1 + radius, y1, x2 - radius, y1], fill=outline, width=width)
                    draw.line([x1 + radius, y2, x2 - radius, y2], fill=outline, width=width)
                    draw.line([x1, y1 + radius, x1, y2 - radius], fill=outline, width=width)
                    draw.line([x2, y1 + radius, x2, y2 - radius], fill=outline, width=width)
            
            # Rahmen um die gesamte Bar (dunkelgrau)
            frame_padding = 2
            draw_rounded_rectangle(
                draw,
                [bar_x - frame_padding, bar_y - frame_padding, 
                 bar_x + bar_width + frame_padding, bar_y + bar_height + frame_padding],
                corner_radius + frame_padding,
                outline=(150, 150, 150),
                width=2
            )
            
            # Hintergrund der Bar (hellgrau, abgerundet) - mit Abstand zum Rahmen
            inner_padding = 2
            draw_rounded_rectangle(
                draw,
                [bar_x + inner_padding, bar_y + inner_padding, 
                 bar_x + bar_width - inner_padding, bar_y + bar_height - inner_padding],
                corner_radius - 1,
                fill=(240, 240, 240)
            )
            
            # Fortschritts-Balken (farbig je nach Step, abgerundet) - mit Abstand zum Rahmen
            if progress > 0:
                progress_width = int((bar_width - inner_padding * 2) * (progress / 100))
                if progress_width > corner_radius * 2:  # Nur zeichnen wenn breit genug für Rundung
                    draw_rounded_rectangle(
                        draw,
                        [bar_x + inner_padding, bar_y + inner_padding, 
                         bar_x + inner_padding + progress_width, bar_y + bar_height - inner_padding],
                        corner_radius - 1,
                        fill=bar_color
                    )
            
            # Auf Display anzeigen
            self.display.image(img)
            logger.debug(f"Progress angezeigt: {step} {progress}%")
            
        except Exception as e:
            logger.error(f"Fehler beim Anzeigen des Fortschritts: {e}")
    
    def show_done(self):
        """Zeigt Erfolgs-Screen"""
        pass
    
    def show_error(self, error_message):
        """Zeigt Fehler-Screen"""
        pass
    
    def cleanup(self):
        """Cleanup beim Beenden"""
        if self.enabled and self.display:
            try:
                self._show_black_screen()
                logger.info("Display cleanup abgeschlossen")
            except:
                pass
