// Script to generate PWA icons in all required sizes
// This creates simple icon placeholders - in production, replace with actual designed icons

const fs = require('fs');
const path = require('path');

// Create icons directory if it doesn't exist
const iconsDir = path.join(__dirname, 'icons');
if (!fs.existsSync(iconsDir)) {
    fs.mkdirSync(iconsDir);
}

// Icon sizes required for PWA
const sizes = [
    { size: 72, name: 'icon-72x72.png' },
    { size: 96, name: 'icon-96x96.png' },
    { size: 128, name: 'icon-128x128.png' },
    { size: 144, name: 'icon-144x144.png' },
    { size: 152, name: 'icon-152x152.png' },
    { size: 192, name: 'icon-192x192.png' },
    { size: 384, name: 'icon-384x384.png' },
    { size: 512, name: 'icon-512x512.png' }
];

// Create SVG template for icon
const createSVG = (size) => {
    return `<svg width="${size}" height="${size}" xmlns="http://www.w3.org/2000/svg">
    <rect width="${size}" height="${size}" fill="#006dfe"/>
    <text x="50%" y="50%" font-family="Arial" font-size="${size * 0.5}" fill="white" text-anchor="middle" dominant-baseline="middle">🚚</text>
</svg>`;
};

// Generate placeholder message
console.log('Icon Generation Instructions:');
console.log('=============================');
console.log('To generate actual PWA icons, you need to:');
console.log('');
console.log('1. Create a high-resolution logo (at least 512x512px)');
console.log('2. Use an icon generator tool like:');
console.log('   - https://www.pwabuilder.com/imageGenerator');
console.log('   - https://realfavicongenerator.net/');
console.log('   - https://maskable.app/');
console.log('');
console.log('3. Generate icons in these sizes:');
sizes.forEach(({ size, name }) => {
    console.log(`   - ${name} (${size}x${size}px)`);
});
console.log('');
console.log('4. Place generated icons in the /icons directory');
console.log('');
console.log('5. Ensure at least one icon is marked as "maskable" for Android adaptive icons');
console.log('');
console.log('For now, creating placeholder icon instructions...');

// Create a simple HTML file with icon generation instructions
const instructionsHTML = `<!DOCTYPE html>
<html>
<head>
    <title>PWA Icon Generator Instructions</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px;
            margin: 40px auto;
            padding: 20px;
            line-height: 1.6;
        }
        .icon-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .icon-preview {
            text-align: center;
            padding: 10px;
            border: 1px solid #eee;
            border-radius: 8px;
        }
        .icon-box {
            width: 100px;
            height: 100px;
            background: #006dfe;
            margin: 0 auto 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 48px;
            border-radius: 20%;
        }
        code {
            background: #f5f5f5;
            padding: 2px 6px;
            border-radius: 3px;
        }
        pre {
            background: #f5f5f5;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
        }
    </style>
</head>
<body>
    <h1>PWA Icon Generation Guide</h1>
    
    <h2>Required Icon Sizes</h2>
    <div class="icon-grid">
        ${sizes.map(({ size, name }) => `
        <div class="icon-preview">
            <div class="icon-box" style="width: ${Math.min(size, 100)}px; height: ${Math.min(size, 100)}px; font-size: ${Math.min(size * 0.5, 48)}px;">🚚</div>
            <code>${name}</code>
            <div>${size}x${size}px</div>
        </div>
        `).join('')}
    </div>

    <h2>Icon Requirements</h2>
    <ul>
        <li><strong>Format:</strong> PNG with transparency</li>
        <li><strong>Purpose:</strong> At least one "maskable" icon for Android</li>
        <li><strong>Design:</strong> Center logo with adequate padding (safe zone)</li>
        <li><strong>Colors:</strong> Use brand color #006dfe as background</li>
    </ul>

    <h2>Quick Generation Script</h2>
    <pre>
# Using ImageMagick to generate icons from a source image
# Install: sudo apt-get install imagemagick (Linux) or brew install imagemagick (Mac)

# Create icons directory
mkdir -p icons

# Generate icons from source image (replace logo.png with your file)
convert logo.png -resize 72x72 icons/icon-72x72.png
convert logo.png -resize 96x96 icons/icon-96x96.png
convert logo.png -resize 128x128 icons/icon-128x128.png
convert logo.png -resize 144x144 icons/icon-144x144.png
convert logo.png -resize 152x152 icons/icon-152x152.png
convert logo.png -resize 192x192 icons/icon-192x192.png
convert logo.png -resize 384x384 icons/icon-384x384.png
convert logo.png -resize 512x512 icons/icon-512x512.png
    </pre>

    <h2>Manifest.json Icon Configuration</h2>
    <pre>
"icons": [
    {
        "src": "/icons/icon-72x72.png",
        "sizes": "72x72",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-96x96.png",
        "sizes": "96x96",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-128x128.png",
        "sizes": "128x128",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-144x144.png",
        "sizes": "144x144",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-152x152.png",
        "sizes": "152x152",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-192x192.png",
        "sizes": "192x192",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-384x384.png",
        "sizes": "384x384",
        "type": "image/png"
    },
    {
        "src": "/icons/icon-512x512.png",
        "sizes": "512x512",
        "type": "image/png",
        "purpose": "any maskable"
    }
]
    </pre>
</body>
</html>`;

// Write instructions file
fs.writeFileSync(path.join(iconsDir, 'icon-generation-guide.html'), instructionsHTML);

console.log('\nCreated icon generation guide at: icons/icon-generation-guide.html');
console.log('Open this file in a browser for detailed instructions.');