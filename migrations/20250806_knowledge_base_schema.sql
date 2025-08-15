-- Knowledge Base Schema Migration
-- Creates tables for knowledge base metadata caching and category management
-- Author: Documentation Team
-- Date: 2025-08-06

-- Enable foreign key support
PRAGMA foreign_keys = ON;

-- Create knowledge_base_articles table for metadata caching
CREATE TABLE IF NOT EXISTS knowledge_base_articles (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    author TEXT,
    category TEXT NOT NULL,
    tags TEXT, -- JSON array as string (comma-separated for simplicity)
    difficulty TEXT CHECK(difficulty IN ('Beginner', 'Intermediate', 'Advanced')),
    word_count INTEGER,
    read_time_minutes INTEGER,
    file_path TEXT NOT NULL,
    file_modified_time TIMESTAMP,
    last_indexed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    content_preview TEXT, -- First 200 characters for search previews
    search_content TEXT, -- Processed content for full-text search
    content_hash TEXT -- MD5 hash for change detection
);

-- Create knowledge_base_categories table for category configuration
CREATE TABLE IF NOT EXISTS knowledge_base_categories (
    name TEXT PRIMARY KEY,
    description TEXT,
    icon TEXT,
    color TEXT,
    sort_order INTEGER DEFAULT 0
);

-- Create indexes for search performance
CREATE INDEX IF NOT EXISTS idx_kb_articles_category ON knowledge_base_articles(category);
CREATE INDEX IF NOT EXISTS idx_kb_articles_modified ON knowledge_base_articles(file_modified_time);
CREATE INDEX IF NOT EXISTS idx_kb_articles_difficulty ON knowledge_base_articles(difficulty);
CREATE INDEX IF NOT EXISTS idx_kb_articles_search ON knowledge_base_articles(search_content);

-- Create index for category sorting
CREATE INDEX IF NOT EXISTS idx_kb_categories_sort ON knowledge_base_categories(sort_order);

-- Insert default categories with proper configuration
INSERT OR IGNORE INTO knowledge_base_categories (name, description, icon, color, sort_order) VALUES
('Getting Started', 'Essential information for new users', '📚', '#4F46E5', 1),
('Feature Tutorials', 'Step-by-step guides for CVD features', '🎯', '#059669', 2),
('Troubleshooting', 'Solutions to common problems', '🔧', '#DC2626', 3),
('System Administration', 'Advanced configuration and management', '⚙️', '#7C2D12', 4),
('Best Practices', 'Recommended workflows and tips', '⭐', '#9333EA', 5);

-- Create audit log entries for knowledge base schema creation
INSERT OR IGNORE INTO audit_log (user_id, action, entity_type, entity_id, details, timestamp)
VALUES 
(1, 'CREATE_SCHEMA', 'knowledge_base', 'schema', 'Knowledge base schema and tables created', CURRENT_TIMESTAMP);

-- Migration completed successfully