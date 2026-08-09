from pathlib import Path
from PIL import Image, ImageDraw, ImageFilter

out_dir = Path(__file__).resolve().parent
out_dir.mkdir(parents=True, exist_ok=True)


def create_banner(path, color_a, color_b, accent):
    img = Image.new("RGB", (800, 600), "#f8fafc")
    pixels = []
    for y in range(600):
        t = y / 599
        r = int(color_a[0] * (1 - t) + color_b[0] * t)
        g = int(color_a[1] * (1 - t) + color_b[1] * t)
        b = int(color_a[2] * (1 - t) + color_b[2] * t)
        pixels.append((r, g, b))
    img.putdata(pixels)

    draw = ImageDraw.Draw(img)
    for x, y, radius in [(120, 80, 120), (650, 120, 100), (140, 420, 140), (640, 450, 110)]:
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=accent + (35,))

    panel = Image.new("RGB", (560, 360), "#ffffff")
    panel_draw = ImageDraw.Draw(panel)
    panel_draw.rounded_rectangle((20, 20, 540, 340), radius=28, fill="#ffffff", outline="#e2e8f0", width=3)
    panel = panel.filter(ImageFilter.GaussianBlur(radius=0.6))
    img.paste(panel, (120, 120))

    base = Image.new("RGB", (560, 360), "#ffffff")
    base_draw = ImageDraw.Draw(base)
    base_draw.rounded_rectangle((20, 20, 540, 340), radius=28, fill="#ffffff", outline="#e2e8f0", width=3)

    if path.name.startswith("fashion"):
        base_draw.ellipse((180, 120, 370, 320), fill="#fef2f2")
        base_draw.ellipse((210, 150, 340, 280), fill="#fde68a")
        base_draw.rectangle((200, 235, 340, 320), fill="#f3f4f6")
        base_draw.rectangle((220, 190, 320, 240), fill="#f9fafb")
        base_draw.line((200, 305, 180, 360), fill="#d1d5db", width=6)
        base_draw.line((340, 305, 360, 360), fill="#d1d5db", width=6)
    elif path.name.startswith("home"):
        base_draw.rounded_rectangle((180, 140, 420, 360), radius=24, fill="#f8fafc", outline="#dbeafe", width=3)
        base_draw.rectangle((210, 170, 390, 330), fill="#ffffff")
        base_draw.rectangle((225, 190, 375, 260), fill="#f1f5f9")
        base_draw.ellipse((255, 285, 300, 330), fill="#e2e8f0")
        base_draw.ellipse((310, 285, 355, 330), fill="#e2e8f0")
    elif path.name.startswith("electronics"):
        base_draw.rounded_rectangle((180, 140, 420, 360), radius=24, fill="#f8fafc", outline="#bfdbfe", width=3)
        base_draw.rounded_rectangle((215, 180, 390, 330), radius=18, fill="#0f172a", outline="#334155", width=2)
        base_draw.rectangle((240, 205, 365, 305), fill="#1e293b")
        base_draw.ellipse((270, 225, 295, 250), fill="#60a5fa")
        base_draw.ellipse((325, 225, 350, 250), fill="#60a5fa")
    elif path.name.startswith("beauty"):
        base_draw.ellipse((180, 130, 420, 360), fill="#fdf2f8")
        base_draw.ellipse((220, 170, 380, 320), fill="#f5f3ff")
        base_draw.rounded_rectangle((220, 200, 380, 340), radius=20, fill="#ffffff", outline="#e9d5ff", width=3)
        base_draw.ellipse((250, 215, 350, 315), fill="#fdf2f8")
    elif path.name.startswith("sports"):
        base_draw.rounded_rectangle((180, 140, 420, 360), radius=24, fill="#f8fafc", outline="#bfdbfe", width=3)
        base_draw.arc((230, 185, 370, 330), 0, 180, fill="#3b82f6", width=8)
        base_draw.line((260, 240, 260, 320), fill="#3b82f6", width=6)
        base_draw.line((340, 240, 340, 320), fill="#3b82f6", width=6)
    else:
        base_draw.rounded_rectangle((180, 140, 420, 360), radius=24, fill="#f8fafc", outline="#c7d2fe", width=3)
        base_draw.ellipse((215, 220, 285, 290), fill="#e2e8f0")
        base_draw.ellipse((315, 220, 385, 290), fill="#e2e8f0")
        base_draw.rectangle((230, 290, 370, 325), fill="#e2e8f0")

    img.paste(base, (120, 120))

    overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle((0, 0, 800, 180), fill=(255, 255, 255, 70))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    img.save(path, quality=95)


for filename, color_a, color_b, accent in [
    ("fashion.jpg", (248, 248, 250), (255, 236, 241), (255, 255, 255)),
    ("home.jpg", (247, 244, 240), (237, 242, 255), (255, 255, 255)),
    ("electronics.jpg", (245, 247, 250), (224, 239, 254), (255, 255, 255)),
    ("beauty.jpg", (255, 245, 247), (250, 245, 255), (255, 255, 255)),
    ("sports.jpg", (246, 247, 255), (233, 246, 255), (255, 255, 255)),
    ("accessories.jpg", (248, 250, 252), (229, 246, 255), (255, 255, 255)),
]:
    create_banner(out_dir / filename, color_a, color_b, accent)

print(f"Created {len(list(out_dir.glob('*.jpg')))} realistic placeholder images in {out_dir}")
