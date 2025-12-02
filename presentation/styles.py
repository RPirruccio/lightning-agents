"""
Visual styling constants for the presentation.

AIMUG branded colors (blue/orange theme from aimug.org).
"""

# Colors (hex without #, for RgbColor.from_string)
COLORS = {
    "primary": "0088CC",       # AIMUG Blue - headers, main boxes
    "secondary": "FF6B35",     # AIMUG Orange - accents, highlights
    "background": "FFFFFF",    # White
    "text_dark": "1A1A2E",     # Near-black for body text
    "text_light": "666666",    # Gray for subtitles
    "code_bg": "F8F9FA",       # Light gray for code blocks
    "success": "28A745",       # Green for "Instance Ready" boxes
    "white": "FFFFFF",         # Pure white for text on colored backgrounds
}

# Fonts
FONTS = {
    "title": "Arial",
    "body": "Arial",
    "code": "Consolas",  # Monospace for code
}

# Font sizes (points)
SIZES = {
    "title": 44,
    "subtitle": 24,
    "heading": 32,
    "body": 18,
    "code": 14,
    "small": 12,
}

# Slide dimensions (16:9 aspect ratio in inches)
DIMS = {
    "width": 13.333,
    "height": 7.5,
    "margin": 0.5,
}
