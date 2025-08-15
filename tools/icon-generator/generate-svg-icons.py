#!/usr/bin/env python3
import os

# SVG template for the icon
svg_template = '''<svg width="{size}" height="{size}" xmlns="http://www.w3.org/2000/svg">
  <rect width="{size}" height="{size}" fill="#006dfe" rx="{radius}"/>
  <text x="50%" y="50%" font-family="Arial" font-size="{font_size}" fill="white" text-anchor="middle" dominant-baseline="middle">🚚</text>
</svg>'''

# Icon sizes needed
sizes = [72, 96, 128, 144, 152, 192, 384, 512]

# Create icons directory if it doesn't exist
os.makedirs('icons', exist_ok=True)

# Generate SVG files
for size in sizes:
    radius = size * 0.1  # 10% border radius
    font_size = size * 0.5  # 50% of icon size
    
    svg_content = svg_template.format(
        size=size,
        radius=radius,
        font_size=font_size
    )
    
    filename = f'icons/icon-{size}x{size}.svg'
    with open(filename, 'w') as f:
        f.write(svg_content)
    print(f'Created {filename}')

print('\nSVG icons created! To convert to PNG:')
print('1. Use an online converter like https://cloudconvert.com/svg-to-png')
print('2. Or install ImageMagick and run:')
for size in sizes:
    print(f'   convert icons/icon-{size}x{size}.svg icons/icon-{size}x{size}.png')