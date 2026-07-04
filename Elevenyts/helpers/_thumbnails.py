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
import random

from PIL import (
    Image,
    ImageDraw,
    ImageEnhance,
    ImageFilter,
    ImageFont,
    ImageChops,
    ImageOps
)

from Elevenyts import config
from Elevenyts.helpers import Track


# ========== ANIME STYLE DIMENSIONS ==========
PANEL_W, PANEL_H = 1080, 620
PANEL_X = (1280 - PANEL_W) // 2
PANEL_Y = 50

THUMB_W, THUMB_H = 960, 420
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

# ========== ANIME COLOR PALETTE ==========
ANIME_COLORS = {
    'sakura': (255, 150, 200),      # Pink
    'neon_blue': (0, 200, 255),     # Cyan
    'lavender': (180, 130, 255),    # Purple
    'sunset': (255, 100, 80),       # Orange/Red
    'mint': (100, 255, 200),        # Mint Green
    'gold': (255, 215, 0),          # Gold
    'dark_purple': (20, 10, 40),
    'glass_bg': (10, 5, 25, 200),
}

# ========== BOT WATERMARK ==========
BOT_NAME = "𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬"


def _decode_f():
    return f"✦ {BOT_NAME} ✦"


def trim_to_width(text: str, font, max_w: int) -> str:
    ellipsis = "…"
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text) - 1, 0, -1):
        if font.getlength(text[:i] + ellipsis) <= max_w:
            return text[:i] + ellipsis
    return ellipsis


def create_anime_pattern(width, height):
    """Create anime-style decorative pattern"""
    pattern = Image.new("RGBA", (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(pattern)
    
    # Cherry blossom petals
    for _ in range(15):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(8, 20)
        alpha = random.randint(20, 60)
        
        # Petal shape (5-petal flower)
        for i in range(5):
            angle = (i / 5) * 2 * math.pi + random.uniform(0, 0.3)
            px = x + int(size * math.cos(angle))
            py = y + int(size * math.sin(angle))
            draw.ellipse(
                (px - size//3, py - size//3, px + size//3, py + size//3),
                fill=(255, 150, 200, alpha)
            )
    
    # Sparkle stars
    for _ in range(30):
        x = random.randint(0, width)
        y = random.randint(0, height)
        size = random.randint(2, 5)
        alpha = random.randint(30, 80)
        
        # 4-point star
        draw.line([(x - size, y), (x + size, y)], fill=(255, 255, 255, alpha), width=1)
        draw.line([(x, y - size), (x, y + size)], fill=(255, 255, 255, alpha), width=1)
    
    # Glowing circles
    for _ in range(8):
        x = random.randint(0, width)
        y = random.randint(0, height)
        radius = random.randint(40, 120)
        alpha = random.randint(5, 15)
        color = random.choice([
            (255, 150, 200, alpha),
            (0, 200, 255, alpha),
            (180, 130, 255, alpha)
        ])
        draw.ellipse(
            (x - radius, y - radius, x + radius, y + radius),
            outline=color,
            width=2
        )
    
    return pattern


def create_anime_glow(draw, x, y, radius, color, layers=12):
    """Create glowing effect for anime style"""
    for i in range(layers, 0, -1):
        alpha = int(60 * (i / layers))
        r = radius + i * 3
        draw.ellipse(
            (x - r, y - r, x + r, y + r),
            fill=(color[0], color[1], color[2], alpha)
        )


def draw_anime_divider(draw, x, y, width):
    """Draw anime-style decorative divider"""
    # Main line with gradient
    for i in range(width):
        progress = i / width
        r = int(0 + 255 * progress)
        g = int(200 + 50 * progress)
        b = int(255 - 150 * progress)
        draw.line(
            [(x + i, y), (x + i, y + 3)],
            fill=(r, g, b, 200)
        )
    
    # Small diamonds on ends
    for pos in [0, width]:
        draw.polygon(
            [(x + pos - 5, y - 5), (x + pos, y - 10), 
             (x + pos + 5, y - 5), (x + pos, y)],
            fill=(0, 200, 255, 200)
        )


class Thumbnail:

    def __init__(self):
        try:
            # Anime-style fonts
            self.title_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 42)
            self.regular_font = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 22)
            self.signature_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 24)
            self.small_font = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 18)
            self.anime_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 32)
            self.bot_font = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 28)
        except OSError:
            self.title_font = ImageFont.load_default()
            self.regular_font = ImageFont.load_default()
            self.signature_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()
            self.anime_font = ImageFont.load_default()
            self.bot_font = ImageFont.load_default()

    async def save_thumb(self, output_path: str, url: str):
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                with open(output_path, "wb") as f:
                    f.write(await resp.read())
        return output_path

    async def generate(self, song: Track, size=(1280, 720)) -> str:
        try:
            temp = f"cache/temp_{song.id}.jpg"
            output = f"cache/{song.id}_anime.png"
            if os.path.exists(output):
                return output
            await self.save_thumb(temp, song.thumbnail)
            return await asyncio.get_event_loop().run_in_executor(
                None, self._generate_sync, temp, output, song, size)
        except Exception as e:
            print(f"Error generating anime thumbnail: {e}")
            return config.DEFAULT_THUMB

    def _generate_sync(self, temp, output, song, size=(1280, 720)):
        try:
            W, H = size

            # ===== 1. ANIME BACKGROUND =====
            with Image.open(temp) as tmp:
                base = tmp.resize(size).convert("RGBA")

            # Dreamy blur effect (anime style)
            bg = base.filter(ImageFilter.GaussianBlur(35))
            bg = ImageEnhance.Brightness(bg).enhance(0.3)
            bg = ImageEnhance.Contrast(bg).enhance(1.3)
            bg = ImageEnhance.Color(bg).enhance(0.7)
            
            # Anime-style color overlay
            overlay = Image.new("RGBA", size, (0, 0, 0, 0))
            od = ImageDraw.Draw(overlay)
            
            # Gradient overlay - anime sunset style
            for i in range(H):
                ratio = i / H
                # Dark purple to transparent
                alpha = int(120 * (1 - ratio * 0.9))
                od.line(
                    [(0, i), (W, i)],
                    fill=(20, 5, 40, alpha)
                )
            
            # Pink overlay from bottom
            for i in range(H):
                ratio = i / H
                if ratio > 0.3:
                    alpha = int(60 * ((ratio - 0.3) / 0.7))
                    od.line(
                        [(0, i), (W, i)],
                        fill=(255, 100, 150, alpha)
                    )
            
            bg = Image.alpha_composite(bg, overlay)
            
            # Add anime pattern
            pattern = create_anime_pattern(W, H)
            bg = Image.alpha_composite(bg, pattern)

            draw = ImageDraw.Draw(bg)

            # ===== 2. ANIME GLASS PANEL =====
            panel = Image.new("RGBA", (PANEL_W, PANEL_H), (0, 0, 0, 0))
            pd = ImageDraw.Draw(panel)

            # Glow rings - anime style
            glow_colors = [
                (255, 150, 200, 40),   # Pink
                (0, 200, 255, 30),     # Cyan
                (180, 130, 255, 25),   # Purple
            ]
            for i, color in enumerate(glow_colors):
                spread = (i + 1) * 12
                pd.rounded_rectangle(
                    (0 - spread, 0 - spread, PANEL_W + spread, PANEL_H + spread),
                    radius=50 + spread,
                    outline=color,
                    width=2
                )

            # Main glass with anime tint
            pd.rounded_rectangle(
                (0, 0, PANEL_W - 1, PANEL_H - 1),
                radius=46,
                fill=(15, 5, 35, 180)  # Dark purple glass
            )
            
            # Animated border - gradient
            for i in range(3, PANEL_W - 3, 5):
                progress = i / PANEL_W
                r = int(200 + 55 * abs(math.sin(progress * math.pi * 2)))
                g = int(150 + 105 * abs(math.sin(progress * math.pi * 2 + 1)))
                b = int(255 * abs(math.sin(progress * math.pi * 2 + 2)))
                pd.rectangle(
                    (i, 2, i + 3, 4),
                    fill=(r, g, b, 180)
                )
                pd.rectangle(
                    (i, PANEL_H - 5, i + 3, PANEL_H - 2),
                    fill=(r, g, b, 180)
                )
            
            # Inner glow
            pd.rounded_rectangle(
                (4, 4, PANEL_W - 5, PANEL_H//2 + 30),
                radius=42,
                outline=(255, 255, 255, 12),
                width=1
            )

            pmask = Image.new("L", (PANEL_W, PANEL_H), 0)
            ImageDraw.Draw(pmask).rounded_rectangle(
                (0, 0, PANEL_W, PANEL_H), radius=46, fill=255)
            bg.paste(panel, (PANEL_X, PANEL_Y), pmask)
            draw = ImageDraw.Draw(bg)

            # ===== 3. ANIME THUMBNAIL WITH GLOW =====
            thumb = base.resize((THUMB_W, THUMB_H))
            
            # Rainbow glow frame
            glow_layer = Image.new("RGBA", size, (0, 0, 0, 0))
            gd = ImageDraw.Draw(glow_layer)
            
            for i in range(12, 0, -1):
                alpha = int(50 * (i / 12))
                color = (
                    int(255 * (i/12)),
                    int(150 * abs(math.sin(i * 0.5))),
                    int(200 * abs(math.sin(i * 0.3 + 1))),
                    alpha
                )
                gd.rounded_rectangle(
                    (THUMB_X - i, THUMB_Y - i,
                     THUMB_X + THUMB_W + i, THUMB_Y + THUMB_H + i),
                    radius=28 + i,
                    fill=color
                )
            bg = Image.alpha_composite(bg, glow_layer)
            draw = ImageDraw.Draw(bg)

            # Thumbnail with rounded corners
            tmask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(tmask).rounded_rectangle(
                (0, 0, THUMB_W, THUMB_H), radius=26, fill=255)
            bg.paste(thumb, (THUMB_X, THUMB_Y), tmask)

            # Anime-style border
            draw.rounded_rectangle(
                (THUMB_X, THUMB_Y, THUMB_X + THUMB_W, THUMB_Y + THUMB_H),
                radius=26, 
                outline=(255, 150, 200, 180), 
                width=3
            )
            
            # Second inner border
            draw.rounded_rectangle(
                (THUMB_X + 5, THUMB_Y + 5, 
                 THUMB_X + THUMB_W - 5, THUMB_Y + THUMB_H - 5),
                radius=22,
                outline=(0, 200, 255, 100),
                width=1
            )

            # ===== 4. ANIME TITLE WITH DECORATION =====
            # Decorative accent bar - anime style
            gradient_colors = [
                (255, 150, 200),
                (255, 100, 150),
                (0, 200, 255)
            ]
            for i, color in enumerate(gradient_colors):
                x_offset = i * 4
                draw.rounded_rectangle(
                    (TITLE_X + x_offset, TITLE_Y + 2, 
                     TITLE_X + x_offset + 4, TITLE_Y + 46),
                    radius=2,
                    fill=(color[0], color[1], color[2], 180)
                )

            # Anime-style title with glow
            clean_title = re.sub(r"\W+", " ", song.title).title()
            final_title = trim_to_width(clean_title, self.title_font, MAX_TITLE_WIDTH)
            
            # Glow effect
            for i in range(6, 0, -1):
                alpha = int(30 * (i / 6))
                draw.text(
                    (TITLE_X + 15 + i//2, TITLE_Y + 2 + i//2),
                    final_title,
                    fill=(0, 200, 255, alpha),
                    font=self.title_font
                )
            
            # Main title
            draw.text(
                (TITLE_X + 14, TITLE_Y + 1),
                final_title,
                fill=(255, 255, 255),
                font=self.title_font
            )
            
            # Subtitle glow
            draw.text(
                (TITLE_X + 13, TITLE_Y + 2),
                final_title,
                fill=(255, 150, 200, 60),
                font=self.title_font
            )

            # ===== 5. ANIME META INFO =====
            meta_text = f"✦  ᴀɴɪᴍᴇ ᴘʟᴀʏʟɪsᴛ  ✦  ʏᴏᴜᴛᴜʙᴇ  ✦  {song.view_count or 'ᴜɴᴋɴᴏᴡɴ ᴠɪᴇᴡs'}"
            
            # Meta info with anime style
            draw.text(
                (TITLE_X + 14, META_Y),
                meta_text,
                fill=(180, 130, 255, 220),
                font=self.regular_font
            )
            
            # Small anime decorative element
            draw_anime_divider(draw, TITLE_X + 14, META_Y + 30, 120)

            # ===== 6. ANIME PROGRESS BAR =====
            # Background with anime glow
            draw.rounded_rectangle(
                (BAR_X, BAR_Y - 5, BAR_X + BAR_TOTAL_LEN, BAR_Y + 5),
                radius=10,
                fill=(30, 10, 50)
            )
            
            # Progress with gradient
            for i in range(BAR_RED_LEN):
                progress = i / BAR_RED_LEN
                r = int(255 * progress)
                g = int(150 + 105 * (1 - progress))
                b = int(200 * (1 - progress))
                draw.line(
                    [(BAR_X + i, BAR_Y - 4), (BAR_X + i, BAR_Y + 4)],
                    fill=(r, g, b, 200)
                )
            
            # Glow behind knob
            for i in range(10, 0, -1):
                alpha = int(80 * (i / 10))
                draw.ellipse(
                    (BAR_X + BAR_RED_LEN - 12 - i, BAR_Y - 12 - i,
                     BAR_X + BAR_RED_LEN + 12 + i, BAR_Y + 12 + i),
                    fill=(255, 150, 200, alpha)
                )
            
            # Anime-style knob
            draw.ellipse(
                (BAR_X + BAR_RED_LEN - 10, BAR_Y - 10,
                 BAR_X + BAR_RED_LEN + 10, BAR_Y + 10),
                fill=(255, 150, 200)
            )
            draw.ellipse(
                (BAR_X + BAR_RED_LEN - 5, BAR_Y - 5,
                 BAR_X + BAR_RED_LEN + 5, BAR_Y + 5),
                fill=(255, 255, 255)
            )
            
            # Sparkle on knob
            for angle in [0, 90, 180, 270]:
                rad = math.radians(angle)
                sx = BAR_X + BAR_RED_LEN + int(14 * math.cos(rad))
                sy = BAR_Y + int(14 * math.sin(rad))
                draw.line(
                    [(sx - 3, sy), (sx + 3, sy)],
                    fill=(255, 255, 255, 150),
                    width=1
                )
                draw.line(
                    [(sx, sy - 3), (sx, sy + 3)],
                    fill=(255, 255, 255, 150),
                    width=1
                )

            # Time stamps with anime style
            draw.text(
                (BAR_X, BAR_Y + 18),
                "◈ 00:00",
                fill=(200, 180, 220),
                font=self.small_font
            )
            
            is_live = getattr(song, "is_live", False)
            end_text = "✦ ʟɪᴠᴇ ✦" if is_live else f"◈ {song.duration}"
            tw = self.small_font.getlength(end_text)
            draw.text(
                (BAR_X + BAR_TOTAL_LEN - tw, BAR_Y + 18),
                end_text,
                fill=(255, 150, 200) if is_live else (200, 180, 220),
                font=self.small_font
            )

            # ===== 7. BOT WATERMARK =====
            watermark_text = f"✦ {BOT_NAME} ✦"
            
            ww = self.bot_font.getlength(watermark_text)
            wh = self.bot_font.getbbox(watermark_text)[3] - self.bot_font.getbbox(watermark_text)[1]
            
            wm_x = PANEL_X + PANEL_W - ww - 25
            wm_y = PANEL_Y + PANEL_H - wh - 15
            
            # Anime glow watermark
            for i in range(8, 0, -1):
                alpha = int(50 * (i / 8))
                draw.text(
                    (wm_x + i//2, wm_y + i//2),
                    watermark_text,
                    fill=(255, 150, 200, alpha),
                    font=self.bot_font
                )
            
            # Main watermark
            draw.text(
                (wm_x, wm_y),
                watermark_text,
                fill=(255, 200, 220, 230),
                font=self.bot_font
            )
            
            # Secondary glow
            draw.text(
                (wm_x - 1, wm_y - 1),
                watermark_text,
                fill=(0, 200, 255, 50),
                font=self.bot_font
            )

            # ===== 8. ANIME DECORATIVE ELEMENTS =====
            # Small sakura flowers at corners
            for corner in [(PANEL_X + 15, PANEL_Y + 15),
                          (PANEL_X + PANEL_W - 15, PANEL_Y + 15),
                          (PANEL_X + 15, PANEL_Y + PANEL_H - 15),
                          (PANEL_X + PANEL_W - 15, PANEL_Y + PANEL_H - 15)]:
                for i in range(5):
                    angle = (i / 5) * 2 * math.pi
                    px = corner[0] + int(12 * math.cos(angle))
                    py = corner[1] + int(12 * math.sin(angle))
                    draw.ellipse(
                        (px - 3, py - 3, px + 3, py + 3),
                        fill=(255, 150, 200, 80)
                    )

            bg.save(output)
            try:
                os.remove(temp)
            except OSError:
                pass
            return output

        except Exception as e:
            print(f"Error in anime thumbnail generation: {e}")
            return config.DEFAULT_THUMB
