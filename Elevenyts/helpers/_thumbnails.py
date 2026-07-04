# ==========================================================
# Copyright (c) 2026 ArtistBots
# All Rights Reserved.
# 
# Project      : ArtistBots API Telegram Music Bot
# Powered By   : Artist
# Type         : API Based Telegram Music Bot
#
# Bot          : @ArtistApibot
# Channel      : https://t.me/artistbots
# GitHub       : https://github.com/elevenyts
#
# Unauthorized copying, modification, or redistribution
# of this source code without permission is prohibited.
# ==========================================================
import os
import re
import asyncio
import aiohttp
import base64
import math
import urllib.request

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageChops
)

from Elevenyts import config
from Elevenyts.helpers import Track


# ========== PREMIUM DIMENSIONS ==========
PANEL_W, PANEL_H = 1100, 640
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 40

THUMB_W, THUMB_H = 980, 430
THUMB_X = PANEL_X + (PANEL_W - THUMB_W) // 2
THUMB_Y = PANEL_Y + 20

TITLE_X = THUMB_X + 10
TITLE_Y = THUMB_Y + THUMB_H + 30

META_Y = TITLE_Y + 55
BAR_X = THUMB_X + 10
BAR_Y = META_Y + 55
BAR_RED_LEN = 340
BAR_TOTAL_LEN = 940

MAX_TITLE_WIDTH = 830

# ========== PREMIUM COLOR PALETTE ==========
PREMIUM_COLORS = {
    'gold': (212, 175, 55),
    'dark_gold': (180, 150, 40),
    'light_gold': (240, 210, 120),
    'black': (10, 10, 15),
    'dark_gray': (30, 30, 40),
    'white': (255, 255, 255),
    'silver': (192, 192, 200),
}


def trim_to_width(text: str, font, max_w: int) -> str:
    """Trim text to fit within max width"""
    if not text:
        return "Unknown Title"
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis


class Thumbnail:

    def __init__(self):
        try:
            self.title_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 44)
            self.regular_font = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 22)
            self.signature_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 28)
            self.small_font = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 18)
            self.bot_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 26)
            self.premium_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 20)
        except OSError:
            self.title_font = ImageFont.load_default()
            self.regular_font = ImageFont.load_default()
            self.signature_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.bot_font = ImageFont.load_default()
            self.premium_font = ImageFont.load_default()

    async def save_thumb(self, output_path: str, url: str):
        """Download thumbnail from URL"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as resp:
                    if resp.status == 200:
                        with open(output_path, "wb") as f:
                            f.write(await resp.read())
                        return output_path
        except Exception as e:
            print(f"Error downloading thumbnail: {e}")
        return None

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        """Generate premium thumbnail"""
        try:
            # Create cache directory if not exists
            os.makedirs("cache", exist_ok=True)
            
            output = f"cache/{song.id}_premium.png"
            
            # Return cached if exists
            if os.path.exists(output):
                return output
            
            # Download thumbnail
            temp = f"cache/temp_{song.id}.jpg"
            
            # Get thumbnail URL from song object
            thumb_url = getattr(song, 'thumbnail', None)
            if not thumb_url:
                # Try to get from youtube
                thumb_url = f"https://img.youtube.com/vi/{song.id}/maxresdefault.jpg"
            
            # Download thumbnail
            downloaded = await self.save_thumb(temp, thumb_url)
            
            if not downloaded or not os.path.exists(temp):
                # Use default thumbnail
                return config.DEFAULT_THUMB
            
            # Generate in thread pool
            return await asyncio.get_event_loop().run_in_executor(
                None, self._generate_sync, temp, output, song, size)
                
        except Exception as e:
            print(f"Error generating premium thumbnail: {e}")
            return config.DEFAULT_THUMB

    def _generate_sync(self, temp, output, song, size=(1280, 720)):
        """Synchronous thumbnail generation"""
        try:
            W, H = size

            # ===== 1. LOAD BACKGROUND =====
            try:
                with Image.open(temp) as tmp:
                    base = tmp.resize(size).convert("RGBA")
            except Exception as e:
                print(f"Error loading image: {e}")
                # Create fallback background
                base = Image.new("RGBA", size, (20, 20, 30, 255))

            # ===== 2. PREMIUM BACKGROUND =====
            # Deep blur for premium feel
            bg = base.filter(ImageFilter.GaussianBlur(30))
            bg = ImageEnhance.Brightness(bg).enhance(0.25)
            bg = ImageEnhance.Contrast(bg).enhance(1.5)
            bg = ImageEnhance.Color(bg).enhance(0.5)
            
            # Dark overlay - premium feel
            overlay = Image.new("RGBA", size, (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            
            # Vignette effect
            for i in range(80, 0, -1):
                alpha = int(150 * (1 - i / 80))
                spread = i * 5
                od.ellipse(
                    (W//2 - spread, H//2 - spread * 9//16,
                     W//2 + spread, H//2 + spread * 9//16),
                    fill=(0, 0, 0, alpha)
                )
            
            bg = Image.alpha_composite(bg, overlay)

            # Gold accent lines
            line_draw = ImageDraw.Draw(bg)
            for i in range(0, W, 200):
                line_draw.line(
                    [(i, 0), (i + 50, H)],
                    fill=(212, 175, 55, 5),
                    width=1
                )

            draw = ImageDraw.Draw(bg)

            # ===== 3. PREMIUM GLASS PANEL =====
            panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
            pd = ImageDraw.Draw(panel)

            # Main panel
            pd.rounded_rectangle(
                (0, 0, PANEL_W - 1, PANEL_H - 1),
                radius=48,
                fill=(15, 15, 25, 185)
            )
            
            # Gold border
            pd.rounded_rectangle(
                (0, 0, PANEL_W - 1, PANEL_H - 1),
                radius=48,
                outline=(212, 175, 55, 180),
                width=2
            )
            
            # Inner subtle glow
            pd.rounded_rectangle(
                (3, 3, PANEL_W - 4, PANEL_H - 4),
                radius=45,
                outline=(212, 175, 55, 40),
                width=1
            )
            
            # Premium shine
            pd.rounded_rectangle(
                (10, 10, PANEL_W - 10, PANEL_H//3),
                radius=42,
                outline=(255, 255, 255, 10),
                width=1
            )

            pmask = Image.new("L", (PANEL_W, PANEL_H), 0)
            ImageDraw.Draw(pmask).rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H), radius=48, fill=255)
            bg.paste(panel, (PANEL_X, PANEL_Y), pmask)
            draw = ImageDraw.Draw(bg)

            # ===== 4. PREMIUM THUMBNAIL =====
            try:
                thumb = base.resize((THUMB_W, THUMB_H))
            except:
                thumb = Image.new("RGBA", (THUMB_W, THUMB_H), (30, 30, 40, 255))
            
            # Minimal glow frame
            for i in range(6, 0, -1):
                alpha = int(20 * (i / 6))
                draw.rounded_rectangle(
                    (THUMB_X - i, THUMB_Y - i,
                     THUMB_X + THUMB_W + i, THUMB_Y + THUMB_H + i),
                    radius=28 + i,
                    outline=(212, 175, 55, alpha),
                    width=1
                )

            # Thumbnail with rounded corners
            tmask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(tmask).rounded_rectangle(
                (0, 0, THUMB_W, THUMB_H), radius=26, fill=255)
            bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)

            # Premium border
            draw.rounded_rectangle(
                (THUMB_X, THUMB_Y, THUMB_X + THUMB_W, THUMB_Y + THUMB_H),
                radius=26,
                outline=(212, 175, 55, 200),
                width=2
            )
            
            # Inner border
            draw.rounded_rectangle(
                (THUMB_X + 4, THUMB_Y + 4, 
                 THUMB_X + THUMB_W - 4, THUMB_Y + THUMB_H - 4),
                radius=22,
                outline=(212, 175, 55, 60),
                width=1
            )

            # ===== 5. SONG TITLE =====
            # Gold accent bar
            draw.rounded_rectangle(
                (TITLE_X, TITLE_Y + 2, TITLE_X + 6, TITLE_Y + 46),
                radius=3,
                fill=(212, 175, 55)
            )

            # Get song title
            song_title = getattr(song, 'title', 'Unknown Song')
            clean_title = re.sub(r"\W+", " ", song_title).title()
            final_title = trim_to_width(clean_title, self.title_font, MAX_TITLE_WIDTH)
            
            # Title shadow
            draw.text(
                (TITLE_X + 15, TITLE_Y + 2),
                final_title,
                fill=(0, 0, 0, 100),
                font=self.title_font
            )
            
            # Main title
            draw.text(
                (TITLE_X + 14, TITLE_Y + 1),
                final_title,
                fill=(255, 255, 255),
                font=self.title_font
            )

            # ===== 6. META INFO =====
            # Get views
            views = getattr(song, 'view_count', None)
            if views:
                if views >= 1000000:
                    views_text = f"{views//1000000}M views"
                elif views >= 1000:
                    views_text = f"{views//1000}K views"
                else:
                    views_text = f"{views} views"
            else:
                views_text = "Unknown Views"
            
            meta_text = f"✦  PREMIUM PLAYLIST  ✦  YOUTUBE  ✦  {views_text}"
            
            draw.text(
                (TITLE_X + 14, META_Y),
                meta_text,
                fill=(212, 175, 55, 200),
                font=self.regular_font
            )
            
            # Gold divider
            draw.line(
                [(TITLE_X + 14, META_Y + 28), (TITLE_X + 250, META_Y + 28)],
                fill=(212, 175, 55, 80),
                width=1
            )

            # ===== 7. PROGRESS BAR =====
            # Background
            draw.rounded_rectangle(
                (BAR_X, BAR_Y - 4, BAR_X + BAR_TOTAL_LEN, BAR_Y + 4),
                radius=8,
                fill=(40, 40, 50)
            )
            
            # Progress - gold gradient
            for i in range(BAR_RED_LEN):
                progress = i / BAR_RED_LEN if BAR_RED_LEN > 0 else 0
                r = int(180 + 32 * progress)
                g = int(150 + 25 * progress)
                b = int(40 + 15 * progress)
                draw.line(
                    [(BAR_X + i, BAR_Y - 3), (BAR_X + i, BAR_Y + 3)],
                    fill=(r, g, b, 200)
                )
            
            # Minimal glow behind knob
            for i in range(6, 0, -1):
                alpha = int(30 * (i / 6))
                draw.ellipse(
                    (BAR_X + BAR_RED_LEN - 10 - i, BAR_Y - 10 - i,
                     BAR_X + BAR_RED_LEN + 10 + i, BAR_Y + 10 + i),
                    fill=(212, 175, 55, alpha)
                )
            
            # Premium knob
            draw.ellipse(
                (BAR_X + BAR_RED_LEN - 8, BAR_Y - 8,
                 BAR_X + BAR_RED_LEN + 8, BAR_Y + 8),
                fill=(212, 175, 55)
            )
            draw.ellipse(
                (BAR_X + BAR_RED_LEN - 4, BAR_Y - 4,
                 BAR_X + BAR_RED_LEN + 4, BAR_Y + 4),
                fill=(255, 255, 255)
            )

            # Time stamps
            draw.text(
                (BAR_X, BAR_Y + 16),
                "00:00",
                fill=(180, 180, 190),
                font=self.small_font
            )
            
            # Duration
            duration = getattr(song, 'duration', '2:46')
            is_live = getattr(song, 'is_live', False)
            end_text = "● LIVE" if is_live else duration
            
            # Fix duration format if needed
            if not is_live and duration and ':' not in str(duration):
                # Convert seconds to mm:ss if needed
                try:
                    secs = int(duration)
                    mins = secs // 60
                    secs = secs % 60
                    end_text = f"{mins}:{secs:02d}"
                except:
                    end_text = "2:46"
            
            tw = self.small_font.getlength(str(end_text))
            draw.text(
                (BAR_X + BAR_TOTAL_LEN - tw, BAR_Y + 16),
                str(end_text),
                fill=(212, 175, 55) if is_live else (180, 180, 190),
                font=self.small_font
            )

            # ===== 8. BOT NAME - SIDE POSITION =====
            bot_text = "✦ 𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬 ✦"
            
            bw = self.bot_font.getlength(bot_text)
            bh = self.bot_font.getbbox(bot_text)[3] - self.bot_font.getbbox(bot_text)[1]
            
            bx = PANEL_X + PANEL_W - bw - 30
            by = PANEL_Y + PANEL_H - bh - 20
            
            # Minimal glow
            for i in range(4, 0, -1):
                alpha = int(20 * (i / 4))
                draw.text(
                    (bx + i//2, by + i//2),
                    bot_text,
                    fill=(212, 175, 55, alpha),
                    font=self.bot_font
                )
            
            # Main bot name
            draw.text(
                (bx, by),
                bot_text,
                fill=(212, 175, 55, 220),
                font=self.bot_font
            )
            
            # Gold underline
            draw.line(
                [(bx, by + bh + 4), (bx + bw, by + bh + 4)],
                fill=(212, 175, 55, 100),
                width=1
            )

            # ===== 9. DECORATIVE ELEMENTS =====
            # Gold dots at corners
            for corner in [(PANEL_X + 20, PANEL_Y + 20),
                          (PANEL_X + PANEL_W - 20, PANEL_Y + 20),
                          (PANEL_X + 20, PANEL_Y + PANEL_H - 20),
                          (PANEL_X + PANEL_W - 20, PANEL_Y + PANEL_H - 20)]:
                draw.ellipse(
                    (corner[0] - 3, corner[1] - 3, corner[0] + 3, corner[1] + 3),
                    fill=(212, 175, 55, 120)
                )
            
            # PREMIUM badge
            badge_text = "✦ PREMIUM ✦"
            badge_w = self.premium_font.getlength(badge_text)
            badge_x = PANEL_X + PANEL_W - badge_w - 25
            badge_y = PANEL_Y + 15
            
            draw.text(
                (badge_x, badge_y),
                badge_text,
                fill=(212, 175, 55, 150),
                font=self.premium_font
            )

            # ===== 10. SAVE =====
            bg.save(output, "PNG")
            
            # Clean up temp
            try:
                os.remove(temp)
            except:
                pass
            
            return output

        except Exception as e:
            print(f"Error in premium thumbnail generation: {e}")
            return config.DEFAULT_THUMB
