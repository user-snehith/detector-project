#!/usr/bin/env python
"""
Icon generator for Phishing URL Detector Chrome Extension
Run this script to generate the required icon files.
"""

import os
from pathlib import Path

# Simple SVG icon template
ICON_SVG = '''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}" xmlns="http://www.w3.org/2000/svg">
  <!-- Shield background -->
  <defs>
    <linearGradient id="shieldGradient" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:#667eea;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#764ba2;stop-opacity:1" />
    </linearGradient>
  </defs>

  <!-- Shield shape -->
  <path d="M {center} 2 L {size_minus_2} {center} L {center} {size_minus_2} L 2 {center} Z"
        fill="url(#shieldGradient)"
        stroke="#ffffff"
        stroke-width="2"/>

  <!-- Warning triangle -->
  <polygon points="{center},{center-8} {center-6},{center+4} {center+6},{center+4}"
           fill="#ff6b6b"
           stroke="#ffffff"
           stroke-width="1"/>

  <!-- Exclamation mark -->
  <circle cx="{center}" cy="{center-2}" r="1.5" fill="#ffffff"/>
  <rect x="{center-0.5}" y="{center+1}" width="1" height="3" fill="#ffffff"/>
</svg>'''

def generate_icons():
    """Generate PNG icons from SVG template"""

    try:
        from PIL import Image, ImageDraw
        import io
    except ImportError:
        print("PIL (Pillow) not installed. Please install with: pip install Pillow")
        print("For now, creating placeholder text files...")
        create_placeholder_icons()
        return

    sizes = [16, 48, 128]
    icons_dir = Path(__file__).parent / "icons"

    for size in sizes:
        # Create simple colored square with text
        img = Image.new('RGBA', (size, size), (102, 126, 234))  # Blue background
        draw = ImageDraw.Draw(img)

        # Draw a simple shield-like shape
        center = size // 2
        margin = size // 8

        # Draw shield outline
        points = [
            (center, margin),  # Top point
            (size - margin, center),  # Right point
            (center, size - margin),  # Bottom point
            (margin, center)  # Left point
        ]
        draw.polygon(points, fill=(102, 126, 234), outline=(255, 255, 255))

        # Draw warning symbol (simplified)
        warn_size = size // 4
        warn_x = center - warn_size // 2
        warn_y = center - warn_size // 2

        # Warning triangle
        draw.polygon([
            (center, warn_y),
            (center - warn_size//2, warn_y + warn_size),
            (center + warn_size//2, warn_y + warn_size)
        ], fill=(255, 107, 107))

        # Exclamation mark (simplified dot)
        draw.ellipse([center-1, center-2, center+1, center], fill=(255, 255, 255))

        # Save icon
        icon_path = icons_dir / f"icon{size}.png"
        img.save(icon_path, "PNG")
        print(f"Generated {icon_path}")

def create_placeholder_icons():
    """Create placeholder text files for icons"""
    icons_dir = Path(__file__).parent / "icons"

    for size in [16, 48, 128]:
        icon_path = icons_dir / f"icon{size}.png"
        with open(icon_path, 'w') as f:
            f.write(f"Placeholder for {size}x{size} PNG icon\n")
            f.write("Run 'python generate_icons.py' with Pillow installed to generate actual icons\n")
        print(f"Created placeholder {icon_path}")

if __name__ == "__main__":
    print("Generating Chrome extension icons...")

    # Create icons directory if it doesn't exist
    icons_dir = Path(__file__).parent / "icons"
    icons_dir.mkdir(exist_ok=True)

    generate_icons()

    print("\nIcon generation complete!")
    print("You can now load the extension in Chrome:")
    print("1. Go to chrome://extensions/")
    print("2. Enable 'Developer mode'")
    print("3. Click 'Load unpacked'")
    print("4. Select the chrome_extension folder")