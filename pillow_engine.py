#!/usr/bin/env python3
# Copyright (c) 2024-2026 Aditya001-max <kaushikadityaraj001@gmail.com>
# MIT License

"""
SlideGen Pure-Python Pillow Rendering Engine
Generates 1920x1080 broadcast-quality slides using Pillow without requiring ImageMagick.
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def parse_song_file(file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    metadata = {}
    songtext = {}
    in_body = False
    current_key = None
    current_body = []

    for line in lines:
        stripped = line.strip()
        if not in_body:
            if stripped.startswith("[") and stripped.endswith("]"):
                in_body = True
                current_key = stripped[1:-1]
                current_body = []
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                metadata[k.strip().lower()] = v.strip()
        else:
            if stripped.startswith("[") and stripped.endswith("]"):
                if current_key:
                    songtext[current_key] = "\n".join(current_body).strip()
                current_key = stripped[1:-1]
                current_body = []
            else:
                current_body.append(line.rstrip("\r\n"))

    if current_key and current_body:
        songtext[current_key] = "\n".join(current_body).strip()

    return metadata, songtext


def get_default_font(size: int, bold: bool = False):
    font_names = [
        "Arial.ttf" if not bold else "Arialbd.ttf",
        "DejaVuSans.ttf" if not bold else "DejaVuSans-Bold.ttf",
        "segoeui.ttf" if not bold else "segoeuib.ttf",
        "calibri.ttf" if not bold else "calibrib.ttf",
    ]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except OSError:
            continue
    try:
        return ImageFont.load_default(size=size)
    except TypeError:
        return ImageFont.load_default()


def render_start_slide(metadata: dict, output_path: str, width=1920, height=1080, bg_color="white", fg_color="#6298a4"):
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Banner
    title_y = 65
    title_h = 160
    draw.rectangle([0, title_y, width, title_y + title_h], fill=fg_color)

    # Triangle Accent
    draw.polygon([(width - 120, title_y), (width, title_y), (width, title_y + title_h)], fill="#d8d5c4")

    # Title Text
    font_title = get_default_font(60, bold=True)
    title = metadata.get("title", "Untitled Slide")
    draw.text((80, title_y + 45), title, fill="white", font=font_title)

    # Book
    book = metadata.get("book", "")
    if book:
        font_book = get_default_font(36, bold=True)
        draw.text((80, 260), book, fill="black", font=font_book)

    # Attributions
    font_attr = get_default_font(32, bold=False)
    text_attr = metadata.get("text", "")
    melody_attr = metadata.get("melody", "")

    attr_y = 880
    if text_attr:
        draw.text((80, attr_y), f"Text: {text_attr}", fill="black", font=font_attr)
        attr_y += 50
    if melody_attr:
        draw.text((80, attr_y), f"Melody: {melody_attr}", fill="black", font=font_attr)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, quality=95)


def render_verse_slide(
    title: str,
    verse_key: str,
    verse_text: str,
    output_path: str,
    current_index: int,
    total_elements: int,
    width=1920,
    height=1080,
    bg_color="white",
    fg_color="#6298a4"
):
    img = Image.new("RGB", (width, height), color=bg_color)
    draw = ImageDraw.Draw(img)

    # Top Title Banner
    title_bar_y = 60
    title_bar_h = 120
    draw.rectangle([0, title_bar_y, width, title_bar_y + title_bar_h], fill=fg_color)

    font_title = get_default_font(48, bold=True)
    draw.text((80, title_bar_y + 35), title, fill="white", font=font_title)

    # Structure Indicator
    font_label = get_default_font(42, bold=True)
    label_text = "Refrain" if verse_key.upper() == "R" else f"Verse {verse_key}"
    draw.text((80, 240), label_text, fill=fg_color, font=font_label)

    # Lyrics Lines
    font_lyrics = get_default_font(46, bold=False)
    lines = verse_text.splitlines()
    start_y = 330
    line_spacing = 64

    for line in lines[:8]:
        draw.text((160, start_y), line, fill="black", font=font_lyrics)
        start_y += line_spacing

    # Navigation Dots at bottom right
    start_dot_x = 1600
    dot_y = 1010
    for i in range(total_elements):
        is_cur = (i == current_index)
        radius = 8 if is_cur else 5
        color = fg_color if is_cur else "#cccccc"
        cx = start_dot_x + (i * 28)
        draw.ellipse([cx - radius, dot_y - radius, cx + radius, dot_y + radius], fill=color)

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path, quality=95)


def generate_all_slides(song_file_path: str, output_dir: str, desired_structure: list[str] | None = None) -> list[str]:
    metadata, songtext = parse_song_file(song_file_path)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    if not desired_structure:
        raw_struct = metadata.get("structure", "")
        if raw_struct:
            desired_structure = [s.strip() for s in raw_struct.split(",") if s.strip()]
        else:
            desired_structure = list(songtext.keys())

    generated = []

    # 1. Start slide
    start_slide_file = str(output_path / "slide-01.jpg")
    render_start_slide(metadata, start_slide_file)
    generated.append(start_slide_file)

    # 2. Sequence slides
    slide_idx = 2
    for seq_i, elem in enumerate(desired_structure):
        lyrics = songtext.get(elem, f"[{elem} not found]")
        slide_file = str(output_path / f"slide-{str(slide_idx).zfill(2)}.jpg")
        render_verse_slide(
            title=metadata.get("title", ""),
            verse_key=elem,
            verse_text=lyrics,
            output_path=slide_file,
            current_index=seq_i,
            total_elements=len(desired_structure)
        )
        generated.append(slide_file)
        slide_idx += 1

    return generated


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python pillow_engine.py <SRC_PATH> <DEST_DIR> [STRUCTURE]")
        print("Example: python pillow_engine.py template.txt ./output '1, 2, 3'")
        sys.exit(1)

    src = sys.argv[1]
    dest = sys.argv[2]
    struct = [s.strip() for s in sys.argv[3].split(",")] if len(sys.argv) > 3 else None
    slides = generate_all_slides(src, dest, struct)
    print(f"Successfully generated {len(slides)} slides into '{dest}'.")
