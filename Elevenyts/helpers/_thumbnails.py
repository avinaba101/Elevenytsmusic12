import os
import asyncio
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

# ==========================================================
# CONFIG
# ==========================================================

W, H = 1280, 720
CACHE = "cache"
os.makedirs(CACHE, exist_ok=True)

BOT_NAME = "𝓕𝓾𝓼𝓱𝓲𝓰𝓾𝓻𝓸X𝓜𝓾𝓼𝓲𝓬"

GOLD = (255, 200, 80)
CYAN = (0, 220, 255)
PURPLE = (170, 90, 255)

# ==========================================================
# HELPERS
# ==========================================================

def safe(txt, fallback="Unknown"):
    return txt if txt else fallback


def fit_text(font, text, max_w):
    if font.getlength(text) <= max_w:
        return text
    for i in range(len(text), 0, -1):
        if font.getlength(text[:i] + "…") <= max_w:
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


def format_time(sec):
    try:
        sec = int(sec)
        return f"{sec//60:02d}:{sec%60:02d}"
    except:
        return "00:00"


# ==========================================================
# YOUTUBE DATA (REAL METADATA OPTIONAL)
# ==========================================================

async def fetch_youtube_data(video_id, api_key=None):
    """
    Real YouTube data fetch (optional)
    If API key not provided → fallback safe mode
    """
    if not api_key:
        return None

    url = (
        "https://www.googleapis.com/youtube/v3/videos"
        f"?part=snippet,statistics,contentDetails&id={video_id}&key={api_key}"
    )

    try:
        async with aiohttp.ClientSession() as s:
            async with s.get(url) as r:
                data = await r.json()
                if "items" in data and data["items"]:
                    item = data["items"][0]

                    return {
                        "title": item["snippet"]["title"],
                        "views": item["statistics"].get("viewCount", "0"),
                        "duration": item["contentDetails"].get("duration", "0")
                    }
    except:
        return None

    return None


# ==========================================================
# THUMBNAIL ENGINE
# ==========================================================

class ThumbnailEngine:

    def __init__(self):
        try:
            self.title_font = ImageFont.truetype("Elevenyts/helpers/Raleway-Bold.ttf", 48)
            self.sub_font = ImageFont.truetype("Elevenyts/helpers/Inter-Light.ttf", 26)
            self.small_font = ImageFont.truetype("Elevenyts/helpers/Inter-Light.ttf", 20)
        except:
            self.title_font = ImageFont.load_default()
            self.sub_font = ImageFont.load_default()
            self.small_font = ImageFont.load_default()

    # ---------------- DOWNLOAD ----------------
    async def download(self, url, path):
        try:
            async with aiohttp.ClientSession() as s:
                async with s.get(url) as r:
                    if r.status == 200:
                        open(path, "wb").write(await r.read())
                        return True
        except:
            return False

    # ---------------- MAIN ----------------
    async def generate(self, song, api_key=None):

        out = f"{CACHE}/{song.id}.png"
        if os.path.exists(out):
            return out

        temp = f"{CACHE}/t_{song.id}.jpg"

        url = getattr(song, "thumbnail", None) or \
              f"https://img.youtube.com/vi/{song.id}/maxresdefault.jpg"

        ok = await self.download(url, temp)
        if not ok:
            return None

        yt_data = await fetch_youtube_data(song.id, api_key)

        return await asyncio.get_event_loop().run_in_executor(
            None, self.render, temp, out, song, yt_data
        )

    # ---------------- RENDER ----------------
    def render(self, temp, out, song, yt):

        img = Image.open(temp).convert("RGBA").resize((W, H))

        # background cinematic blur
        bg = img.filter(ImageFilter.GaussianBlur(35))
        bg = ImageEnhance.Brightness(bg).enhance(0.25)

        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 170))
        bg = Image.alpha_composite(bg, overlay)

        d = ImageDraw.Draw(bg)

        # ================= PANEL =================
        px, py = 90, 60
        pw, ph = 1100, 600

        d.rounded_rectangle(
            (px, py, px+pw, py+ph),
            radius=40,
            fill=(18,18,28,220),
            outline=CYAN,
            width=2
        )

        # ================= THUMB =================
        thumb = img.resize((920, 420))
        tx, ty = px+90, py+40

        mask = Image.new("L", thumb.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle((0,0,920,420), radius=30, fill=255)

        bg.paste(thumb, (tx, ty), mask)

        d.rounded_rectangle((tx-3, ty-3, tx+920+3, ty+420+3),
                            radius=35, outline=PURPLE, width=2)

        # ================= REAL DATA =================

        title = safe(getattr(song, "title", "Unknown Track"))
        views = "0"

        if yt:
            title = yt.get("title", title)
            views = yt.get("views", "0")
        else:
            views = getattr(song, "view_count", "0")

        title = fit_text(self.title_font, title, 850)

        # title
        d.text((tx, ty+440), title, font=self.title_font, fill=(255,255,255))

        # views + bot
        meta = f"▶ {format_views(views)}   •   {BOT_NAME}"
        d.text((tx, ty+500), meta, font=self.sub_font, fill=GOLD)

        # ================= PROGRESS =================
        bx, by = tx, ty+555
        bw = 880

        d.rounded_rectangle((bx,by,bx+bw,by+10), radius=10, fill=(50,50,70))

        progress = 0.6
        fill = int(bw * progress)

        for i in range(fill):
            d.line((bx+i, by, bx+i, by+10), fill=CYAN)

        d.ellipse((bx+fill-10, by-6, bx+fill+10, by+16), fill=PURPLE)

        d.text((bx, by+18), "00:00", font=self.small_font, fill=(200,200,200))
        d.text((bx+bw-60, by+18), "LIVE" if getattr(song,"is_live",False) else "04:00",
               font=self.small_font, fill=GOLD)

        # save
        bg.save(out)
        os.remove(temp)

        return out
