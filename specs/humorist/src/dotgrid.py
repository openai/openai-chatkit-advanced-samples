#!/usr/bin/env python3
# /// script
# dependencies = ["pillow"]
# ///
"""
Dot Grid Renderer - Renders dot grid icons from JSON to SVG and PNG.

Usage:
    uv run dotgrid.py '{"grid": [...], "name": "heart"}'
    uv run dotgrid.py --file input.json
    echo '{"grid": [...]}' | uv run dotgrid.py

Supports 8x8 or 16x16 grids (auto-detected from input).
"""

import json
import sys
from pathlib import Path
from PIL import Image, ImageDraw

# Canvas is always 384x384, grid specs adjust based on size
CANVAS_SIZE = 384

# Grid specs for different sizes (centered on 384px canvas)
# Formula: padding = (canvas - (n-1) * spacing) / 2
GRID_SPECS = {
    8: {"dot_diameter": 32, "spacing": 44, "padding": 38},    # 38 + 7*44 + 38 = 384
    16: {"dot_diameter": 20, "spacing": 24, "padding": 12},   # 12 + 15*24 + 12 = 384
    32: {"dot_diameter": 10, "spacing": 12, "padding": 6},    # 6 + 31*12 + 6 = 384
}

# Color palette
COLORS = {
    "off": None,
    "text": "#464646",
    "red": "#D74E39",
    "orange": "#DA6800",
    "yellow": "#FFC922",
    "pink": "#E7B5A0",
    "green": "#8AA47D",
    "blue": "#6CC2FF",
    "purple": "#9B85B7",
}

DEFAULT_OUTPUT_DIR = Path(__file__).parent.parent / "output"


def hex_to_rgb(hex_color: str) -> tuple:
    """Convert hex color to RGB tuple."""
    h = hex_color.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0, 2, 4))


def get_specs(grid_size: int) -> dict:
    """Get grid specs for a given size."""
    if grid_size in GRID_SPECS:
        return GRID_SPECS[grid_size]
    # Fallback for other sizes
    spacing = CANVAS_SIZE // (grid_size + 1)
    return {
        "dot_diameter": int(spacing * 0.8),
        "spacing": spacing,
        "padding": spacing,
    }


def render_svg(grid: list[list[str]], name: str) -> str:
    """Render grid to SVG string."""
    grid_size = len(grid)
    specs = get_specs(grid_size)
    dot_radius = specs["dot_diameter"] // 2
    spacing = specs["spacing"]
    padding = specs["padding"]

    circles = []

    for row_idx, row in enumerate(grid):
        for col_idx, color in enumerate(row):
            if color == "off" or color not in COLORS or COLORS[color] is None:
                continue

            cx = padding + col_idx * spacing
            cy = padding + row_idx * spacing
            fill = COLORS[color]

            circles.append(
                f'  <circle cx="{cx}" cy="{cy}" r="{dot_radius}" fill="{fill}"/>'
            )

    svg = f'''<svg width="{CANVAS_SIZE}" height="{CANVAS_SIZE}" viewBox="0 0 {CANVAS_SIZE} {CANVAS_SIZE}" xmlns="http://www.w3.org/2000/svg">
  <!-- {name} - Humorist Dot Grid ({grid_size}x{grid_size}) -->
{chr(10).join(circles)}
</svg>'''

    return svg


def render_png(grid: list[list[str]], name: str, antialias: int = 4) -> Image.Image:
    """Render grid to PNG image with antialiasing."""
    grid_size = len(grid)
    specs = get_specs(grid_size)
    dot_radius = specs["dot_diameter"] // 2
    spacing = specs["spacing"]
    padding = specs["padding"]

    # Render at higher resolution for antialiasing
    aa_size = CANVAS_SIZE * antialias
    aa_spacing = spacing * antialias
    aa_padding = padding * antialias
    aa_radius = dot_radius * antialias

    img = Image.new("RGBA", (aa_size, aa_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    for row_idx, row in enumerate(grid):
        for col_idx, color in enumerate(row):
            if color == "off" or color not in COLORS or COLORS[color] is None:
                continue

            cx = aa_padding + col_idx * aa_spacing
            cy = aa_padding + row_idx * aa_spacing
            rgb = hex_to_rgb(COLORS[color])

            draw.ellipse(
                [cx - aa_radius, cy - aa_radius, cx + aa_radius, cy + aa_radius],
                fill=(*rgb, 255)
            )

    # Downsample for antialiasing
    img = img.resize((CANVAS_SIZE, CANVAS_SIZE), Image.LANCZOS)
    return img


def main():
    # Parse input
    if len(sys.argv) > 1 and sys.argv[1] == "--file":
        with open(sys.argv[2]) as f:
            data = json.load(f)
    elif len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        data = json.loads(sys.argv[1])
    elif not sys.stdin.isatty():
        data = json.load(sys.stdin)
    else:
        print("Usage: uv run dotgrid.py '{\"grid\": [...], \"name\": \"icon\"}'")
        print("       uv run dotgrid.py --file input.json")
        sys.exit(1)

    grid = data.get("grid", [])
    name = data.get("name", "dotgrid")
    output_dir = Path(data.get("output_dir", DEFAULT_OUTPUT_DIR))

    # Auto-detect grid size
    grid_size = len(grid)
    if grid_size not in [8, 16, 32]:
        print(f"Warning: Unusual grid size {grid_size}x{grid_size}")

    # Validate grid is square
    for i, row in enumerate(grid):
        if len(row) != grid_size:
            print(f"Error: Row {i} has {len(row)} columns, expected {grid_size}")
            sys.exit(1)

    # Ensure output directory exists
    output_dir.mkdir(parents=True, exist_ok=True)

    # Render SVG
    svg_content = render_svg(grid, name)
    svg_path = output_dir / f"{name}.svg"
    svg_path.write_text(svg_content)
    print(f"Created: {svg_path}")

    # Render PNG
    png_img = render_png(grid, name)
    png_path = output_dir / f"{name}.png"
    png_img.save(png_path, "PNG")
    print(f"Created: {png_path}")


if __name__ == "__main__":
    main()
