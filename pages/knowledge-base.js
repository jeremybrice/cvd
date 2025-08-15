/**
 * Knowledge Base Controller for CVD System
 * Manages knowledge base interface, search, and article viewing
 */

class KnowledgeBaseController {
    constructor() {
        // Don't initialize API or call init() immediately
        this.articles = [];
        this.categories = [];
        this.currentView = 'categories'; // 'categories', 'articles', 'article', 'search'
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
            const response = await fetch('/api/auth/current-user', {
                credentials: 'include'
            });
            
            if (!response.ok) {
                console.error('API access test failed:', response.status);
                return false;
            }
            
            const data = await response.json();
            console.log('API access verified for user:', data.user?.username);
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
            const response = await this.api.getKnowledgeBaseArticles();
            
            if (response && response.success) {
                this.articles = response.articles || [];
                console.log(`KB: Loaded ${this.articles.length} articles`);
                
                // Load categories separately for better organization
                console.log('KB: Fetching categories...');
                const categoriesResponse = await this.api.getKnowledgeBaseCategories();
                
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
    
    
    buildCategoriesFromArticles() {
        const categoryMap = {};
        const categoryConfigs = {
            'Getting Started': { icon: '', color: '#4F46E5', description: 'Essential information for new users' },
            'Feature Tutorials': { icon: '', color: '#059669', description: 'Step-by-step guides for CVD features' },
            'Troubleshooting': { icon: '', color: '#DC2626', description: 'Solutions to common problems' },
            'System Administration': { icon: '', color: '#7C2D12', description: 'Advanced configuration and management' },
            'Best Practices': { icon: '', color: '#9333EA', description: 'Recommended workflows and tips' }
        };
        
        this.articles.forEach(article => {
            const category = article.category;
            if (!categoryMap[category]) {
                const config = categoryConfigs[category] || {
                    icon: '',
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
        
        return Object.values(categoryMap).sort((a, b) => a.sort_order - b.sort_order);
    }
    
    setupEventListeners() {
        // Search input with debouncing
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                const query = e.target.value;
                this.updateSearchClearButton(query);
                
                clearTimeout(this.searchTimeout);
                this.searchTimeout = setTimeout(() => {
                    if (query.length >= 2) {
                        this.showAutocomplete(query);
                        this.performSearch(query);
                    } else {
                        this.hideAutocomplete();
                        this.showCategoriesView();
                    }
                }, 300);
            });
            
            // Show filters when typing
            searchInput.addEventListener('focus', () => {
                this.showSearchFilters(true);
            });
            
            // Handle keyboard navigation for autocomplete
            searchInput.addEventListener('keydown', (e) => {
                this.handleSearchKeyDown(e);
            });
            
            // Hide autocomplete when focus is lost
            searchInput.addEventListener('blur', (e) => {
                setTimeout(() => this.hideAutocomplete(), 100);
            });
        }
        
        // Search clear button
        const searchClear = document.getElementById('searchClear');
        if (searchClear) {
            searchClear.addEventListener('click', () => {
                this.clearSearch();
            });
        }
        
        // Search filters
        const categoryFilter = document.getElementById('categoryFilter');
        const difficultyFilter = document.getElementById('difficultyFilter');
        
        if (categoryFilter) {
            categoryFilter.addEventListener('change', () => {
                this.updateSearchFilters();
                this.updateFiltersClearButton();
            });
        }
        
        if (difficultyFilter) {
            difficultyFilter.addEventListener('change', () => {
                this.updateSearchFilters();
                this.updateFiltersClearButton();
            });
        }
        
        // Filters clear button
        const filtersClear = document.getElementById('filtersClear');
        if (filtersClear) {
            filtersClear.addEventListener('click', () => {
                this.clearFilters();
            });
        }
        
        // Article back button
        const articleBackButton = document.getElementById('articleBackButton');
        if (articleBackButton) {
            articleBackButton.addEventListener('click', () => {
                if (this.currentCategory) {
                    this.showArticlesView(this.currentCategory);
                } else {
                    this.showCategoriesView();
                }
            });
        }
        
        // Navigation buttons
        const prevButton = document.getElementById('prevArticle');
        const nextButton = document.getElementById('nextArticle');
        
        if (prevButton) {
            prevButton.addEventListener('click', () => this.navigateToPreviousArticle());
        }
        
        if (nextButton) {
            nextButton.addEventListener('click', () => this.navigateToNextArticle());
        }
        
        // Handle browser back/forward (if needed for future hash navigation)
        window.addEventListener('popstate', (e) => {
            if (e.state) {
                this.handleStateChange(e.state);
            }
        });
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
            
            // Add manual retry button
            if (showRetry) {
                const retryButton = errorEl.querySelector('.kb-error-retry');
                if (retryButton) {
                    retryButton.textContent = 'Retry Loading';
                    retryButton.onclick = () => {
                        this.hideError();
                        // Reset initialization flags before retrying
                        this.initialized = false;
                        this.initializing = false;
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
    
    hideAllViews() {
        const views = ['categoriesView', 'searchResults', 'articleListView', 'articleView'];
        views.forEach(viewId => {
            const element = document.getElementById(viewId);
            if (element) {
                element.style.display = 'none';
            }
        });
    }
    
    showCategoriesView() {
        this.hideAllViews();
        this.hideError();
        
        const categoriesView = document.getElementById('categoriesView');
        const categoriesGrid = document.getElementById('categoriesGrid');
        
        if (categoriesView && categoriesGrid) {
            categoriesView.style.display = 'block';
            this.renderCategories(categoriesGrid);
            
            // Render highlight articles
            this.renderHighlightArticles();
        }
        
        // Clear search
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
        }
        this.showSearchFilters(false);
        
        this.currentView = 'categories';
        this.currentCategory = null;
    }
    
    renderCategories(container) {
        container.innerHTML = '';
        container.setAttribute('role', 'list');
        
        this.categories.forEach(category => {
            const card = document.createElement('div');
            card.className = 'kb-category-card';
            card.style.borderLeftColor = category.color;
            card.setAttribute('role', 'listitem');
            card.setAttribute('tabindex', '0');
            card.setAttribute('aria-label', `Browse ${category.name} category with ${category.article_count} articles`);
            
            card.innerHTML = `
                ${category.icon ? `<span class="kb-category-icon" aria-hidden="true">${category.icon}</span>` : ''}
                <h3 class="kb-category-title">${this.escapeHtml(category.name)}</h3>
                <p class="kb-category-description">${this.escapeHtml(category.description || '')}</p>
                <span class="kb-category-count">${category.article_count} article${category.article_count !== 1 ? 's' : ''}</span>
            `;
            
            const clickHandler = () => this.showArticlesView(category.name);
            card.addEventListener('click', clickHandler);
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    clickHandler();
                }
            });
            
            container.appendChild(card);
        });
    }
    
    showArticlesView(categoryName) {
        this.hideAllViews();
        this.hideError();
        
        const articleListView = document.getElementById('articleListView');
        const breadcrumb = document.getElementById('breadcrumb');
        const categoryTitle = document.getElementById('categoryTitle');
        const articlesList = document.getElementById('articlesList');
        
        if (articleListView && breadcrumb && categoryTitle && articlesList) {
            // Update breadcrumb and title
            breadcrumb.innerHTML = `<a href="#" onclick="knowledgeBase.showCategoriesView()">Knowledge Base</a> → ${this.escapeHtml(categoryName)}`;
            categoryTitle.textContent = categoryName;
            
            // Filter articles by category
            const categoryArticles = this.articles.filter(article => article.category === categoryName);
            
            // Render articles
            this.renderArticlesList(articlesList, categoryArticles);
            
            articleListView.style.display = 'block';
        }
        
        this.currentView = 'articles';
        this.currentCategory = categoryName;
    }
    
    renderArticlesList(container, articles) {
        container.innerHTML = '';
        
        if (articles.length === 0) {
            container.innerHTML = `
                <div class="kb-empty-state">
                    <h3>No articles found</h3>
                    <p>There are no articles in this category yet.</p>
                </div>
            `;
            return;
        }
        
        articles.forEach(article => {
            const item = document.createElement('div');
            item.className = 'kb-article-item';
            
            const difficultyClass = `kb-difficulty-${article.difficulty.toLowerCase()}`;
            
            item.innerHTML = `
                <h3 class="kb-article-title">${this.escapeHtml(article.title)}</h3>
                <div class="kb-article-meta">
                    <span>By ${this.escapeHtml(article.author || 'Unknown')}</span>
                    <span class="kb-difficulty-badge ${difficultyClass}">
                        ${this.escapeHtml(article.difficulty)}
                    </span>
                    <span>${article.read_time_minutes || 1} min read</span>
                </div>
                <p class="kb-article-description">${this.escapeHtml(article.description || article.content_preview || '')}</p>
            `;
            
            item.addEventListener('click', () => this.showArticle(article.id));
            container.appendChild(item);
        });
    }
    
    async showArticle(articleId) {
        this.showLoading(true);
        
        try {
            const response = await this.api.getKnowledgeBaseArticle(articleId);
            
            if (response.success && response.article) {
                this.renderArticleView(response.article);
                this.currentArticle = articleId;
                this.currentView = 'article';
            } else {
                throw new Error(response.error || 'Article not found');
            }
            
        } catch (error) {
            console.error('Article Load Error:', error);
            this.showError('Failed to load article');
        } finally {
            this.showLoading(false);
        }
    }
    
    renderArticleView(article) {
        this.hideAllViews();
        this.hideError();
        
        const articleView = document.getElementById('articleView');
        const articleBreadcrumb = document.getElementById('articleBreadcrumb');
        const articleMetadata = document.getElementById('articleMetadata');
        const articleContent = document.getElementById('articleContent');
        
        if (articleView && articleBreadcrumb && articleMetadata && articleContent) {
            // Update breadcrumb
            const navigation = article.navigation || {};
            const metadata = article.metadata || article; // Handle nested metadata
            const breadcrumb = navigation.breadcrumb || ['Knowledge Base', metadata.category || article.category, article.title];
            articleBreadcrumb.innerHTML = breadcrumb.map((crumb, index) => {
                if (index === 0) {
                    return `<a href="#" onclick="knowledgeBase.showCategoriesView()">${this.escapeHtml(crumb)}</a>`;
                } else if (index === 1 && index < breadcrumb.length - 1) {
                    return `<a href="#" onclick="knowledgeBase.showArticlesView('${this.escapeHtml(crumb)}')">${this.escapeHtml(crumb)}</a>`;
                }
                return this.escapeHtml(crumb);
            }).join(' → ');
            
            // Update metadata - handle nested metadata structure from backend
            const metadataObj = article.metadata || article; // Fallback to article object if no nested metadata
            const lastUpdated = new Date(metadataObj.last_updated || article.last_updated).toLocaleDateString();
            const difficultyClass = `kb-difficulty-${(metadataObj.difficulty || article.difficulty).toLowerCase()}`;
            
            articleMetadata.innerHTML = `
                <div><strong>Author:</strong> ${this.escapeHtml(metadataObj.author || article.author)}</div>
                <div><strong>Category:</strong> ${this.escapeHtml(metadataObj.category || article.category)}</div>
                <div><strong>Difficulty:</strong> 
                    <span class="kb-difficulty-badge ${difficultyClass}">
                        ${this.escapeHtml(metadataObj.difficulty || article.difficulty)}
                    </span>
                </div>
                <div><strong>Updated:</strong> ${lastUpdated}</div>
                <div><strong>Read Time:</strong> ${metadataObj.read_time_minutes || article.read_time_minutes || 1} min</div>
                <div><strong>Words:</strong> ${metadataObj.word_count || article.word_count || 0}</div>
            `;
            
            // Use content_html from backend if available, otherwise try content_raw or content
            let contentHtml = article.content_html || article.content_raw || article.content;
            
            // If we got raw markdown and marked.js is available, convert it
            if (!article.content_html && article.content_raw && typeof marked !== 'undefined') {
                contentHtml = marked.parse(article.content_raw);
            } else if (!article.content_html && !article.content_raw && article.content && typeof marked !== 'undefined') {
                contentHtml = marked.parse(article.content);
            }
            
            articleContent.innerHTML = contentHtml;
            
            // Update navigation buttons
            this.updateArticleNavigation(navigation);
            
            // Generate table of contents
            this.generateTableOfContents(articleContent);
            
            articleView.style.display = 'block';
            
            // Scroll to top
            window.scrollTo(0, 0);
        }
    }
    
    updateArticleNavigation(navigation) {
        const prevButton = document.getElementById('prevArticle');
        const nextButton = document.getElementById('nextArticle');
        
        if (prevButton) {
            if (navigation.previous_article) {
                prevButton.style.visibility = 'visible';
                prevButton.onclick = () => this.showArticle(navigation.previous_article);
            } else {
                prevButton.style.visibility = 'hidden';
            }
        }
        
        if (nextButton) {
            if (navigation.next_article) {
                nextButton.style.visibility = 'visible';
                nextButton.onclick = () => this.showArticle(navigation.next_article);
            } else {
                nextButton.style.visibility = 'hidden';
            }
        }
    }
    
    async performSearch(query) {
        if (!query || query.length < 2) {
            this.showCategoriesView();
            return;
        }
        
        try {
            const categoryFilter = document.getElementById('categoryFilter')?.value || '';
            const difficultyFilter = document.getElementById('difficultyFilter')?.value || '';
            
            const response = await this.api.searchKnowledgeBase(
                query, 
                categoryFilter || null, 
                difficultyFilter || null
            );
            
            if (response.success) {
                this.renderSearchResults(query, response.results, response.search_time_ms);
                this.currentView = 'search';
            } else {
                throw new Error(response.error || 'Search failed');
            }
            
        } catch (error) {
            console.error('Search Error:', error);
            this.showError('Search failed. Please try again.');
        }
    }
    
    renderSearchResults(query, results, searchTime) {
        this.hideAllViews();
        this.hideError();
        
        const searchResults = document.getElementById('searchResults');
        const searchResultsTitle = document.getElementById('searchResultsTitle');
        const searchResultsList = document.getElementById('searchResultsList');
        
        if (searchResults && searchResultsTitle && searchResultsList) {
            // Update title
            searchResultsTitle.textContent = `Search Results for "${query}" (${results.length} results, ${searchTime.toFixed(0)}ms)`;
            
            // Render results
            searchResultsList.innerHTML = '';
            
            if (results.length === 0) {
                searchResultsList.innerHTML = `
                    <div class="kb-empty-state">
                        <h3>No results found</h3>
                        <p>Try different keywords or browse by category.</p>
                    </div>
                `;
            } else {
                results.forEach(result => {
                    const item = document.createElement('div');
                    item.className = 'kb-search-result-item';
                    
                    const difficultyClass = `kb-difficulty-${result.difficulty.toLowerCase()}`;
                    
                    item.innerHTML = `
                        <h3 class="kb-article-title">${this.escapeHtml(result.title)}</h3>
                        <div class="kb-article-meta">
                            <span>${this.escapeHtml(result.category)}</span>
                            <span class="kb-difficulty-badge ${difficultyClass}">
                                ${this.escapeHtml(result.difficulty)}
                            </span>
                            <span>${result.read_time_minutes || 1} min read</span>
                            <span>Score: ${result.score}</span>
                        </div>
                        <div class="kb-search-snippet">${result.snippet || this.escapeHtml(result.description)}</div>
                    `;
                    
                    item.addEventListener('click', () => this.showArticle(result.id));
                    searchResultsList.appendChild(item);
                });
            }
            
            searchResults.style.display = 'block';
        }
    }
    
    showSearchFilters(show) {
        const filtersEl = document.getElementById('searchFilters');
        if (filtersEl) {
            filtersEl.style.display = show ? 'flex' : 'none';
        }
        
        // Populate category filter if showing
        if (show) {
            this.populateCategoryFilter();
        }
    }
    
    populateCategoryFilter() {
        const categoryFilter = document.getElementById('categoryFilter');
        if (categoryFilter && this.categories.length > 0) {
            // Only populate if empty
            if (categoryFilter.options.length <= 1) {
                this.categories.forEach(category => {
                    const option = document.createElement('option');
                    option.value = category.name;
                    option.textContent = category.name;
                    categoryFilter.appendChild(option);
                });
            }
        }
    }
    
    updateSearchFilters() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput && searchInput.value.length >= 2) {
            this.performSearch(searchInput.value);
        }
    }
    
    navigateToPreviousArticle() {
        // This will be handled by the onclick set in updateArticleNavigation
    }
    
    navigateToNextArticle() {
        // This will be handled by the onclick set in updateArticleNavigation
    }
    
    handleStateChange(state) {
        // Handle browser back/forward if implementing hash navigation
        switch (state.view) {
            case 'categories':
                this.showCategoriesView();
                break;
            case 'articles':
                this.showArticlesView(state.category);
                break;
            case 'article':
                this.showArticle(state.articleId);
                break;
            case 'search':
                this.performSearch(state.query);
                break;
        }
    }
    
    escapeHtml(text) {
        if (typeof text !== 'string') return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // New methods for enhanced functionality
    async loadHighlightArticles() {
        try {
            // Get recent articles (last 5 updated)
            const recentSorted = [...this.articles]
                .sort((a, b) => new Date(b.last_updated) - new Date(a.last_updated))
                .slice(0, 5);
            this.recentArticles = recentSorted;
            
            // Get popular articles (mock data since we don't have view counts yet)
            // In a real implementation, this would use analytics data
            const popularSorted = [...this.articles]
                .sort((a, b) => (b.view_count || 0) - (a.view_count || 0))
                .slice(0, 5);
            this.popularArticles = popularSorted.length > 0 ? popularSorted : recentSorted;
            
        } catch (error) {
            console.warn('Failed to load highlight articles:', error);
            this.recentArticles = this.articles.slice(0, 5);
            this.popularArticles = this.articles.slice(0, 5);
        }
    }
    
    renderHighlightArticles() {
        this.renderHighlightSection('recentArticles', this.recentArticles);
        this.renderHighlightSection('popularArticles', this.popularArticles);
    }
    
    renderHighlightSection(containerId, articles) {
        const container = document.getElementById(containerId);
        if (!container || !articles.length) return;
        
        container.innerHTML = '';
        
        articles.slice(0, 5).forEach(article => {
            const item = document.createElement('div');
            item.className = 'kb-highlight-article';
            
            const link = document.createElement('a');
            link.className = 'kb-highlight-article-link';
            link.href = '#';
            link.textContent = article.title;
            link.setAttribute('aria-label', `Read article: ${article.title}`);
            
            const meta = document.createElement('div');
            meta.className = 'kb-highlight-article-meta';
            meta.textContent = `${article.category} • ${article.read_time_minutes || 1} min read`;
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                this.showArticle(article.id);
            });
            
            item.appendChild(link);
            item.appendChild(meta);
            container.appendChild(item);
        });
    }
    
    setupQuickAccessListeners() {
        document.querySelectorAll('.kb-quick-access-card').forEach(card => {
            const clickHandler = (e) => {
                e.preventDefault();
                const action = card.dataset.action;
                this.handleQuickAccessClick(action);
            };
            
            card.addEventListener('click', clickHandler);
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    clickHandler(e);
                }
            });
        });
    }
    
    handleQuickAccessClick(action) {
        switch (action) {
            case 'getting-started':
                this.showArticlesView('Getting Started');
                break;
            case 'common-issues':
                this.showArticlesView('Troubleshooting');
                break;
            case 'whats-new':
                // Show recent articles or search for "new"
                this.performSearch('new features');
                break;
            default:
                console.warn('Unknown quick access action:', action);
        }
    }
    
    generateTableOfContents(contentElement) {
        const tocContainer = document.getElementById('tableOfContents');
        const tocNav = tocContainer?.querySelector('.kb-toc-nav');
        
        if (!tocContainer || !tocNav) return;
        
        // Find all headings in the content
        const headings = contentElement.querySelectorAll('h1, h2, h3, h4');
        
        if (headings.length === 0) {
            tocContainer.style.display = 'none';
            return;
        }
        
        tocContainer.style.display = 'block';
        tocNav.innerHTML = '';
        
        headings.forEach((heading, index) => {
            // Generate an ID if it doesn't have one
            if (!heading.id) {
                heading.id = `heading-${index}`;
            }
            
            const link = document.createElement('a');
            link.href = `#${heading.id}`;
            link.textContent = heading.textContent;
            link.className = `toc-${heading.tagName.toLowerCase()}`;
            
            link.addEventListener('click', (e) => {
                e.preventDefault();
                heading.scrollIntoView({ behavior: 'smooth' });
                
                // Update active TOC item
                tocNav.querySelectorAll('a').forEach(a => a.classList.remove('active'));
                link.classList.add('active');
            });
            
            tocNav.appendChild(link);
        });
        
        // Add scroll spy functionality
        this.setupScrollSpy(headings, tocNav);
    }
    
    setupScrollSpy(headings, tocNav) {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const activeLink = tocNav.querySelector(`a[href="#${entry.target.id}"]`);
                        if (activeLink) {
                            tocNav.querySelectorAll('a').forEach(a => a.classList.remove('active'));
                            activeLink.classList.add('active');
                        }
                    }
                });
            },
            { rootMargin: '-20% 0px -80% 0px' }
        );
        
        headings.forEach(heading => observer.observe(heading));
    }
    
    setupFeedbackListeners() {
        const feedbackPositive = document.getElementById('feedbackPositive');
        const feedbackNegative = document.getElementById('feedbackNegative');
        const feedbackSubmit = document.getElementById('feedbackSubmit');
        const feedbackCancel = document.getElementById('feedbackCancel');
        
        if (feedbackPositive) {
            feedbackPositive.addEventListener('click', () => this.handleFeedback('positive'));
        }
        
        if (feedbackNegative) {
            feedbackNegative.addEventListener('click', () => this.handleFeedback('negative'));
        }
        
        if (feedbackSubmit) {
            feedbackSubmit.addEventListener('click', () => this.submitFeedback());
        }
        
        if (feedbackCancel) {
            feedbackCancel.addEventListener('click', () => this.cancelFeedback());
        }
    }
    
    handleFeedback(type) {
        const positiveButton = document.getElementById('feedbackPositive');
        const negativeButton = document.getElementById('feedbackNegative');
        const feedbackForm = document.getElementById('feedbackForm');
        
        // Update button states
        [positiveButton, negativeButton].forEach(btn => btn?.classList.remove('selected'));
        
        if (type === 'positive') {
            positiveButton?.classList.add('selected');
            // For positive feedback, just show thanks
            this.showFeedbackThanks();
        } else {
            negativeButton?.classList.add('selected');
            // For negative feedback, show form
            if (feedbackForm) {
                feedbackForm.style.display = 'block';
                feedbackForm.querySelector('textarea')?.focus();
            }
        }
        
        // Store feedback type
        this.currentFeedbackType = type;
    }
    
    async submitFeedback() {
        const textarea = document.getElementById('feedbackComment');
        const comment = textarea?.value.trim() || '';
        
        try {
            // Send feedback to server (implement API call)
            const feedbackData = {
                article_id: this.currentArticle,
                type: this.currentFeedbackType,
                comment: comment,
                timestamp: new Date().toISOString()
            };
            
            console.log('Feedback submitted:', feedbackData);
            // TODO: Implement API call
            // await this.api.post('/api/knowledge-base/feedback', feedbackData);
            
            this.showFeedbackThanks();
            
        } catch (error) {
            console.error('Failed to submit feedback:', error);
            // Show error or just continue with thanks
            this.showFeedbackThanks();
        }
    }
    
    showFeedbackThanks() {
        const feedbackForm = document.getElementById('feedbackForm');
        const feedbackThanks = document.getElementById('feedbackThanks');
        
        if (feedbackForm) feedbackForm.style.display = 'none';
        if (feedbackThanks) {
            feedbackThanks.style.display = 'block';
            // Hide thanks message after 3 seconds
            setTimeout(() => {
                feedbackThanks.style.display = 'none';
            }, 3000);
        }
    }
    
    cancelFeedback() {
        const feedbackForm = document.getElementById('feedbackForm');
        const positiveButton = document.getElementById('feedbackPositive');
        const negativeButton = document.getElementById('feedbackNegative');
        const textarea = document.getElementById('feedbackComment');
        
        if (feedbackForm) feedbackForm.style.display = 'none';
        [positiveButton, negativeButton].forEach(btn => btn?.classList.remove('selected'));
        if (textarea) textarea.value = '';
    }
    
    updateSearchClearButton(query) {
        const clearButton = document.getElementById('searchClear');
        if (clearButton) {
            clearButton.style.display = query.length > 0 ? 'flex' : 'none';
        }
    }
    
    clearSearch() {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.value = '';
            searchInput.focus();
            this.updateSearchClearButton('');
            this.hideAutocomplete();
            this.showCategoriesView();
        }
    }
    
    clearFilters() {
        const categoryFilter = document.getElementById('categoryFilter');
        const difficultyFilter = document.getElementById('difficultyFilter');
        const filtersClear = document.getElementById('filtersClear');
        
        if (categoryFilter) categoryFilter.value = '';
        if (difficultyFilter) difficultyFilter.value = '';
        if (filtersClear) filtersClear.style.display = 'none';
        
        // Re-run search if there's a query
        const searchInput = document.getElementById('searchInput');
        if (searchInput?.value.trim()) {
            this.performSearch(searchInput.value.trim());
        }
    }
    
    async showAutocomplete(query) {
        if (query.length < 2) {
            this.hideAutocomplete();
            return;
        }
        
        try {
            // Simple autocomplete based on article titles and categories
            const suggestions = [];
            const queryLower = query.toLowerCase();
            
            // Add matching article titles
            this.articles.forEach(article => {
                if (article.title.toLowerCase().includes(queryLower)) {
                    suggestions.push({
                        type: 'article',
                        text: article.title,
                        subtitle: article.category
                    });
                }
            });
            
            // Add matching categories
            this.categories.forEach(category => {
                if (category.name.toLowerCase().includes(queryLower)) {
                    suggestions.push({
                        type: 'category',
                        text: category.name,
                        subtitle: `${category.article_count} articles`
                    });
                }
            });
            
            // Limit suggestions
            const limitedSuggestions = suggestions.slice(0, 6);
            
            if (limitedSuggestions.length > 0) {
                this.renderAutocomplete(limitedSuggestions, query);
            } else {
                this.hideAutocomplete();
            }
            
        } catch (error) {
            console.error('Autocomplete error:', error);
            this.hideAutocomplete();
        }
    }
    
    renderAutocomplete(suggestions, query) {
        const autocomplete = document.getElementById('searchAutocomplete');
        if (!autocomplete) return;
        
        autocomplete.innerHTML = '';
        this.autocompleteResults = suggestions;
        this.selectedAutocompleteIndex = -1;
        
        suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'kb-autocomplete-item';
            item.setAttribute('data-index', index);
            
            item.innerHTML = `
                <div style="font-weight: 500;">${this.highlightQuery(suggestion.text, query)}</div>
                <div style="font-size: var(--text-xs); color: var(--color-neutral-500);">${suggestion.subtitle}</div>
            `;
            
            item.addEventListener('click', () => {
                this.selectAutocompleteItem(suggestion);
            });
            
            autocomplete.appendChild(item);
        });
        
        autocomplete.style.display = 'block';
    }
    
    highlightQuery(text, query) {
        const regex = new RegExp(`(${query})`, 'gi');
        return text.replace(regex, '<mark>$1</mark>');
    }
    
    hideAutocomplete() {
        const autocomplete = document.getElementById('searchAutocomplete');
        if (autocomplete) {
            autocomplete.style.display = 'none';
        }
        this.autocompleteResults = [];
        this.selectedAutocompleteIndex = -1;
    }
    
    handleSearchKeyDown(e) {
        const autocomplete = document.getElementById('searchAutocomplete');
        const isAutocompleteVisible = autocomplete && autocomplete.style.display === 'block';
        
        if (!isAutocompleteVisible) return;
        
        switch (e.key) {
            case 'ArrowDown':
                e.preventDefault();
                this.selectedAutocompleteIndex = Math.min(
                    this.selectedAutocompleteIndex + 1,
                    this.autocompleteResults.length - 1
                );
                this.updateAutocompleteSelection();
                break;
                
            case 'ArrowUp':
                e.preventDefault();
                this.selectedAutocompleteIndex = Math.max(
                    this.selectedAutocompleteIndex - 1,
                    -1
                );
                this.updateAutocompleteSelection();
                break;
                
            case 'Enter':
                e.preventDefault();
                if (this.selectedAutocompleteIndex >= 0) {
                    this.selectAutocompleteItem(this.autocompleteResults[this.selectedAutocompleteIndex]);
                } else {
                    this.performSearch(e.target.value.trim());
                }
                break;
                
            case 'Escape':
                e.preventDefault();
                this.hideAutocomplete();
                break;
        }
    }
    
    updateAutocompleteSelection() {
        const items = document.querySelectorAll('.kb-autocomplete-item');
        items.forEach((item, index) => {
            if (index === this.selectedAutocompleteIndex) {
                item.classList.add('selected');
            } else {
                item.classList.remove('selected');
            }
        });
    }
    
    selectAutocompleteItem(suggestion) {
        const searchInput = document.getElementById('searchInput');
        
        if (suggestion.type === 'article') {
            // Find and show the article
            const article = this.articles.find(a => a.title === suggestion.text);
            if (article) {
                this.hideAutocomplete();
                this.showArticle(article.id);
            }
        } else if (suggestion.type === 'category') {
            // Show category articles
            this.hideAutocomplete();
            this.showArticlesView(suggestion.text);
        }
        
        if (searchInput) {
            searchInput.blur();
        }
    }
    
    updateFiltersClearButton() {
        const categoryFilter = document.getElementById('categoryFilter');
        const difficultyFilter = document.getElementById('difficultyFilter');
        const filtersClear = document.getElementById('filtersClear');
        
        if (filtersClear) {
            const hasFilters = (categoryFilter?.value || difficultyFilter?.value);
            filtersClear.style.display = hasFilters ? 'inline-block' : 'none';
        }
    }
}

// Global variable for easy access from onclick handlers
let knowledgeBase;

// Initialize on page load - but wait for DOM and scripts to be ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('KB: DOM loaded, checking for required dependencies...');
    
    // Check if required dependencies are loaded
    if (typeof CVDApi === 'undefined') {
        console.error('KB: CVDApi not loaded');
        setTimeout(() => {
            document.location.reload();
        }, 2000);
        return;
    }
    
    if (typeof checkNonDriverAccess === 'undefined') {
        console.error('KB: checkNonDriverAccess not loaded');
        setTimeout(() => {
            document.location.reload();
        }, 2000);
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