# ==========================================================
# PREMIUM THUMBNAIL GENERATOR FOR TELEGRAM MUSIC BOT
# ==========================================================
# Bot Name: 𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬
# Style: Premium Dark Theme with Gold Accents
# ==========================================================

import os
import re
import asyncio
import aiohttp
import math
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

from Elevenyts import config
from Elevenyts.helpers import Track


# ==========================================================
# DIMENSIONS AND POSITIONS
# ==========================================================

W, H = 1280, 720

PANEL_W, PANEL_H = 1080, 620
PANEL_X = (W - PANEL_W) // 2
PANEL_Y = 50

THUMB_W, THUMB_H = 960, 410
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + 25

TITLE_X = THUMB_X + 15
TITLE_Y = THUMB_Y + THUMB_H + 30

META_Y = TITLE_Y + 50
BAR_X = THUMB_X + 15
BAR_Y = META_Y + 50
BAR_TOTAL_LEN = 930

MAX_TITLE_WIDTH = 850

# ==========================================================
# BOT NAME
# ==========================================================

BOT_NAME = "𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬"


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def trim_text(text, font, max_width):
    """Trim text with ellipsis if too long"""
    if not text:
        return "Unknown Track"
    if font.getlength(text) <= max_width:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + "…") <= max_width:
            return text[:i] + "…"
    return "…"


def format_views(views):
    """Format view count - FIXED"""
    if not views:
        return "0 Views"
    try:
        views = int(views)
        if views >= 10000000:  # 10M+
            return f"{views//1000000}M Views"
        elif views >= 1000000:  # 1M+
            return f"{round(views/1000000, 1)}M Views"
        elif views >= 1000:     # 1K+
            return f"{views//1000}K Views"
        else:
            return f"{views} Views"
    except:
        return "0 Views"


def format_duration(seconds):
    """Format duration in mm:ss"""
    try:
        seconds = int(seconds)
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"
    except:
        return "00:00"


# ==========================================================
# MAIN THUMBNAIL CLASS
# ==========================================================

class Thumbnail:
    """Premium Dark Theme Thumbnail Generator"""

    def __init__(self):
        """Load fonts"""
        try:
            font_path = "Elevenyts/helpers/"
            self.title_font = ImageFont.truetype(font_path + "Raleway-Bold.ttf", 42)
            self.regular_font = ImageFont.truetype(font_path + "Inter-Light.ttf", 22)
            self.bot_font = ImageFont.truetype(font_path + "Raleway-Bold.ttf", 26)
            self.small_font = ImageFont.truetype(font_path + "Inter-Light.ttf", 18)
            self.badge_font = ImageFont.truetype(font_path + "Raleway-Bold.ttf", 20)
            self.now_playing_font = ImageFont.truetype(font_path + "Raleway-Bold.ttf", 18)
        except:
            self.title_font = ImageFont.load_default()
            self.regular_font = ImageFont.load_default()
            self.bot_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.badge_font = ImageFont.load_default()
            self.now_playing_font = ImageFont.load_default()

    async def download_thumb(self, url, path):
        """Download thumbnail from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(path, "wb") as f:
                            f.write(await resp.read())
                        return True
        except:
            pass
        return False

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        """Generate premium thumbnail"""
        try:
            os.makedirs("cache", exist_ok=True)
            
            output = f"cache/{song.id}_premium.png"
            
            if os.path.exists(output):
                return output
            
            temp = f"cache/temp_{song.id}.jpg"
            thumb_url = getattr(song, 'thumbnail', None)
            
            if not thumb_url:
                thumb_url = f"https://img.youtube.com/vi/{song.id}/maxresdefault.jpg"
            
            downloaded = await self.download_thumb(thumb_url, temp)
            
            if not downloaded or not os.path.exists(temp):
                return config.DEFAULT_THUMB
            
            return await asyncio.get_event_loop().run_in_executor(
                None, self._generate_sync, temp, output, song
            )
            
        except Exception as e:
            print(f"Thumbnail Error: {e}")
            return config.DEFAULT_THUMB

    def _generate_sync(self, temp, output, song):
        """Generate thumbnail synchronously"""
        try:
            # ==========================================================
            # BACKGROUND
            # ==========================================================
            
            with Image.open(temp) as img:
                base = img.resize((W, H)).convert("RGBA")

            bg = base.filter(ImageFilter.GaussianBlur(35))
            bg = ImageEnhance.Brightness(bg).enhance(0.30)
            bg = ImageEnhance.Contrast(bg).enhance(1.3)

            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            for i in range(100, 0, -1):
                alpha = int(180 * (1 - i / 100))
                spread = i * 4
                draw.ellipse(
                    (W//2 - spread, H//2 - spread*9//16,
                     W//2 + spread, H//2 + spread*9//16),
                    fill=(0, 0, 0, alpha)
                )

            bg = Image.alpha_composite(bg, overlay)
            draw = ImageDraw.Draw(bg)

            # ==========================================================
            # MAIN PANEL
            # ==========================================================

            panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
            pd = ImageDraw.Draw(panel)

            pd.rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H),
                radius=50,
                fill=(10, 10, 25, 200)
            )

            pd.rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H),
                radius=50,
                outline=(212, 175, 55, 200),
                width=2
            )

            pd.rounded_rectangle(
                (3, 3, PANEL_W - 3, PANEL_H - 3),
                radius=47,
                outline=(212, 175, 55, 50),
                width=1
            )

            pd.rounded_rectangle(
                (15, 15, PANEL_W - 15, PANEL_H//3 + 20),
                radius=42,
                outline=(255, 255, 255, 12),
                width=1
            )

            mask = Image.new("L", (PANEL_W, PANEL_H), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H), radius=50, fill=255
            )
            bg.paste(panel, (PANEL_X, PANEL_Y), mask)
            draw = ImageDraw.Draw(bg)

            # ==========================================================
            # THUMBNAIL WITH GOLD FRAME
            # ==========================================================

            thumb = base.resize((THUMB_W, THUMB_H))

            for i in range(8, 0, -1):
                alpha = int(25 * (i / 8))
                draw.rounded_rectangle(
                    (THUMB_X - i, THUMB_Y - i,
                     THUMB_X + THUMB_W + i, THUMB_Y + THUMB_H + i),
                    radius=30 + i,
                    outline=(212, 175, 55, alpha),
                    width=1
                )

            thumb_mask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(thumb_mask).rounded_rectangle(
                (0, 0, THUMB_W, THUMB_H), radius=28, fill=255
            )
            bg.paste(thumb, (THUMB_X, THUMB_Y), thumb_mask)

            draw.rounded_rectangle(
                (THUMB_X, THUMB_Y, THUMB_X + THUMB_W, THUMB_Y + THUMB_H),
                radius=28,
                outline=(212, 175, 55, 200),
                width=2
            )

            draw.rounded_rectangle(
                (THUMB_X + 5, THUMB_Y + 5,
                 THUMB_X + THUMB_W - 5, THUMB_Y + THUMB_H - 5),
                radius=23,
                outline=(212, 175, 55, 60),
                width=1
            )

            # ==========================================================
            # SONG TITLE
            # ==========================================================

            draw.rounded_rectangle(
                (TITLE_X, TITLE_Y + 2, TITLE_X + 6, TITLE_Y + 46),
                radius=3,
                fill=(212, 175, 55)
            )

            song_title = getattr(song, 'title', 'Unknown Track')
            clean_title = re.sub(r"\W+", " ", song_title).strip().title()
            final_title = trim_text(clean_title, self.title_font, MAX_TITLE_WIDTH)

            draw.text(
                (TITLE_X + 18, TITLE_Y + 3),
                final_title,
                fill=(0, 0, 0, 120),
                font=self.title_font
            )

            draw.text(
                (TITLE_X + 16, TITLE_Y + 1),
                final_title,
                fill=(255, 255, 255, 255),
                font=self.title_font
            )

            # ==========================================================
            # META INFO - FIXED VIEWS
            # ==========================================================

            # Get real views from song object
            views = getattr(song, 'view_count', None)
            
            # If views is None, try to get from other attributes
            if views is None:
                views = getattr(song, 'views', None)
            
            # If still None, try to get from duration (some bots store views there)
            if views is None:
                views = getattr(song, 'views_count', None)
            
            # Format views
            views_text = format_views(views)
            
            # Create meta text - CHANGED: Removed "PREMIUM" from here
            meta_text = f"✦  YOUTUBE  ✦  {views_text}"

            draw.text(
                (TITLE_X + 16, META_Y),
                meta_text,
                fill=(212, 175, 55, 200),
                font=self.regular_font
            )

            # Gold divider line
            draw.line(
                [(TITLE_X + 16, META_Y + 28), (TITLE_X + 260, META_Y + 28)],
                fill=(212, 175, 55, 80),
                width=1
            )

            # ==========================================================
            # PROGRESS BAR
            # ==========================================================

            draw.rounded_rectangle(
                (BAR_X, BAR_Y - 4, BAR_X + BAR_TOTAL_LEN, BAR_Y + 4),
                radius=8,
                fill=(40, 40, 55)
            )

            bar_len = 350
            for i in range(bar_len):
                progress = i / bar_len if bar_len > 0 else 0
                r = int(180 + 32 * progress)
                g = int(150 + 25 * progress)
                b = int(40 + 15 * progress)
                draw.line(
                    [(BAR_X + i, BAR_Y - 3), (BAR_X + i, BAR_Y + 3)],
                    fill=(r, g, b, 200)
                )

            for i in range(6, 0, -1):
                alpha = int(30 * (i / 6))
                draw.ellipse(
                    (BAR_X + bar_len - 10 - i, BAR_Y - 10 - i,
                     BAR_X + bar_len + 10 + i, BAR_Y + 10 + i),
                    fill=(212, 175, 55, alpha)
                )

            draw.ellipse(
                (BAR_X + bar_len - 8, BAR_Y - 8,
                 BAR_X + bar_len + 8, BAR_Y + 8),
                fill=(212, 175, 55)
            )
            draw.ellipse(
                (BAR_X + bar_len - 4, BAR_Y - 4,
                 BAR_X + bar_len + 4, BAR_Y + 4),
                fill=(255, 255, 255)
            )

            draw.text(
                (BAR_X, BAR_Y + 16),
                "00:00",
                fill=(180, 180, 195),
                font=self.small_font
            )

            duration = getattr(song, 'duration', None)
            if duration and isinstance(duration, int):
                duration = format_duration(duration)
            else:
                duration = "00:00"

            is_live = getattr(song, 'is_live', False)
            end_text = "● LIVE" if is_live else duration

            end_width = self.small_font.getlength(end_text)
            draw.text(
                (BAR_X + BAR_TOTAL_LEN - end_width, BAR_Y + 16),
                end_text,
                fill=(255, 80, 80) if is_live else (180, 180, 195),
                font=self.small_font
            )

            # ==========================================================
            # BOT NAME - TOP RIGHT (REPLACED "PREMIUM")
            # ==========================================================

            bot_text = f"✦ {BOT_NAME} ✦"
            bot_width = self.bot_font.getlength(bot_text)
            
            # Position: Top Right
            bot_x = PANEL_X + PANEL_W - bot_width - 30
            bot_y = PANEL_Y + 15

            # Subtle glow
            for i in range(4, 0, -1):
                alpha = int(20 * (i / 4))
                draw.text(
                    (bot_x + i//2, bot_y + i//2),
                    bot_text,
                    fill=(212, 175, 55, alpha),
                    font=self.bot_font
                )

            # Main bot name
            draw.text(
                (bot_x, bot_y),
                bot_text,
                fill=(212, 175, 55, 230),
                font=self.bot_font
            )

            # ==========================================================
            # NOW PLAYING - BOTTOM RIGHT (REPLACED "PREMIUM")
            # ==========================================================

            now_playing_text = "✦ NOW PLAYING ✦"
            np_width = self.now_playing_font.getlength(now_playing_text)
            
            # Position: Bottom Right (above bot name)
            np_x = PANEL_X + PANEL_W - np_width - 30
            np_y = PANEL_Y + PANEL_H - 60

            draw.text(
                (np_x, np_y),
                now_playing_text,
                fill=(212, 175, 55, 150),
                font=self.now_playing_font
            )

            # ==========================================================
            # CORNER DECORATIONS
            # ==========================================================

            corners = [
                (PANEL_X + 18, PANEL_Y + 18),
                (PANEL_X + PANEL_W - 18, PANEL_Y + 18),
                (PANEL_X + 18, PANEL_Y + PANEL_H - 18),
                (PANEL_X + PANEL_W - 18, PANEL_Y + PANEL_H - 18)
            ]

            for cx, cy in corners:
                draw.ellipse(
                    (cx - 3, cy - 3, cx + 3, cy + 3),
                    fill=(212, 175, 55, 100)
                )

            # ==========================================================
            # SAVE IMAGE
            # ==========================================================

            bg.save(output, "PNG")

            try:
                os.remove(temp)
            except:
                pass

            return output

        except Exception as e:
            print(f"Generation Error: {e}")
            return config.DEFAULT_THUMB
