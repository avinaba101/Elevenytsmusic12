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
# STEP 1: DIMENSIONS AND POSITIONS
# ==========================================================

W, H = 1280, 720  # Full image size

# Main Panel
PANEL_W, PANEL_H = 1080, 620
PANEL_X = (W - PANEL_W) // 2
PANEL_Y = 50

# Thumbnail Image
THUMB_W, THUMB_H = 960, 410
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + 25

# Title Position
TITLE_X = THUMB_X + 15
TITLE_Y = THUMB_Y + THUMB_H + 30

# Meta Info Position
META_Y = TITLE_Y + 50

# Progress Bar Position
BAR_X = THUMB_X + 15
BAR_Y = META_Y + 50
BAR_TOTAL_LEN = 930

# Max title width
MAX_TITLE_WIDTH = 850

# Bot Name
BOT_NAME = "𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬"


# ==========================================================
# STEP 2: HELPER FUNCTIONS
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
    """Format view count"""
    if not views:
        return "Unknown Views"
    try:
        views = int(views)
        if views >= 1000000:
            return f"{views//1000000}M Views"
        elif views >= 1000:
            return f"{views//1000}K Views"
        else:
            return f"{views} Views"
    except:
        return "Unknown Views"


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
# STEP 3: MAIN THUMBNAIL CLASS
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
            self.badge_font = ImageFont.truetype(font_path + "Raleway-Bold.ttf", 16)
        except:
            self.title_font = ImageFont.load_default()
            self.regular_font = ImageFont.load_default()
            self.bot_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.badge_font = ImageFont.load_default()

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
            
            # Return cached if exists
            if os.path.exists(output):
                return output
            
            # Download thumbnail
            temp = f"cache/temp_{song.id}.jpg"
            thumb_url = getattr(song, 'thumbnail', None)
            
            if not thumb_url:
                thumb_url = f"https://img.youtube.com/vi/{song.id}/maxresdefault.jpg"
            
            downloaded = await self.download_thumb(thumb_url, temp)
            
            if not downloaded or not os.path.exists(temp):
                return config.DEFAULT_THUMB
            
            # Generate in thread pool
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
            # STEP 4: CREATE BACKGROUND
            # ==========================================================
            
            # Load and resize thumbnail
            with Image.open(temp) as img:
                base = img.resize((W, H)).convert("RGBA")

            # Apply blur for dreamy effect
            bg = base.filter(ImageFilter.GaussianBlur(35))
            bg = ImageEnhance.Brightness(bg).enhance(0.30)
            bg = ImageEnhance.Contrast(bg).enhance(1.3)

            # Dark overlay
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
            draw = ImageDraw.Draw(overlay)

            # Vignette effect - dark corners
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
            # STEP 5: CREATE MAIN PANEL
            # ==========================================================

            panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
            pd = ImageDraw.Draw(panel)

            # Main glass panel
            pd.rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H),
                radius=50,
                fill=(10, 10, 25, 200)
            )

            # Gold border
            pd.rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H),
                radius=50,
                outline=(212, 175, 55, 200),
                width=2
            )

            # Inner subtle glow
            pd.rounded_rectangle(
                (3, 3, PANEL_W - 3, PANEL_H - 3),
                radius=47,
                outline=(212, 175, 55, 50),
                width=1
            )

            # Top shine line
            pd.rounded_rectangle(
                (15, 15, PANEL_W - 15, PANEL_H//3 + 20),
                radius=42,
                outline=(255, 255, 255, 12),
                width=1
            )

            # Paste panel
            mask = Image.new("L", (PANEL_W, PANEL_H), 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H), radius=50, fill=255
            )
            bg.paste(panel, (PANEL_X, PANEL_Y), mask)
            draw = ImageDraw.Draw(bg)

            # ==========================================================
            # STEP 6: ADD THUMBNAIL WITH GOLD FRAME
            # ==========================================================

            # Resize thumbnail
            thumb = base.resize((THUMB_W, THUMB_H))

            # Gold glow frame (minimal)
            for i in range(8, 0, -1):
                alpha = int(25 * (i / 8))
                draw.rounded_rectangle(
                    (THUMB_X - i, THUMB_Y - i,
                     THUMB_X + THUMB_W + i, THUMB_Y + THUMB_H + i),
                    radius=30 + i,
                    outline=(212, 175, 55, alpha),
                    width=1
                )

            # Paste thumbnail with rounded corners
            thumb_mask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(thumb_mask).rounded_rectangle(
                (0, 0, THUMB_W, THUMB_H), radius=28, fill=255
            )
            bg.paste(thumb, (THUMB_X, THUMB_Y), thumb_mask)

            # Gold border
            draw.rounded_rectangle(
                (THUMB_X, THUMB_Y, THUMB_X + THUMB_W, THUMB_Y + THUMB_H),
                radius=28,
                outline=(212, 175, 55, 200),
                width=2
            )

            # Inner border
            draw.rounded_rectangle(
                (THUMB_X + 5, THUMB_Y + 5,
                 THUMB_X + THUMB_W - 5, THUMB_Y + THUMB_H - 5),
                radius=23,
                outline=(212, 175, 55, 60),
                width=1
            )

            # ==========================================================
            # STEP 7: ADD SONG TITLE
            # ==========================================================

            # Gold accent bar
            draw.rounded_rectangle(
                (TITLE_X, TITLE_Y + 2, TITLE_X + 6, TITLE_Y + 46),
                radius=3,
                fill=(212, 175, 55)
            )

            # Get and trim title
            song_title = getattr(song, 'title', 'Unknown Track')
            clean_title = re.sub(r"\W+", " ", song_title).strip().title()
            final_title = trim_text(clean_title, self.title_font, MAX_TITLE_WIDTH)

            # Title shadow
            draw.text(
                (TITLE_X + 18, TITLE_Y + 3),
                final_title,
                fill=(0, 0, 0, 120),
                font=self.title_font
            )

            # Main title - white
            draw.text(
                (TITLE_X + 16, TITLE_Y + 1),
                final_title,
                fill=(255, 255, 255, 255),
                font=self.title_font
            )

            # ==========================================================
            # STEP 8: ADD META INFO
            # ==========================================================

            views = format_views(getattr(song, 'view_count', None))
            meta_text = f"✦  PREMIUM  ✦  YOUTUBE  ✦  {views}"

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
            # STEP 9: ADD PROGRESS BAR
            # ==========================================================

            # Background track
            draw.rounded_rectangle(
                (BAR_X, BAR_Y - 4, BAR_X + BAR_TOTAL_LEN, BAR_Y + 4),
                radius=8,
                fill=(40, 40, 55)
            )

            # Progress (gold gradient)
            bar_len = 350  # Default progress
            for i in range(bar_len):
                progress = i / bar_len if bar_len > 0 else 0
                r = int(180 + 32 * progress)
                g = int(150 + 25 * progress)
                b = int(40 + 15 * progress)
                draw.line(
                    [(BAR_X + i, BAR_Y - 3), (BAR_X + i, BAR_Y + 3)],
                    fill=(r, g, b, 200)
                )

            # Knob glow (minimal)
            for i in range(6, 0, -1):
                alpha = int(30 * (i / 6))
                draw.ellipse(
                    (BAR_X + bar_len - 10 - i, BAR_Y - 10 - i,
                     BAR_X + bar_len + 10 + i, BAR_Y + 10 + i),
                    fill=(212, 175, 55, alpha)
                )

            # Knob
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

            # Time labels
            draw.text(
                (BAR_X, BAR_Y + 16),
                "00:00",
                fill=(180, 180, 195),
                font=self.small_font
            )

            # Duration
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
            # STEP 10: ADD BOT NAME (SIDE POSITION)
            # ==========================================================

            bot_text = f"✦ {BOT_NAME} ✦"

            bot_width = self.bot_font.getlength(bot_text)
            bot_height = self.bot_font.getbbox(bot_text)[3] - self.bot_font.getbbox(bot_text)[1]

            # Position: Bottom Right
            bot_x = PANEL_X + PANEL_W - bot_width - 30
            bot_y = PANEL_Y + PANEL_H - bot_height - 20

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

            # Gold underline
            draw.line(
                [(bot_x, bot_y + bot_height + 4),
                 (bot_x + bot_width, bot_y + bot_height + 4)],
                fill=(212, 175, 55, 80),
                width=1
            )

            # ==========================================================
            # STEP 11: ADD PREMIUM BADGE
            # ==========================================================

            badge_text = "✦ PREMIUM ✦"
            badge_width = self.badge_font.getlength(badge_text)
            badge_x = PANEL_X + PANEL_W - badge_width - 30
            badge_y = PANEL_Y + 15

            draw.text(
                (badge_x, badge_y),
                badge_text,
                fill=(212, 175, 55, 150),
                font=self.badge_font
            )

            # ==========================================================
            # STEP 12: ADD CORNER DECORATIONS
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
            # STEP 13: SAVE IMAGE
            # ==========================================================

            bg.save(output, "PNG")

            # Clean temp
            try:
                os.remove(temp)
            except:
                pass

            return output

        except Exception as e:
            print(f"Generation Error: {e}")
            return config.DEFAULT_THUMB
