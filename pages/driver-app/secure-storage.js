// Secure storage with encryption for sensitive offline data
class SecureStorage {
    constructor() {
        this.initialized = false;
        this.keyName = 'cvd-driver-key';
    }

    async init() {
        // Check if Web Crypto API is available
        if (!window.crypto || !window.crypto.subtle) {
            console.warn('Web Crypto API not available - falling back to standard storage');
            this.initialized = false;
            return;
        }

        try {
            // Test encryption capability
            const testKey = await this.generateKey();
            const testData = { test: 'data' };
            const encrypted = await this.encrypt(testData, testKey);
            const decrypted = await this.decrypt(encrypted, testKey);
            
            if (decrypted.test === 'data') {
                this.initialized = true;
                console.log('Secure storage initialized');
            }
        } catch (error) {
            console.error('Secure storage initialization failed:', error);
            this.initialized = false;
        }
    }

    async encrypt(data, key = null) {
        if (!this.initialized) {
            // Fallback to base64 encoding
            return btoa(JSON.stringify(data));
        }

        try {
            const encoder = new TextEncoder();
            const dataBuffer = encoder.encode(JSON.stringify(data));
            
            // Use provided key or get user key
            const cryptoKey = key || await this.getUserKey();
            
            // Generate initialization vector
            const iv = crypto.getRandomValues(new Uint8Array(12));
            
            // Encrypt the data
            const encrypted = await crypto.subtle.encrypt(
                { name: 'AES-GCM', iv },
                cryptoKey,
                dataBuffer
            );
            
            // Combine IV and encrypted data for storage
            return {
                iv: Array.from(iv),
                data: Array.from(new Uint8Array(encrypted)),
                encrypted: true
            };
        } catch (error) {
            console.error('Encryption failed:', error);
            // Fallback to base64
            return btoa(JSON.stringify(data));
        }
    }

    async decrypt(encryptedData, key = null) {
        if (!this.initialized || typeof encryptedData === 'string') {
            // Fallback for base64 encoded data
            try {
                return JSON.parse(atob(encryptedData));
            } catch {
                return encryptedData;
            }
        }

        try {
            // Use provided key or get user key
            const cryptoKey = key || await this.getUserKey();
            
            const decrypted = await crypto.subtle.decrypt(
                { name: 'AES-GCM', iv: new Uint8Array(encryptedData.iv) },
                cryptoKey,
                new Uint8Array(encryptedData.data)
            );
            
            const decoder = new TextDecoder();
            return JSON.parse(decoder.decode(decrypted));
        } catch (error) {
            console.error('Decryption failed:', error);
            return null;
        }
    }

    async generateKey() {
        return crypto.subtle.generateKey(
            { name: 'AES-GCM', length: 256 },
            true,
            ['encrypt', 'decrypt']
        );
    }

    async getUserKey() {
        // Check if we have a stored key
        let keyData = await this.getStoredKey();
        
        if (!keyData) {
            // Generate new key for user
            const key = await this.generateKey();
            await this.storeKey(key);
            return key;
        }
        
        // Import the stored key
        return crypto.subtle.importKey(
            'jwk',
            keyData,
            { name: 'AES-GCM', length: 256 },
            true,
            ['encrypt', 'decrypt']
        );
    }

    async storeKey(key) {
        const exported = await crypto.subtle.exportKey('jwk', key);
        
        // In production, this should be derived from user credentials
        // For now, store in localStorage with user-specific key
        const userId = window.currentUser?.id || 'default';
        localStorage.setItem(`${this.keyName}-${userId}`, JSON.stringify(exported));
    }

    async getStoredKey() {
        const userId = window.currentUser?.id || 'default';
        const stored = localStorage.getItem(`${this.keyName}-${userId}`);
        return stored ? JSON.parse(stored) : null;
    }

    // Secure session data
    async secureSession(sessionData) {
        const encrypted = await this.encrypt(sessionData);
        sessionStorage.setItem('cvd-secure-session', JSON.stringify(encrypted));
    }

    async getSecureSession() {
        const stored = sessionStorage.getItem('cvd-secure-session');
        if (!stored) return null;
        
        try {
            const encrypted = JSON.parse(stored);
            return await this.decrypt(encrypted);
        } catch {
            return null;
        }
    }

    // Clear all secure data on logout
    async clearSecureData() {
        const userId = window.currentUser?.id || 'default';
        localStorage.removeItem(`${this.keyName}-${userId}`);
        sessionStorage.removeItem('cvd-secure-session');
    }

    // Encrypt sensitive fields in an object
    async encryptSensitiveFields(data, sensitiveFields = ['password', 'pin', 'ssn', 'creditCard']) {
        const result = { ...data };
        
        for (const field of sensitiveFields) {
            if (result[field]) {
                result[field] = await this.encrypt(result[field]);
            }
        }
        
        return result;
    }

    // Decrypt sensitive fields in an object
    async decryptSensitiveFields(data, sensitiveFields = ['password', 'pin', 'ssn', 'creditCard']) {
        const result = { ...data };
        
        for (const field of sensitiveFields) {
            if (result[field]) {
                result[field] = await this.decrypt(result[field]);
            }
        }
        
        return result;
    }
}

// Create singleton instance
const secureStorage = new SecureStorage();