"""
colors.py
Shared color palette and gender constants used across the app.
Replaces the old silhouette.py avatar-drawing module — StyleSync no longer
renders a mannequin/doll, so we only need color swatches now.
"""

COLOR_HEX = {
    "white":  "#FFFFFF",
    "black":  "#1F1B24",
    "grey":   "#9CA3AF",
    "blue":   "#3B82F6",
    "navy":   "#1E3A5F",
    "red":    "#EF4444",
    "green":  "#22C55E",
    "yellow": "#EAB308",
    "brown":  "#8B5E34",
    "beige":  "#D8C3A5",
    "pink":   "#EC4899",
    "purple": "#A855F7",
    "orange": "#F97316",
}

# Genders a wardrobe item can be tagged with. "Unisex" items are eligible
# for both Male and Female outfit suggestions.
GENDERS = ["Male", "Female", "Unisex"]
