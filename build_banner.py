"""
Build animated terminal banners (dark.svg and light.svg) adhering strictly to the
GitHub Profile Master Prompt specification.

Terminal Dimensions: 1180x610
Title: profile.sh --live
Left: ~38% portrait frame labelled VISUAL.MAP
Right: SYSTEM.INFO readout with computed dotted leaders, pulsing red LIVE badge, handle pill.
Palette:
  Portrait: #A78BFA (dark) / #7C3AED (light)
  UI Chrome: #22D3EE (dark) / #0891B2 (light)
  Accent: #10B981
  Background: #0A101F (dark) / #F8FAFC (light)
"""

import os
import math
import html
import numpy as np
from PIL import Image, ImageOps, ImageFilter, ImageDraw
import xml.etree.ElementTree as ET

def create_sample_avatar(width=280, height=340):
    """
    Fallback artistic high-tech head-and-shoulders silhouette
    if no external user photo is found.
    """
    img = Image.new("L", (width, height), color=0)
    draw = ImageDraw.Draw(img)

    cx, cy = width // 2, 130
    draw.ellipse([cx - 58, cy - 75, cx + 58, cy + 65], fill=195)
    draw.polygon([(cx - 45, cy + 30), (cx + 45, cy + 30), (cx, cy + 85)], fill=180)
    draw.rectangle([cx - 28, cy + 65, cx + 28, cy + 130], fill=150)
    draw.ellipse([cx - 135, cy + 115, cx + 135, cy + 310], fill=135)
    draw.ellipse([cx - 62, cy - 88, cx + 62, cy - 10], fill=80)
    draw.rectangle([cx - 38, cy - 15, cx - 12, cy - 8], fill=40)
    draw.rectangle([cx + 12, cy - 15, cx + 38, cy - 8], fill=40)
    draw.line([(cx, cy - 5), (cx - 4, cy + 22), (cx + 4, cy + 22)], fill=90, width=2)
    draw.line([(cx - 18, cy + 42), (cx + 18, cy + 42)], fill=60, width=3)
    return img

def process_portrait(image_path=None, grid_w=280, grid_h=340, dark_mode=True):
    """
    Implements Floyd-Steinberg dithering in serpentine order
    with contrast, autocontrast and unsharp mask per Master Prompt spec:
    - 280x340 grid
    - Contrast 1.3x only, autocontrast(cutoff=1), UnsharpMask(radius=3, percent=140)
    - 1-bit Floyd-Steinberg dither, serpentine order
    - Runs of dots as <path> with crispEdges
    """
    if image_path and os.path.exists(image_path):
        raw_img = Image.open(image_path).convert("L")
        # Crop head-and-shoulders preserving aspect ratio
        img = ImageOps.fit(raw_img, (grid_w, grid_h), centering=(0.5, 0.35))
    else:
        img = create_sample_avatar(grid_w, grid_h)

    # Autocontrast(cutoff=1)
    img = ImageOps.autocontrast(img, cutoff=1)
    # Contrast 1.3x
    lut = [min(255, max(0, int(128 + 1.3 * (i - 128)))) for i in range(256)]
    img = img.point(lut)
    # UnsharpMask(radius=3, percent=140)
    img = img.filter(ImageFilter.UnsharpMask(radius=3, percent=140))

    arr = np.array(img, dtype=float)

    # In dark mode: lit pixels drawn on dark panel
    if not dark_mode:
        arr = 255.0 - arr

    # Serpentine Floyd-Steinberg dithering
    output_bits = np.zeros((grid_h, grid_w), dtype=np.uint8)
    h, w = arr.shape

    for y in range(h):
        is_even = (y % 2 == 0)
        x_range = range(w) if is_even else range(w - 1, -1, -1)
        for x in x_range:
            old_val = arr[y, x]
            new_val = 255.0 if old_val > 127.5 else 0.0
            output_bits[y, x] = 1 if new_val == 255.0 else 0
            err = old_val - new_val

            if is_even:
                if x + 1 < w:
                    arr[y, x + 1] += err * (7.0 / 16.0)
                if y + 1 < h:
                    if x - 1 >= 0:
                        arr[y + 1, x - 1] += err * (3.0 / 16.0)
                    arr[y + 1, x] += err * (5.0 / 16.0)
                    if x + 1 < w:
                        arr[y + 1, x + 1] += err * (1.0 / 16.0)
            else:
                if x - 1 >= 0:
                    arr[y, x - 1] += err * (7.0 / 16.0)
                if y + 1 < h:
                    if x + 1 < w:
                        arr[y + 1, x + 1] += err * (3.0 / 16.0)
                    arr[y + 1, x] += err * (5.0 / 16.0)
                    if x - 1 >= 0:
                        arr[y + 1, x - 1] += err * (1.0 / 16.0)

    return output_bits

def bits_to_svg_paths(bits, origin_x=65, origin_y=118, scale_x=1.32, scale_y=1.28):
    """
    Compresses consecutive horizontal dot runs into efficient SVG <path> d strings
    with crispEdges rendering to avoid font-glyph mushing.
    """
    h, w = bits.shape
    path_segments = []

    for y in range(h):
        run_start = None
        for x in range(w):
            if bits[y, x] == 1:
                if run_start is None:
                    run_start = x
            else:
                if run_start is not None:
                    sx = origin_x + run_start * scale_x
                    sy = origin_y + y * scale_y
                    rlen = (x - run_start) * scale_x
                    path_segments.append(f"M{sx:.1f} {sy:.1f}h{rlen:.1f}v{scale_y:.1f}h-{rlen:.1f}z")
                    run_start = None
        if run_start is not None:
            sx = origin_x + run_start * scale_x
            sy = origin_y + y * scale_y
            rlen = (w - run_start) * scale_x
            path_segments.append(f"M{sx:.1f} {sy:.1f}h{rlen:.1f}v{scale_y:.1f}h-{rlen:.1f}z")

    return " ".join(path_segments)

def generate_banner(output_path, dark_mode=True, photo_path=None):
    # Palette per specification
    bg_color = "#0A101F" if dark_mode else "#F8FAFC"
    term_bar_bg = "#0D1527" if dark_mode else "#E2E8F0"
    term_border = "#1E293B" if dark_mode else "#CBD5E1"
    chrome_color = "#22D3EE" if dark_mode else "#0891B2"
    portrait_color = "#A78BFA" if dark_mode else "#7C3AED"
    accent_color = "#10B981"
    leader_color = "#334155" if dark_mode else "#CBD5E1"
    label_color = "#94A3B8" if dark_mode else "#64748B"
    value_color = "#F8FAFC" if dark_mode else "#0F172A"

    # Dithered portrait
    bits = process_portrait(photo_path, grid_w=280, grid_h=340, dark_mode=dark_mode)
    path_d = bits_to_svg_paths(bits, origin_x=65, origin_y=118, scale_x=1.32, scale_y=1.28)

    # Info panel rows from CV
    info_rows = [
        ("Subject", "Uvaram Mohanaram"),
        ("Role", "AI / ML & Software Engineer"),
        ("Origin", "Colombo, Sri Lanka"),
        ("Education", "BSc (Hons) Software Eng · KDU"),
        ("Status", "Building + Training + Shipping"),
        ("ToolChain", "VS Code · Git · Docker · Azure · Linux"),
        ("Core.Lang", "Python · TypeScript · JavaScript · SQL"),
        ("Core.AI", "PyTorch · Hugging Face · ONNX Runtime"),
        ("Core.MLOps", "FastAPI · Docker · Azure · GitHub CI/CD"),
        ("Core.Data", "scikit-learn · Pandas · NumPy · RAG"),
        ("Core.Web", "Next.js · React · Vite · Tailwind CSS"),
        ("Core.DB", "Supabase (Postgres) · Pinecone · SQLite"),
        ("Platform", "Xyrex · Scalable AI Systems & Engineering"),
        ("Grid.Mail", "mohanuvaram123@gmail.com"),
        ("Grid.LinkedIn", "uvaram-mohanaram-aa20932b1"),
        ("Grid.GitHub", "github.com/batman2400"),
        ("Grid.Lead", "Team Leader · Team Fade (TensorForge 2.0)"),
    ]

    # Generate SVGs
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1180 610" width="1180" height="610">',
        f'  <defs>',
        f'    <style>',
        f'      @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.25; }} }}',
        f'      .pulse-red {{ animation: pulse 1.5s cubic-bezier(0.4, 0, 0.6, 1) infinite; }}',
        f'      .mono {{ font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, "Liberation Mono", monospace; }}',
        f'    </style>',
        f'  </defs>',
        f'  <!-- Background -->',
        f'  <rect width="1180" height="610" rx="14" fill="{bg_color}" stroke="{term_border}" stroke-width="1.5" />',
        f'  <!-- Terminal Titlebar -->',
        f'  <path d="M 0 14 Q 0 0 14 0 L 1166 0 Q 1180 0 1180 14 L 1180 44 L 0 44 Z" fill="{term_bar_bg}" />',
        f'  <line x1="0" y1="44" x2="1180" y2="44" stroke="{term_border}" stroke-width="1" />',
        f'  <!-- Window Buttons -->',
        f'  <circle cx="28" cy="22" r="6" fill="#EF4444" />',
        f'  <circle cx="48" cy="22" r="6" fill="#F59E0B" />',
        f'  <circle cx="68" cy="22" r="6" fill="#10B981" />',
        f'  <!-- Terminal Title -->',
        f'  <text x="590" y="27" text-anchor="middle" fill="{label_color}" class="mono" font-size="13" font-weight="600">profile.sh --live</text>',
        f'  <!-- Pulse LIVE Badge -->',
        f'  <circle cx="1035" cy="22" r="4.5" fill="#EF4444" class="pulse-red" />',
        f'  <text x="1048" y="26" fill="#EF4444" class="mono" font-size="12" font-weight="700" letter-spacing="1">LIVE</text>',
        f'  <!-- Handle Pill -->',
        f'  <rect x="1090" y="11" width="76" height="22" rx="11" fill="{chrome_color}" fill-opacity="0.15" stroke="{chrome_color}" stroke-width="1" />',
        f'  <text x="1128" y="26" text-anchor="middle" fill="{chrome_color}" class="mono" font-size="11" font-weight="700">@batman2400</text>',
        f'  <!-- Left Column: Portrait Frame -->',
        f'  <rect x="45" y="65" width="410" height="515" rx="8" fill="{bg_color}" stroke="{term_border}" stroke-width="1" />',
        f'  <!-- Portrait Header -->',
        f'  <rect x="45" y="65" width="410" height="34" rx="8" fill="{term_bar_bg}" fill-opacity="0.7" />',
        f'  <line x1="45" y1="99" x2="455" y2="99" stroke="{term_border}" stroke-width="1" />',
        f'  <text x="65" y="87" fill="{chrome_color}" class="mono" font-size="12" font-weight="700" letter-spacing="1.5">VISUAL.MAP</text>',
        f'  <text x="435" y="87" text-anchor="end" fill="{accent_color}" class="mono" font-size="11">DITHER_1BIT</text>',
        f'  <!-- Portrait Dither Dots Path -->',
        f'  <g fill="{portrait_color}" shape-rendering="crispEdges">',
        f'    <path d="{path_d}" />',
        f'  </g>',
        f'  <!-- Right Column: SYSTEM.INFO Panel -->',
        f'  <rect x="475" y="65" width="660" height="515" rx="8" fill="{bg_color}" stroke="{term_border}" stroke-width="1" />',
        f'  <!-- SYSTEM.INFO Header -->',
        f'  <rect x="475" y="65" width="660" height="34" rx="8" fill="{term_bar_bg}" fill-opacity="0.7" />',
        f'  <line x1="475" y1="99" x2="1135" y2="99" stroke="{term_border}" stroke-width="1" />',
        f'  <text x="495" y="87" fill="{chrome_color}" class="mono" font-size="12" font-weight="700" letter-spacing="1.5">SYSTEM.INFO</text>',
        f'  <text x="1115" y="87" text-anchor="end" fill="{label_color}" class="mono" font-size="11">SYS_STATUS: ONLINE</text>',
    ]

    # Render info rows with computed dotted leaders and XML-escaped content
    start_y = 130
    spacing = 26
    label_x = 498

    for i, (label, val) in enumerate(info_rows):
        cur_y = start_y + i * spacing
        dots_count = max(3, 72 - (len(label) + len(val)))
        dots_str = " " + ("." * dots_count) + " "

        esc_label = html.escape(label)
        esc_val = html.escape(val)

        svg_lines.append(
            f'  <g class="mono" font-size="13">'
            f'<text x="{label_x}" y="{cur_y}" fill="{label_color}">{esc_label}'
            f'<tspan fill="{leader_color}">{dots_str}</tspan>'
            f'<tspan fill="{value_color}" font-weight="600">{esc_val}</tspan>'
            f'</text>'
            f'</g>'
        )

    # Footer status line
    svg_lines.append(f'  <line x1="475" y1="545" x2="1135" y2="545" stroke="{term_border}" stroke-width="1" />')
    svg_lines.append(f'  <text x="498" y="565" fill="{accent_color}" class="mono" font-size="12">&#9654; model.eval() --precision bfloat16 --inference-ready</text>')
    svg_lines.append(f'  <text x="1115" y="565" text-anchor="end" fill="{label_color}" class="mono" font-size="11">UTC: 2026.10</text>')

    svg_lines.append('</svg>')

    full_svg = "\n".join(svg_lines)

    # Validate XML before writing
    try:
        ET.fromstring(full_svg)
    except ET.ParseError as err:
        raise ValueError(f"Generated SVG has XML parse error: {err}")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_svg)

if __name__ == "__main__":
    work_dir = os.path.dirname(os.path.abspath(__file__))
    dark_path = os.path.join(work_dir, "dark.svg")
    light_path = os.path.join(work_dir, "light.svg")

    photo_path = os.path.join(work_dir, "photo.jpg")
    if not os.path.exists(photo_path):
        photo_path = None

    print(f"Generating dark.svg with user photo: {photo_path}")
    generate_banner(dark_path, dark_mode=True, photo_path=photo_path)
    print(f"Generating light.svg with user photo: {photo_path}")
    generate_banner(light_path, dark_mode=False, photo_path=photo_path)
    print("All banners generated and XML validated successfully!")
