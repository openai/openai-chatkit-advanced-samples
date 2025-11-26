#!/usr/bin/env python3
"""
Halftone Converter - Convert images to dot-grid halftone style

Takes an input image and converts it to a halftone pattern using circular dots
on a grid, with dot size varying based on brightness. Colors are mapped to
a predefined palette.

Usage:
    python halftone_converter.py input.png output.png
    python halftone_converter.py input.png output.png --sample 8 --scale 2
"""

import argparse
import math
from pathlib import Path
from PIL import Image, ImageDraw

# CUPID Color Palette
PALETTE = {
    'background': (253, 246, 227),  # #FDF6E3
    'text': (70, 70, 70),           # #464646
    'red': (215, 78, 57),           # #D74E39
    'orange': (218, 104, 0),        # #DA6800
    'yellow': (255, 201, 34),       # #FFC922
    'pink': (231, 181, 160),        # #E7B5A0
    'green': (138, 164, 125),       # #8AA47D
    'blue': (108, 194, 255),        # #6CC2FF
    'purple': (155, 133, 183),      # #9B85B7
}

# Just the colors we want to map to (excluding background)
PALETTE_COLORS = [
    PALETTE['text'],
    PALETTE['red'],
    PALETTE['orange'],
    PALETTE['yellow'],
    PALETTE['pink'],
    PALETTE['green'],
    PALETTE['blue'],
    PALETTE['purple'],
]


def color_distance(c1: tuple, c2: tuple) -> float:
    """Calculate Euclidean distance between two RGB colors."""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(c1, c2)))


def nearest_palette_color(rgb: tuple) -> tuple:
    """Find the nearest color in the palette to the given RGB color."""
    return min(PALETTE_COLORS, key=lambda c: color_distance(rgb, c))


def get_brightness(rgb: tuple) -> float:
    """Calculate perceived brightness (0-1) using luminance formula."""
    r, g, b = rgb[:3]
    return (0.299 * r + 0.587 * g + 0.114 * b) / 255


def halftone_convert(
    input_path: str,
    output_path: str,
    sample: int = 8,
    scale: float = 1.0,
    min_dot_ratio: float = 0.1,
    antialias: int = 4,
    white_threshold: float = 0.92,
) -> None:
    """
    Convert an image to halftone dot-grid style.

    Args:
        input_path: Path to input image
        output_path: Path to save output image
        sample: Size of sample blocks in pixels (grid cell size)
        scale: Scale factor for output (1.0 = same grid size as sample)
        min_dot_ratio: Minimum dot size as ratio of cell (0-1)
        antialias: Antialiasing factor (draws Nx size then downsamples)
    """
    # Load image
    img = Image.open(input_path).convert('RGBA')
    width, height = img.size

    # Calculate output dimensions
    grid_cols = width // sample
    grid_rows = height // sample
    cell_size = int(sample * scale)

    # Create output at antialias scale for smooth circles
    aa_cell = cell_size * antialias
    aa_width = grid_cols * aa_cell
    aa_height = grid_rows * aa_cell

    # Transparent background
    output = Image.new('RGBA', (aa_width, aa_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(output)

    # Process each grid cell
    for row in range(grid_rows):
        for col in range(grid_cols):
            # Sample the block from input image
            x1 = col * sample
            y1 = row * sample
            x2 = min(x1 + sample, width)
            y2 = min(y1 + sample, height)

            # Get all pixels in this block
            block = img.crop((x1, y1, x2, y2))
            pixels = list(block.getdata())

            # Filter out transparent pixels (strict threshold)
            opaque_pixels = [p for p in pixels if p[3] > 240]

            if not opaque_pixels:
                # Skip transparent blocks
                continue

            # Need at least 25% of block to be opaque to draw a dot
            if len(opaque_pixels) < len(pixels) * 0.25:
                continue

            # Skip if the block is too light (only keep darker areas)
            avg_brightness_check = sum(get_brightness(p[:3]) for p in opaque_pixels) / len(opaque_pixels)
            if avg_brightness_check > 0.85:
                continue

            # Calculate average color of opaque pixels
            avg_r = sum(p[0] for p in opaque_pixels) // len(opaque_pixels)
            avg_g = sum(p[1] for p in opaque_pixels) // len(opaque_pixels)
            avg_b = sum(p[2] for p in opaque_pixels) // len(opaque_pixels)
            avg_a = sum(p[3] for p in opaque_pixels) // len(opaque_pixels)

            avg_color = (avg_r, avg_g, avg_b)

            # Map to nearest palette color
            dot_color = nearest_palette_color(avg_color)

            # Calculate dot size based on brightness
            # Darker = larger dots, lighter = smaller dots
            brightness = get_brightness(avg_color)
            # Invert: dark areas get big dots
            dot_ratio = 1.0 - brightness

            # Make dots BIG - like the reference halftone
            # Minimum dot is 70% of max, maximum is 95%
            dot_ratio = 0.70 + (dot_ratio * 0.25)

            # Calculate dot radius in antialiased space
            max_radius = aa_cell / 2
            radius = max_radius * dot_ratio

            if radius < 1:
                continue

            # Calculate center position
            cx = col * aa_cell + aa_cell // 2
            cy = row * aa_cell + aa_cell // 2

            # Draw circle
            draw.ellipse(
                [cx - radius, cy - radius, cx + radius, cy + radius],
                fill=(*dot_color, 255)
            )

    # Downsample with antialiasing
    final_width = grid_cols * cell_size
    final_height = grid_rows * cell_size
    output = output.resize((final_width, final_height), Image.LANCZOS)

    # Save
    output.save(output_path, 'PNG')
    print(f"Saved halftone image to: {output_path}")
    print(f"  Input size: {width}x{height}")
    print(f"  Grid: {grid_cols}x{grid_rows} cells")
    print(f"  Output size: {final_width}x{final_height}")


def main():
    parser = argparse.ArgumentParser(
        description='Convert images to halftone dot-grid style'
    )
    parser.add_argument('input', help='Input image path')
    parser.add_argument('output', help='Output image path')
    parser.add_argument(
        '--sample', type=int, default=8,
        help='Sample block size in pixels (default: 8)'
    )
    parser.add_argument(
        '--scale', type=float, default=1.0,
        help='Output scale factor (default: 1.0)'
    )
    parser.add_argument(
        '--min-dot', type=float, default=0.1,
        help='Minimum dot size ratio (default: 0.1)'
    )
    parser.add_argument(
        '--antialias', type=int, default=4,
        help='Antialiasing factor (default: 4)'
    )

    args = parser.parse_args()

    halftone_convert(
        args.input,
        args.output,
        sample=args.sample,
        scale=args.scale,
        min_dot_ratio=args.min_dot,
        antialias=args.antialias,
    )


if __name__ == '__main__':
    main()
