#!/bin/bash

# Create minimal colored square icons for PWA testing
# These are just colored squares with "CVD" text

# Create icons directory if it doesn't exist
mkdir -p icons

# Create a simple Python script to generate colored squares
cat > create_icon.py << 'EOF'
from PIL import Image, ImageDraw, ImageFont
import sys

size = int(sys.argv[1])
output = sys.argv[2]

# Create image with blue background
img = Image.new('RGBA', (size, size), (0, 109, 254, 255))
draw = ImageDraw.Draw(img)

# Try to use a basic font, fallback to default if not available
try:
    # Adjust font size based on icon size
    font_size = size // 3
    font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", font_size)
except:
    font = ImageFont.load_default()

# Draw white text
text = "CVD"
bbox = draw.textbbox((0, 0), text, font=font)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2
draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

# Save
img.save(output, "PNG")
print(f"Created {output}")
EOF

# Check if Pillow is installed
if python3 -c "import PIL" &> /dev/null; then
    echo "Creating icons with Pillow..."
    python3 create_icon.py 192 icons/icon-192x192.png
    python3 create_icon.py 512 icons/icon-512x512.png
else
    echo "Pillow not installed. Creating minimal icons with ImageMagick..."
    
    # Try ImageMagick as fallback
    if command -v convert &> /dev/null; then
        convert -size 192x192 xc:'#006dfe' -gravity center -fill white -font Arial -pointsize 64 -annotate +0+0 'CVD' icons/icon-192x192.png
        convert -size 512x512 xc:'#006dfe' -gravity center -fill white -font Arial -pointsize 170 -annotate +0+0 'CVD' icons/icon-512x512.png
    else
        echo "Neither Pillow nor ImageMagick found."
        echo "Creating minimal placeholder files..."
        
        # Create empty placeholder files so the manifest doesn't fail
        touch icons/icon-192x192.png
        touch icons/icon-512x512.png
        
        echo "Please use create-png-icons.html in a browser to generate proper icons."
    fi
fi

# Clean up
rm -f create_icon.py

echo "Done! Check the icons directory."
ls -la icons/*.png 2>/dev/null || echo "No PNG files created."