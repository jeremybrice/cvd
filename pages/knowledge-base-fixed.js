/**
 * Knowledge Base Controller for CVD System - FIXED VERSION
 * Manages knowledge base interface, search, and article viewing
 */

class KnowledgeBaseController {
    constructor() {
        // Don't initialize API or call init() immediately
        this.articles = [];
        this.categories = [];
        this.currentView = 'categories';
        this.currentCategory = null;
        this.currentArticle = null;
        this.searchTimeout = null;
        this.initialized = false;
        
        // Flag to track if we're in the middle of initialization
        this.initializing = false;
    }
    
    async init() {
        // Prevent double initialization
        if (this.initialized || this.initializing) {
            return;
        }
        
        this.initializing = true;
        
        try {
            // Show loading immediately
            this.showLoading(true);
            
            // Step 1: Verify authentication first
            console.log('KB: Starting authentication check...');
            const authResult = await checkNonDriverAccess();
            if (!authResult) {
                // Authentication failed, checkNonDriverAccess handles redirect
                console.log('KB: Authentication check failed, redirect should happen');
                return;
            }
            console.log('KB: Authentication check passed');
            
            // Step 2: Initialize API client AFTER auth check
            console.log('KB: Initializing API client...');
            this.api = new CVDApi();
            if (!this.api || typeof this.api.get !== 'function') {
                throw new Error('CVDApi failed to initialize properly');
            }
            console.log('KB: API client initialized successfully');
            
            // Step 3: Additional verification - test API access directly
            const apiTest = await this.verifyApiAccess();
            if (!apiTest) {
                console.error('API access verification failed');
                this.showError('Failed to initialize knowledge base - API access issue');
                return;
            }
            console.log('KB: API access verified');
            
            // Step 4: Load initial data
            console.log('KB: Loading initial data...');
            await this.loadInitialData();
            console.log('KB: Initial data loaded');
            
            // Step 5: Load highlight articles data
            console.log('KB: Loading highlight articles...');
            await this.loadHighlightArticles();
            console.log('KB: Highlight articles loaded');
            
            // Step 6: Setup event listeners
            console.log('KB: Setting up event listeners...');
            this.setupEventListeners();
            this.setupQuickAccessListeners();
            this.setupFeedbackListeners();
            console.log('KB: Event listeners set up');
            
            // Step 7: Show categories view initially
            console.log('KB: Showing categories view...');
            this.showCategoriesView();
            
            // Mark as initialized
            this.initialized = true;
            console.log('KB: Initialization complete');
            
        } catch (error) {
            console.error('KB Init Error:', error);
            this.showError(`Failed to initialize knowledge base: ${error.message}`);
        } finally {
            this.initializing = false;
            this.showLoading(false);
        }
    }
    
    async verifyApiAccess() {
        try {
            // Test a simple API call to verify authentication is working
            console.log('KB: Testing API access...');
            const response = await fetch('/api/auth/current-user', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                console.error('API access test failed:', response.status, response.statusText);
                return false;
            }
            
            const data = await response.json();
            console.log('KB: API access verified for user:', data.user?.username);
            return true;
        } catch (error) {
            console.error('API access verification error:', error);
            return false;
        }
    }
    
    async loadInitialData() {
        console.log('KB: Starting to load initial data...');
        
        try {
            // Load articles with improved error handling
            console.log('KB: Fetching articles...');
            const response = await this.apiWithRetry('/knowledge-base/articles');
            
            if (response && response.success) {
                this.articles = response.articles || [];
                console.log(`KB: Loaded ${this.articles.length} articles`);
                
                // Load categories separately for better organization
                console.log('KB: Fetching categories...');
                const categoriesResponse = await this.apiWithRetry('/knowledge-base/categories');
                
                if (categoriesResponse && categoriesResponse.success) {
                    this.categories = categoriesResponse.categories || [];
                    console.log(`KB: Loaded ${this.categories.length} categories`);
                } else {
                    console.warn('Categories API failed, building from articles');
                    // Build categories from articles if API fails
                    this.categories = this.buildCategoriesFromArticles();
                }
            } else {
                throw new Error(response?.error || 'Failed to load articles');
            }
            
        } catch (error) {
            console.error('Failed to load initial data:', error);
            throw new Error(`Failed to load knowledge base data: ${error.message}`);
        }
    }
    
    async apiWithRetry(endpoint, maxRetries = 2, delay = 1000) {
        for (let attempt = 0; attempt < maxRetries; attempt++) {
            try {
                console.log(`KB: API call attempt ${attempt + 1}/${maxRetries} for ${endpoint}`);
                
                // Ensure we have an API instance
                if (!this.api || typeof this.api.get !== 'function') {
                    console.log('KB: Reinitializing API client...');
                    this.api = new CVDApi();
                    if (!this.api || typeof this.api.get !== 'function') {
                        throw new Error('CVDApi initialization failed');
                    }
                }
                
                const response = await this.api.get(`/api${endpoint}`);
                
                if (response.success || response.error !== 'Authentication required') {
                    return response;
                }
                
                // If authentication failed, wait and retry
                console.warn(`KB: API auth retry ${attempt + 1}/${maxRetries} for ${endpoint}`);
                await new Promise(resolve => setTimeout(resolve, delay));
                
                // Re-verify authentication before retry
                const authCheck = await this.verifyApiAccess();
                if (!authCheck) {
                    throw new Error('Authentication verification failed on retry');
                }
                
            } catch (error) {
                console.error(`KB: API attempt ${attempt + 1} failed:`, error.message);
                if (attempt === maxRetries - 1) {
                    throw error;
                }
                await new Promise(resolve => setTimeout(resolve, delay));
            }
        }
    }
    
    buildCategoriesFromArticles() {
        const categoryMap = {};
        const categoryConfigs = {
            'Getting Started': { icon: '📚', color: '#4F46E5', description: 'Essential information for new users' },
            'Feature Tutorials': { icon: '🎯', color: '#059669', description: 'Step-by-step guides for CVD features' },
            'Troubleshooting': { icon: '🔧', color: '#DC2626', description: 'Solutions to common problems' },
            'System Administration': { icon: '⚙️', color: '#7C2D12', description: 'Advanced configuration and management' },
            'Best Practices': { icon: '⭐', color: '#9333EA', description: 'Recommended workflows and tips' }
        };
        
        this.articles.forEach(article => {
            const category = article.category;
            if (!categoryMap[category]) {
                const config = categoryConfigs[category] || {
                    icon: '📄',
                    color: '#6B7280',
                    description: `Articles about ${category}`
                };
                
                categoryMap[category] = {
                    name: category,
                    article_count: 0,
                    ...config
                };
            }
            categoryMap[category].article_count++;
        });
        
        return Object.values(categoryMap).sort((a, b) => (a.sort_order || 99) - (b.sort_order || 99));
    }
    
    showLoading(show) {
        const loadingEl = document.getElementById('loadingState');
        if (loadingEl) {
            loadingEl.style.display = show ? 'block' : 'none';
        }
    }
    
    showError(message, showRetry = true) {
        console.error('KB Error:', message);
        
        const errorEl = document.getElementById('errorState');
        if (errorEl) {
            const messageEl = errorEl.querySelector('p');
            if (messageEl) {
                messageEl.textContent = message;
            }
            
            // Add manual retry button for authentication issues
            if (showRetry) {
                const retryButton = errorEl.querySelector('.kb-error-retry');
                if (retryButton) {
                    retryButton.textContent = 'Retry Loading';
                    retryButton.onclick = () => {
                        this.hideError();
                        this.init();
                    };
                }
            }
            
            errorEl.style.display = 'block';
        }
    }
    
    hideError() {
        const errorEl = document.getElementById('errorState');
        if (errorEl) {
            errorEl.style.display = 'none';
        }
    }
    
    // ... Rest of the methods remain the same ...
    // Copy from original knowledge-base.js starting from hideAllViews()
}

// Global variable for easy access from onclick handlers
let knowledgeBase;

// Initialize on page load - but wait for DOM and scripts to be ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('KB: DOM loaded, checking for required dependencies...');
    
    // Check if required dependencies are loaded
    if (typeof CVDApi === 'undefined') {
        console.error('KB: CVDApi not loaded');
        return;
    }
    
    if (typeof checkNonDriverAccess === 'undefined') {
        console.error('KB: checkNonDriverAccess not loaded');
        return;
    }
    
    console.log('KB: All dependencies loaded, creating controller...');
    knowledgeBase = new KnowledgeBaseController();
    
    // Initialize after a small delay to ensure everything is ready
    setTimeout(() => {
        console.log('KB: Starting initialization...');
        knowledgeBase.init();
    }, 100);
});

// Make functions available globally for onclick handlers
window.showCategoriesView = () => knowledgeBase?.showCategoriesView();
window.showArticlesView = (category) => knowledgeBase?.showArticlesView(category);