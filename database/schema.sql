-- KIVerdienst v2 - Database Schema
-- 60+ tables for complete content generation system

-- Setup Status
CREATE TABLE IF NOT EXISTS setup_status (
    id SERIAL PRIMARY KEY,
    setup_complete BOOLEAN DEFAULT false,
    last_step VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Core: Brands
CREATE TABLE IF NOT EXISTS brands (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    niche VARCHAR(100),
    tagline VARCHAR(255),
    description TEXT,
    content_mode VARCHAR(50) DEFAULT 'character',
    character_id INTEGER,
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

-- Characters
CREATE TABLE IF NOT EXISTS characters (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    gender VARCHAR(20),
    character_type VARCHAR(50),
    description TEXT,
    personality TEXT,
    reference_image_path TEXT,
    voice_id VARCHAR(100),
    voice_provider VARCHAR(50) DEFAULT 'azure',
    library_path TEXT,
    clips_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Character Clips
CREATE TABLE IF NOT EXISTS character_clips (
    id SERIAL PRIMARY KEY,
    character_id INTEGER REFERENCES characters(id) ON DELETE CASCADE,
    clip_filename VARCHAR(255),
    clip_type VARCHAR(50),
    emotion VARCHAR(50),
    action VARCHAR(100),
    duration_seconds FLOAT,
    resolution VARCHAR(20),
    file_path TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Videos
CREATE TABLE IF NOT EXISTS videos (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    character_id INTEGER REFERENCES characters(id) ON DELETE SET NULL,
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
    thumbnail_path TEXT,
    duration_seconds FLOAT,
    views INTEGER DEFAULT 0,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    shares INTEGER DEFAULT 0,
    saves INTEGER DEFAULT 0,
    watch_time_avg FLOAT,
    completion_rate FLOAT,
    engagement_rate FLOAT,
    is_viral BOOLEAN DEFAULT false,
    posted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Video Scripts
CREATE TABLE IF NOT EXISTS video_scripts (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    script_version INTEGER,
    full_script TEXT,
    generated_by VARCHAR(100),
    approved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Video Scenes
CREATE TABLE IF NOT EXISTS video_scenes (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    scene_number INTEGER,
    scene_type VARCHAR(50),
    duration_seconds FLOAT,
    asset_type VARCHAR(50),
    asset_path TEXT,
    transition VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Accounts
CREATE TABLE IF NOT EXISTS accounts (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    username VARCHAR(100),
    session_data TEXT,
    proxy_id VARCHAR(100),
    phone_number VARCHAR(50),
    status VARCHAR(50) DEFAULT 'active',
    followers INTEGER DEFAULT 0,
    posting_mode VARCHAR(50) DEFAULT 'auto',
    videos_per_day INTEGER DEFAULT 7,
    last_post_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Plans
CREATE TABLE IF NOT EXISTS content_plans (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    week_start_date DATE,
    theme VARCHAR(255),
    keywords TEXT,
    target_topics TEXT,
    status VARCHAR(50) DEFAULT 'planned',
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assets (Stock Footage)
CREATE TABLE IF NOT EXISTS assets (
    id SERIAL PRIMARY KEY,
    asset_type VARCHAR(50),
    category VARCHAR(100),
    keywords TEXT,
    file_path TEXT,
    duration_seconds FLOAT,
    resolution VARCHAR(20),
    license VARCHAR(100),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Products
CREATE TABLE IF NOT EXISTS products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    price DECIMAL(10,2),
    category VARCHAR(100),
    platform VARCHAR(50),
    product_url TEXT,
    commission_rate FLOAT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Product Sales
CREATE TABLE IF NOT EXISTS product_sales (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    sale_amount DECIMAL(10,2),
    commission_earned DECIMAL(10,2),
    sale_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Affiliate Links
CREATE TABLE IF NOT EXISTS affiliate_links (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id) ON DELETE CASCADE,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    tracking_code VARCHAR(255),
    full_url TEXT,
    clicks INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Affiliate Clicks
CREATE TABLE IF NOT EXISTS affiliate_clicks (
    id SERIAL PRIMARY KEY,
    affiliate_link_id INTEGER REFERENCES affiliate_links(id) ON DELETE CASCADE,
    video_id INTEGER,
    clicked_at TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Affiliate Conversions
CREATE TABLE IF NOT EXISTS affiliate_conversions (
    id SERIAL PRIMARY KEY,
    affiliate_link_id INTEGER REFERENCES affiliate_links(id) ON DELETE CASCADE,
    click_id INTEGER REFERENCES affiliate_clicks(id) ON DELETE SET NULL,
    conversion_value DECIMAL(10,2),
    commission_earned DECIMAL(10,2),
    converted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Leads
CREATE TABLE IF NOT EXISTS leads (
    id SERIAL PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255),
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    source VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    opt_in_date TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Lead Activities
CREATE TABLE IF NOT EXISTS lead_activities (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    activity_type VARCHAR(100),
    activity_data TEXT,
    occurred_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Sequences
CREATE TABLE IF NOT EXISTS email_sequences (
    id SERIAL PRIMARY KEY,
    sequence_name VARCHAR(255),
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    description TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Templates
CREATE TABLE IF NOT EXISTS email_templates (
    id SERIAL PRIMARY KEY,
    sequence_id INTEGER REFERENCES email_sequences(id) ON DELETE CASCADE,
    template_name VARCHAR(255),
    subject_line VARCHAR(500),
    body_html TEXT,
    body_text TEXT,
    send_delay_hours INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Sends
CREATE TABLE IF NOT EXISTS email_sends (
    id SERIAL PRIMARY KEY,
    lead_id INTEGER REFERENCES leads(id) ON DELETE CASCADE,
    template_id INTEGER REFERENCES email_templates(id) ON DELETE CASCADE,
    sent_at TIMESTAMP,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Opens
CREATE TABLE IF NOT EXISTS email_opens (
    id SERIAL PRIMARY KEY,
    email_send_id INTEGER REFERENCES email_sends(id) ON DELETE CASCADE,
    opened_at TIMESTAMP,
    ip_address VARCHAR(50),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Email Clicks
CREATE TABLE IF NOT EXISTS email_clicks (
    id SERIAL PRIMARY KEY,
    email_send_id INTEGER REFERENCES email_sends(id) ON DELETE CASCADE,
    link_url TEXT,
    clicked_at TIMESTAMP,
    ip_address VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Posting Queue
CREATE TABLE IF NOT EXISTS posting_queue (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    scheduled_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    attempt_count INTEGER DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Posting History
CREATE TABLE IF NOT EXISTS posting_history (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    posted_at TIMESTAMP,
    post_url TEXT,
    initial_views INTEGER DEFAULT 0,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Analytics Snapshots
CREATE TABLE IF NOT EXISTS analytics_snapshots (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    snapshot_date DATE,
    views INTEGER,
    likes INTEGER,
    comments INTEGER,
    shares INTEGER,
    watch_time_avg FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Mastermind Decisions
CREATE TABLE IF NOT EXISTS mastermind_decisions (
    id SERIAL PRIMARY KEY,
    decision_type VARCHAR(100),
    brand_id INTEGER,
    input_data TEXT,
    output_decision TEXT,
    confidence_score FLOAT,
    decided_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Mastermind Learnings (RAG)
CREATE TABLE IF NOT EXISTS mastermind_learnings (
    id SERIAL PRIMARY KEY,
    learning_type VARCHAR(100),
    content TEXT,
    embedding TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent Tasks
CREATE TABLE IF NOT EXISTS agent_tasks (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    task_type VARCHAR(100),
    task_data TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    priority INTEGER DEFAULT 5,
    scheduled_at TIMESTAMP,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    result TEXT,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Agent Logs
CREATE TABLE IF NOT EXISTS agent_logs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100),
    log_level VARCHAR(20),
    message TEXT,
    logged_at TIMESTAMP DEFAULT NOW()
);

-- Niches
CREATE TABLE IF NOT EXISTS niches (
    id SERIAL PRIMARY KEY,
    niche_name VARCHAR(100) NOT NULL,
    description TEXT,
    target_audience TEXT,
    avg_cpm FLOAT,
    competition_level VARCHAR(50),
    potential_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Competitor Analysis
CREATE TABLE IF NOT EXISTS competitor_analysis (
    id SERIAL PRIMARY KEY,
    niche_id INTEGER REFERENCES niches(id) ON DELETE CASCADE,
    creator_username VARCHAR(100),
    platform VARCHAR(50),
    followers INTEGER,
    avg_views INTEGER,
    engagement_rate FLOAT,
    content_strategy TEXT,
    analyzed_at DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Trending Topics
CREATE TABLE IF NOT EXISTS trending_topics (
    id SERIAL PRIMARY KEY,
    niche_id INTEGER REFERENCES niches(id) ON DELETE CASCADE,
    topic VARCHAR(255),
    trend_score FLOAT,
    detected_at DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comment Triggers
CREATE TABLE IF NOT EXISTS comment_triggers (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    trigger_keyword VARCHAR(255),
    reply_template TEXT,
    cta_link TEXT,
    active BOOLEAN DEFAULT true,
    trigger_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Comment Interactions
CREATE TABLE IF NOT EXISTS comment_interactions (
    id SERIAL PRIMARY KEY,
    trigger_id INTEGER REFERENCES comment_triggers(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    comment_text TEXT,
    reply_sent BOOLEAN DEFAULT false,
    interacted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Revenue Goals
CREATE TABLE IF NOT EXISTS revenue_goals (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    goal_period VARCHAR(50),
    target_amount DECIMAL(10,2),
    current_amount DECIMAL(10,2) DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transactions
CREATE TABLE IF NOT EXISTS transactions (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    transaction_type VARCHAR(50),
    amount DECIMAL(10,2),
    currency VARCHAR(10) DEFAULT 'EUR',
    description TEXT,
    transaction_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Performance Metrics
CREATE TABLE IF NOT EXISTS performance_metrics (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    metric_name VARCHAR(100),
    metric_value FLOAT,
    period_start DATE,
    period_end DATE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- AB Tests
CREATE TABLE IF NOT EXISTS ab_tests (
    id SERIAL PRIMARY KEY,
    test_name VARCHAR(255),
    brand_id INTEGER REFERENCES brands(id) ON DELETE CASCADE,
    variant_a_description TEXT,
    variant_b_description TEXT,
    status VARCHAR(50) DEFAULT 'active',
    winner VARCHAR(10),
    created_at TIMESTAMP DEFAULT NOW()
);

-- AB Test Results
CREATE TABLE IF NOT EXISTS ab_test_results (
    id SERIAL PRIMARY KEY,
    test_id INTEGER REFERENCES ab_tests(id) ON DELETE CASCADE,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    variant VARCHAR(10),
    views INTEGER,
    engagement_rate FLOAT,
    conversion_rate FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Hashtag Library
CREATE TABLE IF NOT EXISTS hashtag_library (
    id SERIAL PRIMARY KEY,
    hashtag VARCHAR(100),
    category VARCHAR(100),
    niche_id INTEGER REFERENCES niches(id) ON DELETE SET NULL,
    performance_score FLOAT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Video Hashtags (Many-to-Many)
CREATE TABLE IF NOT EXISTS video_hashtags (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    hashtag_id INTEGER REFERENCES hashtag_library(id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Voice Profiles
CREATE TABLE IF NOT EXISTS voice_profiles (
    id SERIAL PRIMARY KEY,
    voice_name VARCHAR(100),
    provider VARCHAR(50),
    voice_id VARCHAR(100),
    language VARCHAR(20),
    gender VARCHAR(20),
    style VARCHAR(50),
    sample_url TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Content Templates
CREATE TABLE IF NOT EXISTS content_templates (
    id SERIAL PRIMARY KEY,
    template_name VARCHAR(255),
    template_type VARCHAR(50),
    structure TEXT,
    example TEXT,
    usage_count INTEGER DEFAULT 0,
    performance_score FLOAT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Script Hooks
CREATE TABLE IF NOT EXISTS script_hooks (
    id SERIAL PRIMARY KEY,
    hook_text TEXT,
    category VARCHAR(100),
    niche_id INTEGER REFERENCES niches(id) ON DELETE SET NULL,
    performance_score FLOAT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Call To Actions
CREATE TABLE IF NOT EXISTS call_to_actions (
    id SERIAL PRIMARY KEY,
    cta_text TEXT,
    cta_type VARCHAR(50),
    target_url TEXT,
    conversion_rate FLOAT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Music Library
CREATE TABLE IF NOT EXISTS music_library (
    id SERIAL PRIMARY KEY,
    track_name VARCHAR(255),
    artist VARCHAR(255),
    genre VARCHAR(100),
    mood VARCHAR(100),
    duration_seconds FLOAT,
    file_path TEXT,
    license VARCHAR(100),
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Transitions Library
CREATE TABLE IF NOT EXISTS transitions_library (
    id SERIAL PRIMARY KEY,
    transition_name VARCHAR(100),
    transition_type VARCHAR(50),
    duration_seconds FLOAT,
    file_path TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Effects Library
CREATE TABLE IF NOT EXISTS effects_library (
    id SERIAL PRIMARY KEY,
    effect_name VARCHAR(100),
    effect_type VARCHAR(50),
    parameters TEXT,
    usage_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Proxies
CREATE TABLE IF NOT EXISTS proxies (
    id SERIAL PRIMARY KEY,
    proxy_type VARCHAR(50),
    proxy_url TEXT,
    username VARCHAR(100),
    password VARCHAR(100),
    location VARCHAR(100),
    status VARCHAR(50) DEFAULT 'active',
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Platform Sessions
CREATE TABLE IF NOT EXISTS platform_sessions (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    session_token TEXT,
    cookies TEXT,
    user_agent TEXT,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Upload Queue
CREATE TABLE IF NOT EXISTS upload_queue (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    account_id INTEGER REFERENCES accounts(id) ON DELETE CASCADE,
    platform VARCHAR(50),
    scheduled_time TIMESTAMP,
    status VARCHAR(50) DEFAULT 'pending',
    retry_count INTEGER DEFAULT 0,
    error_log TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Platform Restrictions
CREATE TABLE IF NOT EXISTS platform_restrictions (
    id SERIAL PRIMARY KEY,
    platform VARCHAR(50),
    restriction_type VARCHAR(100),
    restriction_data TEXT,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Webhook Events
CREATE TABLE IF NOT EXISTS webhook_events (
    id SERIAL PRIMARY KEY,
    event_type VARCHAR(100),
    platform VARCHAR(50),
    payload TEXT,
    processed BOOLEAN DEFAULT false,
    received_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- System Config
CREATE TABLE IF NOT EXISTS system_config (
    id SERIAL PRIMARY KEY,
    config_key VARCHAR(100) UNIQUE,
    config_value TEXT,
    config_type VARCHAR(50),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Backup History
CREATE TABLE IF NOT EXISTS backup_history (
    id SERIAL PRIMARY KEY,
    backup_type VARCHAR(50),
    file_path TEXT,
    file_size_bytes BIGINT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Error Logs
CREATE TABLE IF NOT EXISTS error_logs (
    id SERIAL PRIMARY KEY,
    error_type VARCHAR(100),
    error_message TEXT,
    stack_trace TEXT,
    context TEXT,
    severity VARCHAR(20),
    resolved BOOLEAN DEFAULT false,
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Notifications
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    notification_type VARCHAR(100),
    title VARCHAR(255),
    message TEXT,
    priority VARCHAR(20),
    read BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW()
);

-- User Actions
CREATE TABLE IF NOT EXISTS user_actions (
    id SERIAL PRIMARY KEY,
    action_type VARCHAR(100),
    action_data TEXT,
    ip_address VARCHAR(50),
    user_agent TEXT,
    occurred_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_videos_brand ON videos(brand_id);
CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_views ON videos(views DESC);
CREATE INDEX IF NOT EXISTS idx_videos_posted_at ON videos(posted_at);
CREATE INDEX IF NOT EXISTS idx_accounts_brand ON accounts(brand_id);
CREATE INDEX IF NOT EXISTS idx_accounts_platform ON accounts(platform);
CREATE INDEX IF NOT EXISTS idx_leads_email ON leads(email);
CREATE INDEX IF NOT EXISTS idx_leads_brand ON leads(brand_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_scheduled ON agent_tasks(scheduled_at);
CREATE INDEX IF NOT EXISTS idx_posting_queue_status ON posting_queue(status);
CREATE INDEX IF NOT EXISTS idx_posting_queue_scheduled ON posting_queue(scheduled_time);
CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_video ON analytics_snapshots(video_id);
CREATE INDEX IF NOT EXISTS idx_analytics_snapshots_date ON analytics_snapshots(snapshot_date);

-- Insert initial data
INSERT INTO setup_status (setup_complete) VALUES (false) ON CONFLICT DO NOTHING;
