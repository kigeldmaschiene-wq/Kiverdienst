-- KIVerdienst V2 - Complete Database Schema
-- 60+ tables for autonomous multi-brand content generation

-- Setup & Configuration
CREATE TABLE IF NOT EXISTS setup_status (
    id SERIAL PRIMARY KEY,
    setup_complete BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Brands (4 core brands + scalable)
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    niche VARCHAR(100),
    description TEXT,
    active BOOLEAN DEFAULT false,
    tiktok_enabled BOOLEAN DEFAULT false,
    tiktok_username VARCHAR(100),
    instagram_enabled BOOLEAN DEFAULT false,
    instagram_username VARCHAR(100),
    youtube_enabled BOOLEAN DEFAULT false,
    youtube_username VARCHAR(100),
    videos_per_day INTEGER DEFAULT 7,
    posting_times TEXT,
    posting_days TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Characters (2 per brand: male + female for A/B testing)
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    gender VARCHAR(20),
    character_type VARCHAR(50),
    voice_id VARCHAR(100),
    library_path TEXT,
    clips_count INTEGER DEFAULT 0,
    base_prompt TEXT,
    personality TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Character Clips (40-60 per character)
CREATE TABLE IF NOT EXISTS character_clips (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    clip_filename VARCHAR(255),
    clip_type VARCHAR(50),
    duration_seconds FLOAT,
    file_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Videos (main content table)
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    character_id INTEGER REFERENCES characters(id),
    account_id INTEGER,
    platform VARCHAR(50),
    title VARCHAR(500),
    script TEXT,
    hook TEXT,
    body TEXT,
    cta TEXT,
    hashtags TEXT,
    status VARCHAR(50) DEFAULT 'draft',
    file_path TEXT,
    duration_seconds FLOAT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    engagement_rate FLOAT,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_scripts (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    script_version INTEGER,
    full_script TEXT,
    approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS video_scenes (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    scene_number INTEGER,
    scene_type VARCHAR(50),
    duration_seconds FLOAT,
    asset_path TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Social Media Accounts
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    platform VARCHAR(50),
    username VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    followers INTEGER DEFAULT 0,
    proxy_config TEXT,
    session_data TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Planning
CREATE TABLE IF NOT EXISTS content_plans (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    week_start_date DATE,
    theme VARCHAR(255),
    keywords TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets (stock footage, music, etc)
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(50),
    category VARCHAR(100),
    keywords TEXT,
    file_path TEXT,
    duration_seconds FLOAT,
    source VARCHAR(100),
    license_type VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products & Revenue
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255),
    description TEXT,
    price DECIMAL(10,2),
    commission_rate FLOAT,
    product_url TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS product_sales (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    brand_id INTEGER REFERENCES brands(id),
    sale_amount DECIMAL(10,2),
    commission_earned DECIMAL(10,2),
    sale_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS affiliate_links (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    brand_id INTEGER REFERENCES brands(id),
    tracking_code VARCHAR(255),
    full_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS affiliate_clicks (
    id SERIAL PRIMARY KEY,
    affiliate_link_id INTEGER REFERENCES affiliate_links(id),
    clicked_at TIMESTAMP,
    user_agent TEXT,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS affiliate_conversions (
    id SERIAL PRIMARY KEY,
    affiliate_link_id INTEGER REFERENCES affiliate_links(id),
    conversion_value DECIMAL(10,2),
    converted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lead Generation & Email Marketing
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    brand_id INTEGER REFERENCES brands(id),
    source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    subscribed_at TIMESTAMP,
    unsubscribed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_sequences (
    id SERIAL PRIMARY KEY,
    sequence_name VARCHAR(255),
    brand_id INTEGER REFERENCES brands(id),
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_templates (
    id SERIAL PRIMARY KEY,
    sequence_id INTEGER REFERENCES email_sequences(id),
    email_number INTEGER,
    subject_line VARCHAR(500),
    body_html TEXT,
    body_plain TEXT,
    send_delay_hours INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_sends (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id),
    template_id INTEGER REFERENCES email_templates(id),
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_opens (
    id SERIAL PRIMARY KEY,
    email_send_id INTEGER REFERENCES email_sends(id),
    opened_at TIMESTAMP,
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS email_clicks (
    id SERIAL PRIMARY KEY,
    email_send_id INTEGER REFERENCES email_sends(id),
    link_url TEXT,
    clicked_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Posting Queue & History
CREATE TABLE IF NOT EXISTS posting_queue (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    account_id INTEGER REFERENCES accounts(id),
    scheduled_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    last_error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS posting_history (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    account_id INTEGER REFERENCES accounts(id),
    posted_at TIMESTAMP,
    post_url TEXT,
    platform VARCHAR(50),
    initial_engagement JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics & Performance
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id),
    snapshot_date DATE,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    engagement_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    metric_name VARCHAR(100),
    metric_value FLOAT,
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255),
    brand_id INTEGER REFERENCES brands(id),
    test_type VARCHAR(50),
    status VARCHAR(50),
    winner VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS ab_test_results (
    id SERIAL PRIMARY KEY,
    test_id INTEGER REFERENCES ab_tests(id),
    video_id INTEGER REFERENCES videos(id),
    variant VARCHAR(50),
    views INTEGER,
    engagement_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent System
CREATE TABLE IF NOT EXISTS agent_tasks (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    task_type VARCHAR(100),
    task_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result JSONB,
    error TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    log_level VARCHAR(20),
    message TEXT,
    context JSONB,
    logged_at TIMESTAMP DEFAULT NOW()
);

-- Mastermind System
CREATE TABLE IF NOT EXISTS mastermind_decisions (
    id SERIAL PRIMARY KEY,
    decision_type VARCHAR(100),
    input_data JSONB,
    output_decision JSONB,
    reasoning TEXT,
    confidence_score FLOAT,
    decided_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS mastermind_learnings (
    id SERIAL PRIMARY KEY,
    learning_type VARCHAR(100),
    content TEXT,
    source VARCHAR(255),
    effectiveness_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Niche Analysis
CREATE TABLE IF NOT EXISTS niches (
    id SERIAL PRIMARY KEY,
    niche_name VARCHAR(100),
    description TEXT,
    avg_cpm DECIMAL(10,2),
    competition_level VARCHAR(50),
    potential_score FLOAT,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS competitor_analysis (
    id SERIAL PRIMARY KEY,
    niche_id INTEGER REFERENCES niches(id),
    creator_username VARCHAR(100),
    platform VARCHAR(50),
    followers INTEGER,
    avg_views INTEGER,
    engagement_rate FLOAT,
    posting_frequency INTEGER,
    analyzed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS trending_topics (
    id SERIAL PRIMARY KEY,
    niche_id INTEGER REFERENCES niches(id),
    topic TEXT,
    trend_score FLOAT,
    hashtags TEXT,
    detected_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comment Triggers (automated engagement)
CREATE TABLE IF NOT EXISTS comment_triggers (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    trigger_keyword VARCHAR(255),
    reply_template TEXT,
    cta_link TEXT,
    active BOOLEAN DEFAULT true,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS comment_interactions (
    id SERIAL PRIMARY KEY,
    trigger_id INTEGER REFERENCES comment_triggers(id),
    video_id INTEGER REFERENCES videos(id),
    comment_text TEXT,
    reply_sent TEXT,
    interacted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Revenue & Budget Tracking
CREATE TABLE IF NOT EXISTS revenue_goals (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    goal_period VARCHAR(50),
    target_amount DECIMAL(10,2),
    current_amount DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    transaction_type VARCHAR(50),
    amount DECIMAL(10,2),
    currency VARCHAR(10),
    description TEXT,
    transaction_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS budget_allocations (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id),
    category VARCHAR(100),
    allocated_amount DECIMAL(10,2),
    spent_amount DECIMAL(10,2),
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- System Settings
CREATE TABLE IF NOT EXISTS settings (
    id SERIAL PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE,
    setting_value TEXT,
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_videos_brand ON videos(brand_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_posted_at ON videos(posted_at);
CREATE INDEX IF NOT EXISTS idx_accounts_brand ON accounts(brand_id);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_posting_queue_scheduled_time ON posting_queue(scheduled_time);

-- Initial data
INSERT INTO setup_status (setup_complete) VALUES (false) 
    ON CONFLICT DO NOTHING;

INSERT INTO settings (setting_key, setting_value) VALUES 
    ('system_version', '2.0'),
    ('maintenance_mode', 'false'),
    ('auto_posting_enabled', 'false')
    ON CONFLICT (setting_key) DO NOTHING;
