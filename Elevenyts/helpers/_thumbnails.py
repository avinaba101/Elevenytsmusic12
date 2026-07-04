import os
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# =========================
# CONFIG
# =========================

W, H = 1280, 720
CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)

BOT_NAME = "𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬"

# Premium Colors
GOLD = (255, 196, 80)
CYAN = (0, 220, 255)
PURPLE = (170, 90, 255)
DARK = (10, 10, 18)


# =========================
# HELPERS
# =========================

def safe(text, fallback="Unknown"):
    return text if text else fallback


def fit_text(font, text, max_width):
    if font.getlength(text) <= max_width:
        return text
    for i in range(len(text), 0, -1):
        if font.getlength(text[:i] + "…") <= max_width:
            return text[:i] + "…"
    return "…"


def format_views(v):
    try:
        v = int(v)
        if v >= 1_000_000:
            return f"{v//1_000_000}M views"
        elif v >= 1_000:
            return f"{v//1_000}K views"
        return f"{v} views"
    except:
        return "0 views"


# =========================
# THUMBNAIL CLASS (IMPORTANT NAME FIX)
# =========================

class Thumbnail:

    def __init__(self):
        try:
            self.title_font = ImageFont.truetype("Elevenyts/helpers/Raleway-Bold.ttf", 50)
            self.sub_font = ImageFont.truetype("Elevenyts/helpers/Inter-Light.ttf", 26)
            self.small_font = ImageFont.truetype("Elevenyts/helpers/Inter-Light.ttf", 20)
        except:
            self.title_font = ImageFont.load_default()
            self.sub_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

    # =========================
    # DOWNLOAD THUMB
    # =========================
    async def download(self, url, path):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as r:
                    if r.status == 200:
                        open(path, "wb").write(await r.read())
                        return True
        except:
            return False

    # =========================
    # MAIN GENERATE FUNCTION
    # =========================
    async def generate(self, song):

        out = f"{CACHE}/{song.id}.png"
        if os.path.exists(out):
            return out

        temp = f"{CACHE}/t_{song.id}.jpg"

        url = getattr(song, "thumbnail", None) or \
              f"https://img.youtube.com/vi/{song.id}/maxresdefault.jpg"

        ok = await self.download(url, temp)
        if not ok:
            return None

        return await asyncio.get_event_loop().run_in_executor(
            None, self.render, temp, out, song
        )

    # =========================
    # RENDER ENGINE (UI CORE)
    # =========================
    def render(self, temp, out, song):

        img = Image.open(temp).convert("RGBA").resize((W, H))

        # ================= BACKGROUND =================
        bg = img.filter(ImageFilter.GaussianBlur(40))
        bg = ImageEnhance.Brightness(bg).enhance(0.25)
        bg = ImageEnhance.Contrast(bg).enhance(1.3)

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 170))
        bg = Image.alpha_composite(bg, overlay)

        draw = ImageDraw.Draw(bg)

        # ================= GLASS PANEL =================
        px, py = 90, 60
        pw, ph = 1100, 600

        draw.rounded_rectangle(
            (px, py, px+pw, py+ph),
            radius=45,
            fill=(18, 18, 28, 220),
            outline=CYAN,
            width=2
        )

        # ================= THUMBNAIL =================
        thumb = img.resize((920, 420))
        tx, ty = px + 90, py + 40

        mask = Image.new("L", thumb.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle(
            (0, 0, 920, 420),
            radius=30,
            fill=255
        )

        bg.paste(thumb, (tx, ty), mask)

        # Neon border
        draw.rounded_rectangle(
            (tx-3, ty-3, tx+920+3, ty+420+3),
            radius=35,
            outline=PURPLE,
            width=2
        )

        # ================= TITLE =================
        title = safe(getattr(song, "title", "Unknown Track"))
        title = fit_text(self.title_font, title, 850)

        draw.text(
            (tx, ty + 440),
            title,
            font=self.title_font,
            fill=(255, 255, 255)
        )

        # shadow
        draw.text(
            (tx+2, ty + 442),
            title,
            font=self.title_font,
            fill=(0, 0, 0, 120)
        )

        # ================= META =================
        views = format_views(getattr(song, "view_count", 0))

        meta = f"▶ {views}   •   {BOT_NAME}"

        draw.text(
            (tx, ty + 505),
            meta,
            font=self.sub_font,
            fill=GOLD
        )

        # ================= PROGRESS BAR =================
        bx, by = tx, ty + 555
        bw = 880

        draw.rounded_rectangle(
            (bx, by, bx + bw, by + 10),
            radius=10,
            fill=(40, 40, 60)
        )

        progress = 0.55
        fill = int(bw * progress)

        for i in range(fill):
            draw.line(
                (bx + i, by, bx + i, by + 10),
                fill=CYAN
            )

        draw.ellipse(
            (bx + fill - 10, by - 6, bx + fill + 10, by + 16),
            fill=PURPLE
        )

        # ================= SAVE =================
        bg.save(out)
        os.remove(temp)

        return out
