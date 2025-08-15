/**
 * CVD User Avatar System
 * P2 Medium Priority - User Features Component 1
 * 
 * Profile image management with:
 * - Profile image upload and management
 * - Automatic fallback to initials
 * - Cross-frame avatar updates
 * - Avatar generation and caching
 */

class UserAvatarSystem {
    constructor() {
        this.currentUser = null;
        this.avatarCache = new Map();
        this.subscribers = [];
        this.storageKey = 'cvd_user_avatars';
        this.maxAvatarSize = 2 * 1024 * 1024; // 2MB
        this.allowedTypes = ['image/jpeg', 'image/png', 'image/webp'];
        this.avatarSize = 40; // Default size in pixels
        
        this.init();
    }

    async init() {
        await this.loadCachedAvatars();
        this.setupEventListeners();
        
        // Wait for current user to be available
        this.waitForCurrentUser();
        
        console.log('UserAvatarSystem initialized');
    }

    waitForCurrentUser() {
        if (window.currentUser) {
            this.currentUser = window.currentUser;
            this.updateAllAvatars();
        } else {
            setTimeout(() => this.waitForCurrentUser(), 100);
        }
    }

    async loadCachedAvatars() {
        try {
            const cached = localStorage.getItem(this.storageKey);
            if (cached) {
                const data = JSON.parse(cached);
                this.avatarCache = new Map(Object.entries(data));
            }
        } catch (error) {
            console.error('Error loading cached avatars:', error);
        }
    }

    async saveCachedAvatars() {
        try {
            const data = Object.fromEntries(this.avatarCache);
            localStorage.setItem(this.storageKey, JSON.stringify(data));
        } catch (error) {
            console.error('Error saving cached avatars:', error);
        }
    }

    setupEventListeners() {
        // Listen for user updates from cross-frame messages
        window.addEventListener('message', (event) => {
            if (event.origin !== window.location.origin) return;
            
            const { type, payload } = event.data;
            if (type === 'AVATAR_UPDATED') {
                this.handleAvatarUpdate(payload);
            } else if (type === 'USER_UPDATED') {
                if (payload.user) {
                    this.currentUser = { ...this.currentUser, ...payload.user };
                    this.updateAllAvatars();
                }
            }
        });
    }

    handleAvatarUpdate(payload) {
        const { userId, avatar } = payload;
        
        if (avatar) {
            this.avatarCache.set(userId.toString(), avatar);
        } else {
            this.avatarCache.delete(userId.toString());
        }
        
        this.saveCachedAvatars();
        this.updateAllAvatars();
        this.notifySubscribers('avatar_updated', { userId, avatar });
    }

    subscribe(callback) {
        this.subscribers.push(callback);
        
        return () => {
            const index = this.subscribers.indexOf(callback);
            if (index > -1) {
                this.subscribers.splice(index, 1);
            }
        };
    }

    notifySubscribers(event, data) {
        this.subscribers.forEach(callback => {
            try {
                callback(event, data);
            } catch (error) {
                console.error('Error in avatar subscriber:', error);
            }
        });
    }

    generateInitialsAvatar(username, size = this.avatarSize) {
        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');

        // Generate background color based on username
        const colors = [
            '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7',
            '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9'
        ];
        const colorIndex = this.hashString(username) % colors.length;
        const bgColor = colors[colorIndex];

        // Draw background circle
        ctx.fillStyle = bgColor;
        ctx.beginPath();
        ctx.arc(size / 2, size / 2, size / 2, 0, 2 * Math.PI);
        ctx.fill();

        // Draw initials
        const initials = this.getInitials(username);
        ctx.fillStyle = '#FFFFFF';
        ctx.font = `bold ${Math.floor(size * 0.4)}px ${getComputedStyle(document.documentElement).getPropertyValue('--font-sans')}`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText(initials, size / 2, size / 2);

        return canvas.toDataURL();
    }

    getInitials(name) {
        if (!name) return '?';
        
        const words = name.trim().split(/\s+/);
        if (words.length === 1) {
            return words[0].substring(0, 2).toUpperCase();
        }
        
        return words
            .slice(0, 2)
            .map(word => word.charAt(0))
            .join('')
            .toUpperCase();
    }

    hashString(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash; // Convert to 32-bit integer
        }
        return Math.abs(hash);
    }

    getAvatar(userId, username = null, size = this.avatarSize) {
        const userIdStr = userId ? userId.toString() : null;
        
        // Try to get cached avatar first
        if (userIdStr && this.avatarCache.has(userIdStr)) {
            const cached = this.avatarCache.get(userIdStr);
            if (cached.startsWith('data:image/')) {
                return this.resizeAvatar(cached, size);
            }
        }
        
        // Generate initials avatar as fallback
        const displayName = username || (this.currentUser && this.currentUser.id === userId ? this.currentUser.username : `User ${userId}`);
        return this.generateInitialsAvatar(displayName, size);
    }

    resizeAvatar(dataUrl, size) {
        if (size === this.avatarSize) {
            return dataUrl; // Return original if same size
        }

        const canvas = document.createElement('canvas');
        canvas.width = size;
        canvas.height = size;
        const ctx = canvas.getContext('2d');

        const img = new Image();
        img.onload = () => {
            // Draw image scaled to fit circle
            ctx.save();
            ctx.beginPath();
            ctx.arc(size / 2, size / 2, size / 2, 0, 2 * Math.PI);
            ctx.clip();
            ctx.drawImage(img, 0, 0, size, size);
            ctx.restore();
        };
        img.src = dataUrl;

        return canvas.toDataURL();
    }

    createAvatarElement(userId, username = null, size = this.avatarSize, className = '') {
        const avatar = document.createElement('div');
        avatar.className = `user-avatar ${className}`;
        avatar.style.cssText = `
            width: ${size}px;
            height: ${size}px;
            border-radius: 50%;
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            display: inline-block;
            flex-shrink: 0;
        `;

        const avatarUrl = this.getAvatar(userId, username, size);
        avatar.style.backgroundImage = `url(${avatarUrl})`;
        
        // Add data attributes for updates
        avatar.dataset.userId = userId;
        avatar.dataset.username = username || '';
        avatar.dataset.size = size;

        return avatar;
    }

    updateAllAvatars() {
        document.querySelectorAll('.user-avatar[data-user-id]').forEach(element => {
            const userId = element.dataset.userId;
            const username = element.dataset.username;
            const size = parseInt(element.dataset.size) || this.avatarSize;
            
            const avatarUrl = this.getAvatar(userId, username, size);
            element.style.backgroundImage = `url(${avatarUrl})`;
        });

        // Also update any avatar images
        document.querySelectorAll('img.user-avatar[data-user-id]').forEach(img => {
            const userId = img.dataset.userId;
            const username = img.dataset.username;
            const size = parseInt(img.dataset.size) || this.avatarSize;
            
            img.src = this.getAvatar(userId, username, size);
        });
    }

    async uploadAvatar(file, userId = null) {
        if (!userId && this.currentUser) {
            userId = this.currentUser.id;
        }
        
        if (!userId) {
            throw new Error('No user ID provided for avatar upload');
        }

        // Validate file
        if (!this.validateFile(file)) {
            throw new Error('Invalid file type or size');
        }

        // Process and resize image
        const processedImage = await this.processImage(file);
        
        try {
            // Upload to server
            if (typeof CVDApi !== 'undefined') {
                const api = new CVDApi();
                const formData = new FormData();
                formData.append('avatar', file);
                
                const response = await api.makeRequest('POST', `/user/${userId}/avatar`, formData, {
                    'Content-Type': undefined // Let browser set multipart boundary
                });
                
                if (response.avatar) {
                    // Cache the avatar
                    this.avatarCache.set(userId.toString(), response.avatar);
                    this.saveCachedAvatars();
                    
                    // Notify other frames
                    this.broadcastAvatarUpdate(userId, response.avatar);
                    
                    return response.avatar;
                }
            }
            
            // Fallback to local storage only
            this.avatarCache.set(userId.toString(), processedImage);
            this.saveCachedAvatars();
            this.broadcastAvatarUpdate(userId, processedImage);
            
            return processedImage;
            
        } catch (error) {
            console.error('Avatar upload failed:', error);
            
            // Store locally as fallback
            this.avatarCache.set(userId.toString(), processedImage);
            this.saveCachedAvatars();
            this.broadcastAvatarUpdate(userId, processedImage);
            
            if (window.ToastManager) {
                window.ToastManager.show('warning', 'Avatar saved locally only');
            }
            
            return processedImage;
        }
    }

    validateFile(file) {
        if (!file) return false;
        
        // Check file type
        if (!this.allowedTypes.includes(file.type)) {
            if (window.ToastManager) {
                window.ToastManager.show('error', 'Please select a JPEG, PNG, or WebP image');
            }
            return false;
        }
        
        // Check file size
        if (file.size > this.maxAvatarSize) {
            if (window.ToastManager) {
                window.ToastManager.show('error', 'Image must be smaller than 2MB');
            }
            return false;
        }
        
        return true;
    }

    async processImage(file) {
        return new Promise((resolve, reject) => {
            const img = new Image();
            img.onload = () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                
                // Calculate dimensions to create a square crop
                const size = Math.min(img.width, img.height);
                const startX = (img.width - size) / 2;
                const startY = (img.height - size) / 2;
                
                // Set canvas size for avatar
                const outputSize = 200; // High quality output
                canvas.width = outputSize;
                canvas.height = outputSize;
                
                // Draw circular avatar
                ctx.save();
                ctx.beginPath();
                ctx.arc(outputSize / 2, outputSize / 2, outputSize / 2, 0, 2 * Math.PI);
                ctx.clip();
                
                // Draw cropped and scaled image
                ctx.drawImage(img, startX, startY, size, size, 0, 0, outputSize, outputSize);
                ctx.restore();
                
                // Convert to data URL
                const dataUrl = canvas.toDataURL('image/jpeg', 0.85);
                resolve(dataUrl);
            };
            
            img.onerror = () => {
                reject(new Error('Failed to load image'));
            };
            
            img.src = URL.createObjectURL(file);
        });
    }

    async removeAvatar(userId = null) {
        if (!userId && this.currentUser) {
            userId = this.currentUser.id;
        }
        
        if (!userId) {
            throw new Error('No user ID provided for avatar removal');
        }

        try {
            // Remove from server
            if (typeof CVDApi !== 'undefined') {
                const api = new CVDApi();
                await api.makeRequest('DELETE', `/user/${userId}/avatar`);
            }
        } catch (error) {
            console.error('Server avatar removal failed:', error);
        }
        
        // Remove from cache
        this.avatarCache.delete(userId.toString());
        this.saveCachedAvatars();
        
        // Notify other frames
        this.broadcastAvatarUpdate(userId, null);
        
        // Update all avatar displays
        this.updateAllAvatars();
    }

    broadcastAvatarUpdate(userId, avatar) {
        const message = {
            type: 'AVATAR_UPDATED',
            payload: { userId, avatar }
        };
        
        // Broadcast to all frames
        window.parent.postMessage(message, window.location.origin);
        
        // Update local display
        this.updateAllAvatars();
        this.notifySubscribers('avatar_updated', { userId, avatar });
    }

    createAvatarUploadModal(userId = null) {
        if (!userId && this.currentUser) {
            userId = this.currentUser.id;
        }

        const modal = document.createElement('div');
        modal.className = 'avatar-upload-modal';
        modal.innerHTML = `
            <div class="avatar-modal-backdrop"></div>
            <div class="avatar-modal-content">
                <div class="avatar-modal-header">
                    <h3>Update Profile Picture</h3>
                    <button class="avatar-modal-close">×</button>
                </div>
                <div class="avatar-modal-body">
                    <div class="avatar-preview-section">
                        <div class="current-avatar">
                            ${this.createAvatarElement(userId, this.currentUser?.username, 100, 'preview-avatar').outerHTML}
                        </div>
                        <div class="avatar-actions">
                            <label class="avatar-upload-btn">
                                <input type="file" accept="${this.allowedTypes.join(',')}" class="avatar-file-input">
                                Choose Image
                            </label>
                            <button class="avatar-remove-btn" type="button">Remove</button>
                        </div>
                    </div>
                    <div class="avatar-upload-info">
                        <p>Upload a square image for the best results. Supported formats: JPEG, PNG, WebP (max 2MB)</p>
                    </div>
                    <div class="avatar-upload-progress" style="display: none;">
                        <div class="progress-bar">
                            <div class="progress-fill"></div>
                        </div>
                        <div class="progress-text">Uploading...</div>
                    </div>
                </div>
                <div class="avatar-modal-footer">
                    <button class="btn btn-secondary" data-action="cancel">Cancel</button>
                    <button class="btn btn-primary" data-action="save" style="display: none;">Save Changes</button>
                </div>
            </div>
        `;

        this.addAvatarModalStyles();
        this.attachAvatarModalEvents(modal, userId);
        
        return modal;
    }

    addAvatarModalStyles() {
        if (document.getElementById('avatar-modal-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'avatar-modal-styles';
        style.textContent = `
            .avatar-upload-modal {
                position: fixed;
                inset: 0;
                z-index: var(--z-modal);
                display: flex;
                align-items: center;
                justify-content: center;
                opacity: 0;
                visibility: hidden;
                transition: opacity var(--duration-base), visibility var(--duration-base);
            }
            
            .avatar-upload-modal.active {
                opacity: 1;
                visibility: visible;
            }
            
            .avatar-modal-backdrop {
                position: absolute;
                inset: 0;
                background: rgba(0, 0, 0, 0.5);
                cursor: pointer;
            }
            
            .avatar-modal-content {
                background: var(--color-neutral-0);
                border-radius: var(--modal-radius);
                box-shadow: var(--modal-shadow);
                width: 90vw;
                max-width: 500px;
                position: relative;
                z-index: 1;
                display: flex;
                flex-direction: column;
                max-height: 80vh;
            }
            
            .avatar-modal-header {
                padding: var(--space-lg);
                border-bottom: 1px solid var(--color-neutral-200);
                display: flex;
                justify-content: space-between;
                align-items: center;
            }
            
            .avatar-modal-header h3 {
                margin: 0;
                font-size: var(--text-lg);
                font-weight: var(--font-semibold);
            }
            
            .avatar-modal-close {
                background: none;
                border: none;
                font-size: var(--text-xl);
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                border-radius: var(--radius-md);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background var(--duration-fast);
            }
            
            .avatar-modal-close:hover {
                background: var(--color-neutral-100);
            }
            
            .avatar-modal-body {
                padding: var(--space-lg);
                overflow-y: auto;
            }
            
            .avatar-preview-section {
                display: flex;
                align-items: center;
                gap: var(--space-lg);
                margin-bottom: var(--space-lg);
            }
            
            .current-avatar {
                flex-shrink: 0;
            }
            
            .avatar-actions {
                display: flex;
                flex-direction: column;
                gap: var(--space-sm);
            }
            
            .avatar-upload-btn {
                display: inline-block;
                padding: var(--btn-padding-y) var(--btn-padding-x);
                background: var(--color-primary-500);
                color: var(--color-neutral-0);
                border-radius: var(--btn-radius);
                font-weight: var(--btn-font-weight);
                text-align: center;
                cursor: pointer;
                transition: background var(--duration-fast);
                border: none;
            }
            
            .avatar-upload-btn:hover {
                background: var(--color-primary-600);
            }
            
            .avatar-file-input {
                display: none;
            }
            
            .avatar-remove-btn {
                padding: var(--btn-padding-y) var(--btn-padding-x);
                background: var(--color-danger);
                color: var(--color-neutral-0);
                border: none;
                border-radius: var(--btn-radius);
                font-weight: var(--btn-font-weight);
                cursor: pointer;
                transition: background var(--duration-fast);
            }
            
            .avatar-remove-btn:hover {
                background: var(--color-danger);
                filter: brightness(0.9);
            }
            
            .avatar-upload-info {
                background: var(--color-info-bg);
                padding: var(--space-md);
                border-radius: var(--radius-md);
                margin-bottom: var(--space-md);
            }
            
            .avatar-upload-info p {
                margin: 0;
                font-size: var(--text-sm);
                color: var(--color-info-text);
            }
            
            .avatar-upload-progress {
                margin-top: var(--space-md);
            }
            
            .progress-bar {
                width: 100%;
                height: 8px;
                background: var(--color-neutral-200);
                border-radius: var(--radius-full);
                overflow: hidden;
                margin-bottom: var(--space-sm);
            }
            
            .progress-fill {
                height: 100%;
                background: var(--color-primary-500);
                width: 0%;
                transition: width var(--duration-base);
            }
            
            .progress-text {
                text-align: center;
                font-size: var(--text-sm);
                color: var(--color-neutral-600);
            }
            
            .avatar-modal-footer {
                padding: var(--space-lg);
                border-top: 1px solid var(--color-neutral-200);
                display: flex;
                gap: var(--space-sm);
                justify-content: flex-end;
            }
            
            .btn {
                padding: var(--btn-padding-y) var(--btn-padding-x);
                border-radius: var(--btn-radius);
                border: 1px solid;
                cursor: pointer;
                font-weight: var(--btn-font-weight);
                text-decoration: none;
                display: inline-flex;
                align-items: center;
                justify-content: center;
                transition: all var(--duration-fast);
            }
            
            .btn-primary {
                background: var(--color-primary-500);
                border-color: var(--color-primary-500);
                color: var(--color-neutral-0);
            }
            
            .btn-primary:hover {
                background: var(--color-primary-600);
                border-color: var(--color-primary-600);
            }
            
            .btn-secondary {
                background: var(--color-neutral-0);
                border-color: var(--color-neutral-300);
                color: var(--color-neutral-700);
            }
            
            .btn-secondary:hover {
                background: var(--color-neutral-50);
                border-color: var(--color-neutral-400);
            }
        `;
        
        document.head.appendChild(style);
    }

    attachAvatarModalEvents(modal, userId) {
        let pendingFile = null;
        
        const closeModal = () => {
            modal.classList.remove('active');
            setTimeout(() => modal.remove(), 300);
        };
        
        // Close handlers
        modal.querySelector('.avatar-modal-backdrop').addEventListener('click', closeModal);
        modal.querySelector('.avatar-modal-close').addEventListener('click', closeModal);
        
        // File upload handler
        const fileInput = modal.querySelector('.avatar-file-input');
        const saveBtn = modal.querySelector('[data-action="save"]');
        const progressSection = modal.querySelector('.avatar-upload-progress');
        
        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file && this.validateFile(file)) {
                pendingFile = file;
                
                // Show preview
                const reader = new FileReader();
                reader.onload = (e) => {
                    const preview = modal.querySelector('.preview-avatar');
                    if (preview) {
                        preview.style.backgroundImage = `url(${e.target.result})`;
                    }
                };
                reader.readAsDataURL(file);
                
                saveBtn.style.display = 'inline-flex';
            }
        });
        
        // Remove avatar handler
        modal.querySelector('.avatar-remove-btn').addEventListener('click', async () => {
            try {
                await this.removeAvatar(userId);
                if (window.ToastManager) {
                    window.ToastManager.show('success', 'Profile picture removed');
                }
                closeModal();
            } catch (error) {
                console.error('Remove avatar error:', error);
                if (window.ToastManager) {
                    window.ToastManager.show('error', 'Failed to remove profile picture');
                }
            }
        });
        
        // Footer actions
        modal.addEventListener('click', async (e) => {
            const action = e.target.dataset.action;
            if (!action) return;
            
            switch (action) {
                case 'cancel':
                    closeModal();
                    break;
                    
                case 'save':
                    if (!pendingFile) return;
                    
                    try {
                        progressSection.style.display = 'block';
                        const progressFill = modal.querySelector('.progress-fill');
                        
                        // Animate progress
                        progressFill.style.width = '30%';
                        
                        const avatar = await this.uploadAvatar(pendingFile, userId);
                        
                        progressFill.style.width = '100%';
                        
                        if (window.ToastManager) {
                            window.ToastManager.show('success', 'Profile picture updated');
                        }
                        
                        setTimeout(closeModal, 1000);
                        
                    } catch (error) {
                        console.error('Upload error:', error);
                        if (window.ToastManager) {
                            window.ToastManager.show('error', 'Failed to update profile picture');
                        }
                        progressSection.style.display = 'none';
                    }
                    break;
            }
        });
        
        // Keyboard support
        document.addEventListener('keydown', function escapeHandler(e) {
            if (e.key === 'Escape') {
                closeModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        });
    }

    showAvatarUploadModal(userId = null) {
        const modal = this.createAvatarUploadModal(userId);
        document.body.appendChild(modal);
        
        // Show with animation
        requestAnimationFrame(() => {
            modal.classList.add('active');
        });
    }

    // Utility method to update navigation user avatar
    updateNavigationAvatar() {
        if (!this.currentUser) return;
        
        const userButton = document.querySelector('.user-button');
        if (userButton) {
            // Look for existing avatar or create one
            let avatar = userButton.querySelector('.user-avatar');
            if (!avatar) {
                avatar = this.createAvatarElement(this.currentUser.id, this.currentUser.username, 32);
                userButton.insertBefore(avatar, userButton.firstChild);
            } else {
                const avatarUrl = this.getAvatar(this.currentUser.id, this.currentUser.username, 32);
                avatar.style.backgroundImage = `url(${avatarUrl})`;
            }
            
            // Make avatar clickable to open upload modal
            avatar.style.cursor = 'pointer';
            avatar.addEventListener('click', (e) => {
                e.stopPropagation();
                this.showAvatarUploadModal(this.currentUser.id);
            });
        }
    }

    // Integration method for profile pages
    setupProfileAvatarSection(container, userId = null) {
        if (!userId && this.currentUser) {
            userId = this.currentUser.id;
        }

        const avatarSection = document.createElement('div');
        avatarSection.className = 'profile-avatar-section';
        avatarSection.innerHTML = `
            <div class="profile-avatar-container">
                ${this.createAvatarElement(userId, this.currentUser?.username, 120).outerHTML}
                <button class="avatar-change-btn" type="button">Change Picture</button>
            </div>
        `;

        const changeBtn = avatarSection.querySelector('.avatar-change-btn');
        changeBtn.addEventListener('click', () => {
            this.showAvatarUploadModal(userId);
        });

        container.appendChild(avatarSection);
        return avatarSection;
    }

    // Clear all cached avatars (for admin use)
    clearCache() {
        this.avatarCache.clear();
        localStorage.removeItem(this.storageKey);
        this.updateAllAvatars();
        
        if (window.ToastManager) {
            window.ToastManager.show('info', 'Avatar cache cleared');
        }
    }

    // Get avatar statistics
    getStats() {
        return {
            cachedAvatars: this.avatarCache.size,
            cacheSize: new Blob([localStorage.getItem(this.storageKey) || '{}']).size,
            subscribers: this.subscribers.length
        };
    }
}

// Initialize global instance
window.UserAvatarSystem = new UserAvatarSystem();

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UserAvatarSystem;
}