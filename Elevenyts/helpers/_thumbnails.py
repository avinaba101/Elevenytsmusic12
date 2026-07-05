# Copyright (c) 2025 AnonymousX1025
# Licensed under the MIT License.
# This file is part of AnonXMusic
#
# Modified for Elevenyts Project
# Changes: Custom UI with glassmorphism, neon effects, and premium styling

import os
import asyncio
import aiohttp
from PIL import (
    Image, ImageDraw, ImageEnhance,
    ImageFilter, ImageFont, ImageOps
)


# =========================
# CONFIGURATION
# =========================

W, H = 1280, 720
CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

BOT_NAME = "𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬"

# Premium Colors
GOLD = (255, 196, 80)
CYAN = (0, 220, 255)
PURPLE = (170, 90, 255)
WHITE = (255, 255, 255)
DARK = (10, 10, 18)

# Default thumbnail fallback (create a default image if needed)
DEFAULT_THUMB = None


# =========================
# HELPER FUNCTIONS
# =========================

def safe_text(text, fallback="Unknown"):
    """Safely get text or return fallback"""
    return text if text else fallback


def fit_text(font, text, max_width):
    """Truncate text with ellipsis if too long"""
    if font.getlength(text) <= max_width:
        return text
    for i in range(len(text), 0, -1):
        if font.getlength(text[:i] + "…") <= max_width:
            return text[:i] + "…"
    return "…"


def format_views(views):
    """Format view count to K/M format"""
    try:
        views = int(views)
        if views >= 1_000_000:
            return f"{views//1_000_000}M"
        elif views >= 1_000:
            return f"{views//1_000}K"
        return str(views)
    except:
        return "0"


# =========================
# TRACK CLASS (Mock if not available)
# =========================

class Track:
    """Simple Track class for compatibility"""
    def __init__(self, id, title, thumbnail, channel_name, view_count, duration):
        self.id = id
        self.title = title
        self.thumbnail = thumbnail
        self.channel_name = channel_name
        self.view_count = view_count
        self.duration = duration


# =========================
# MAIN THUMBNAIL CLASS
# =========================

class Thumbnail:
    """
    Premium Thumbnail Generator with Glassmorphism Design
    Original: Copyright (c) 2025 AnonymousX1025 (MIT License)
    """

    def __init__(self):
        self.session = None
        self.rect = (914, 514)
        self.fill = WHITE
        self.mask = Image.new("L", self.rect, 0)
        
        # Try to load custom fonts, fallback to default
        try:
            self.font_title = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 50
            )
            self.font_sub = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 26
            )
            self.font_small = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 20
            )
            # Also keep old fonts for compatibility
            self.font1 = ImageFont.truetype(
                "Elevenyts/helpers/Raleway-Bold.ttf", 30
            )
            self.font2 = ImageFont.truetype(
                "Elevenyts/helpers/Inter-Light.ttf", 30
            )
        except:
            print("⚠️ Custom fonts not found, using default fonts")
            self.font_title = ImageFont.load_default()
            self.font_sub = ImageFont.load_default()
            self.font_small = ImageFont.load_default()
            self.font1 = ImageFont.load_default()
            self.font2 = ImageFont.load_default()

    async def start(self) -> None:
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()

    async def close(self) -> None:
        """Close HTTP session"""
        if self.session:
            await self.session.close()

    async def save_thumb(self, output_path: str, url: str) -> str:
        """Download thumbnail from URL"""
        if not self.session:
            await self.start()
        
        async with self.session.get(url) as resp:
            with open(output_path, "wb") as f:
                f.write(await resp.read())
        return output_path

    # ========================================
    # ORIGINAL GENERATE METHOD (Kept for compatibility)
    # ========================================
    
    async def generate_original(self, song, size=(1280, 720)) -> str:
        """Original AnonXMusic style thumbnail"""
        try:
            temp = f"{CACHE_DIR}/temp_{song.id}.jpg"
            output = f"{CACHE_DIR}/{song.id}_original.png"
            
            if os.path.exists(output):
                return output

            # Download thumbnail
            if not self.session:
                await self.start()
            await self.save_thumb(temp, song.thumbnail)
            
            # Process image
            thumb = Image.open(temp).convert("RGBA").resize(
                size, Image.Resampling.LANCZOS
            )
            blur = thumb.filter(ImageFilter.GaussianBlur(25))
            image = ImageEnhance.Brightness(blur).enhance(0.40)

            # Create rounded rectangle
            _rect = ImageOps.fit(
                thumb, self.rect,
                method=Image.LANCZOS,
                centering=(0.5, 0.5)
            )
            
            # Reset mask for each generation
            self.mask = Image.new("L", self.rect, 0)
            ImageDraw.Draw(self.mask).rounded_rectangle(
                (0, 0, self.rect[0], self.rect[1]),
                radius=15,
                fill=255
            )
            _rect.putalpha(self.mask)
            image.paste(_rect, (183, 30), _rect)

            # Add text
            draw = ImageDraw.Draw(image)
            
            # Channel name and views
            channel = safe_text(song.channel_name, "Unknown Channel")[:25]
            views = format_views(getattr(song, "view_count", 0))
            draw.text(
                (50, 560),
                f"{channel} | {views} views",
                font=self.font2,
                fill=self.fill
            )
            
            # Title
            title = safe_text(song.title, "Unknown Track")[:50]
            draw.text((50, 600), title, font=self.font1, fill=self.fill)
            
            # Duration and progress
            draw.text((40, 650), "0:01", font=self.font1)
            draw.line(
                [(140, 670), (1160, 670)],
                fill=self.fill,
                width=5,
                joint="curve"
            )
            
            duration = safe_text(getattr(song, "duration", "0:00"))
            draw.text((1185, 650), duration, font=self.font1, fill=self.fill)

            image.save(output)
            try:
                os.remove(temp)
            except:
                pass
            
            return output
            
        except Exception as e:
            print(f"❌ Original thumbnail error: {e}")
            return DEFAULT_THUMB

    # ========================================
    # NEW PREMIUM GENERATE METHOD (Your Design)
    # ========================================

    async def generate(self, song, size=(1280, 720)) -> str:
        """Generate premium thumbnail with glassmorphism design"""
        try:
            # Use a different output name to avoid conflicts
            output = f"{CACHE_DIR}/{song.id}_premium.png"
            if os.path.exists(output):
                return output

            temp = f"{CACHE_DIR}/temp_{song.id}.jpg"
            
            # Get thumbnail URL
            url = getattr(song, "thumbnail", None)
            if not url:
                url = f"https://img.youtube.com/vi/{song.id}/maxresdefault.jpg"

            # Download thumbnail
            if not self.session:
                await self.start()
            await self.save_thumb(temp, url)

            # Run rendering in thread pool
            return await asyncio.get_event_loop().run_in_executor(
                None, self._render_premium, temp, output, song
            )

        except Exception as e:
            print(f"❌ Premium thumbnail error: {e}")
            # Fallback to original style
            return await self.generate_original(song)

    # ========================================
    # PREMIUM RENDER ENGINE
    # ========================================

    def _render_premium(self, temp, output, song):
        """Render premium glassmorphism thumbnail"""
        try:
            # Open and resize image
            img = Image.open(temp).convert("RGBA").resize((W, H))

            # ====== BACKGROUND ======
            bg = img.filter(ImageFilter.GaussianBlur(40))
            bg = ImageEnhance.Brightness(bg).enhance(0.25)
            bg = ImageEnhance.Contrast(bg).enhance(1.3)

            # Dark overlay
            overlay = Image.new("RGBA", (W, H), (0, 0, 0, 170))
            bg = Image.alpha_composite(bg, overlay)

            draw = ImageDraw.Draw(bg)

            # ====== GLASS PANEL ======
            px, py = 90, 60
            pw, ph = 1100, 600

            draw.rounded_rectangle(
                (px, py, px + pw, py + ph),
                radius=45,
                fill=(18, 18, 28, 220),
                outline=CYAN,
                width=2
            )

            # ====== THUMBNAIL ======
            thumb = img.resize((920, 420))
            tx, ty = px + 90, py + 40

            # Rounded corners
            mask = Image.new("L", thumb.size, 0)
            ImageDraw.Draw(mask).rounded_rectangle(
                (0, 0, 920, 420),
                radius=30,
                fill=255
            )

            bg.paste(thumb, (tx, ty), mask)

            # Neon border
            draw.rounded_rectangle(
                (tx - 3, ty - 3, tx + 920 + 3, ty + 420 + 3),
                radius=35,
                outline=PURPLE,
                width=2
            )

            # ====== TITLE ======
            title = safe_text(getattr(song, "title", "Unknown Track"))
            title = fit_text(self.font_title, title, 850)

            # Main title
            draw.text(
                (tx, ty + 440),
                title,
                font=self.font_title,
                fill=WHITE
            )

            # Shadow
            draw.text(
                (tx + 2, ty + 442),
                title,
                font=self.font_title,
                fill=(0, 0, 0, 120)
            )

            # ====== META INFO ======
            views = format_views(getattr(song, "view_count", 0))
            channel = safe_text(getattr(song, "channel_name", "Unknown"), "Unknown")[:20]

            meta = f"▶ {views} views   •   {channel}   •   {BOT_NAME}"
            draw.text(
                (tx, ty + 505),
                meta,
                font=self.font_sub,
                fill=GOLD
            )

            # ====== PROGRESS BAR ======
            bx, by = tx, ty + 555
            bw = 880

            # Background track
            draw.rounded_rectangle(
                (bx, by, bx + bw, by + 10),
                radius=10,
                fill=(40, 40, 60)
            )

            # Progress (55%)
            progress = 0.55
            fill_width = int(bw * progress)

            # Cyan progress
            for i in range(fill_width):
                draw.line(
                    (bx + i, by, bx + i, by + 10),
                    fill=CYAN
                )

            # Purple knob
            draw.ellipse(
                (bx + fill_width - 10, by - 6,
                 bx + fill_width + 10, by + 16),
                fill=PURPLE
            )

            # ====== DURATION ======
            duration = safe_text(getattr(song, "duration", "0:00"))
            draw.text(
                (bx + bw - 100, by - 5),
                duration,
                font=self.font_small,
                fill=(200, 200, 200)
            )

            # Save
            bg.save(output)
            try:
                os.remove(temp)
            except:
                pass

            return output

        except Exception as e:
            print(f"❌ Render error: {e}")
            return None


# ========================================
# CONVENIENCE FUNCTIONS
# ========================================

async def generate_thumbnail(song, premium=True):
    """
    Generate thumbnail for a song
    
    Args:
        song: Track object
        premium: If True, use premium design, else original
    
    Returns:
        Path to generated thumbnail
    """
    thumb = Thumbnail()
    await thumb.start()
    
    if premium:
        result = await thumb.generate(song)
    else:
        result = await thumb.generate_original(song)
    
    await thumb.close()
    return result


# ========================================
# TEST CODE (Remove in production)
# ========================================

if __name__ == "__main__":
    # Test the thumbnail generator
    async def test():
        song = Track(
            id="dQw4w9WgXcQ",
            title="Never Gonna Give You Up",
            thumbnail="https://img.youtube.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
            channel_name="Rick Astley",
            view_count="1500000000",
            duration="3:33"
        )
        
        # Test premium
        result = await generate_thumbnail(song, premium=True)
        print(f"✅ Premium thumbnail saved: {result}")
        
        # Test original
        result = await generate_thumbnail(song, premium=False)
        print(f"✅ Original thumbnail saved: {result}")
    
    asyncio.run(test())
