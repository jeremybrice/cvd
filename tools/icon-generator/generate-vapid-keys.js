// Script to generate VAPID keys for Web Push notifications
// Run this script to generate keys, then add them to your environment variables

const crypto = require('crypto');
const { promisify } = require('util');

// Generate VAPID keys
async function generateVAPIDKeys() {
    const { publicKey, privateKey } = crypto.generateKeyPairSync('ec', {
        namedCurve: 'prime256v1',
        publicKeyEncoding: {
            type: 'spki',
            format: 'der'
        },
        privateKeyEncoding: {
            type: 'pkcs8',
            format: 'der'
        }
    });

    // Convert to base64url format
    const publicKeyBase64 = publicKey.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');

    const privateKeyBase64 = privateKey.toString('base64')
        .replace(/\+/g, '-')
        .replace(/\//g, '_')
        .replace(/=/g, '');

    console.log('=================================');
    console.log('VAPID Keys Generated Successfully');
    console.log('=================================\n');
    
    console.log('Add these to your environment variables:\n');
    console.log(`VAPID_PUBLIC_KEY="${publicKeyBase64}"`);
    console.log(`VAPID_PRIVATE_KEY="${privateKeyBase64}"`);
    console.log(`VAPID_SUBJECT="mailto:admin@cvd.com"\n`);
    
    console.log('For Flask app.py, add to your environment:');
    console.log('----------------------------------------');
    console.log(`export VAPID_PUBLIC_KEY="${publicKeyBase64}"`);
    console.log(`export VAPID_PRIVATE_KEY="${privateKeyBase64}"`);
    console.log(`export VAPID_SUBJECT="mailto:admin@cvd.com"\n`);
    
    console.log('For the frontend push-manager.js:');
    console.log('--------------------------------');
    console.log(`vapidPublicKey: '${publicKeyBase64}'\n`);
    
    console.log('Security Notes:');
    console.log('--------------');
    console.log('1. Keep the PRIVATE key secure - never commit it to version control');
    console.log('2. The PUBLIC key can be safely shared with clients');
    console.log('3. Update the VAPID_SUBJECT email to your actual contact email');
    console.log('4. Consider using a .env file for local development');
    
    // Create .env.example file
    const envExample = `# Web Push VAPID Keys
# Generate new keys with: node generate-vapid-keys.js
VAPID_PUBLIC_KEY=your_public_key_here
VAPID_PRIVATE_KEY=your_private_key_here
VAPID_SUBJECT=mailto:your-email@example.com

# Anthropic API Key (for AI chat bot)
ANTHROPIC_API_KEY=your_anthropic_api_key_here`;

    require('fs').writeFileSync('.env.example', envExample);
    console.log('\nCreated .env.example file for reference');
}

// Alternative method using web-push library (if installed)
function generateWithWebPush() {
    try {
        const webpush = require('web-push');
        const vapidKeys = webpush.generateVAPIDKeys();
        
        console.log('\n=================================');
        console.log('Alternative: Using web-push library');
        console.log('=================================\n');
        console.log('Public Key:', vapidKeys.publicKey);
        console.log('Private Key:', vapidKeys.privateKey);
        
    } catch (e) {
        console.log('\nTo use web-push for key generation:');
        console.log('npm install -g web-push');
        console.log('web-push generate-vapid-keys');
    }
}

// Run generation
generateVAPIDKeys();
generateWithWebPush();