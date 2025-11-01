-- ============================================================
-- KIVERDIENST V2 - CONTENT ENGINE DATABASE MIGRATION
-- Version: 1.0 | Date: 01.11.2025
-- Adds: 8 new tables + extends videos table
-- ============================================================

BEGIN;

-- ============================================================
-- 1. VIDEOS TABLE - EXTENSIONS
-- ============================================================

-- Approval System
ALTER TABLE videos ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE videos ADD COLUMN IF NOT EXISTS approved_by VARCHAR(100);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS rejected_reason TEXT;

COMMENT ON COLUMN videos.approval_status IS 'pending_approval, approved, rejected, auto_approved';

-- Video Metadata
ALTER TABLE videos ADD COLUMN IF NOT EXISTS duration FLOAT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS script TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS hook TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS cta TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS topic VARCHAR(255);

-- Performance & Quality
ALTER TABLE videos ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS watch_time_predicted FLOAT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS cost_generated DECIMAL(10,2) DEFAULT 0.00;

COMMENT ON COLUMN videos.quality_score IS '0-100 AI quality assessment';

-- Generation Timing
ALTER TABLE videos ADD COLUMN IF NOT EXISTS generation_started_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS generation_completed_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS generation_error TEXT;

COMMENT ON COLUMN videos.status IS 'pending, generating, completed, approved, rejected, posted, failed';

-- ============================================================
-- 2. CHARACTER CLIPS TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS character_clips (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    
    -- File Info
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    duration FLOAT NOT NULL,
    resolution VARCHAR(20) DEFAULT '1080x1920',
    
    -- Runway Gen-3 Metadata
    runway_prompt TEXT,
    runway_job_id VARCHAR(255),
    runway_cost DECIMAL(10,2) DEFAULT 0.00,
    runway_generation_time INTEGER,
    
    -- Usage Tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Quality Scores
    quality_score INTEGER DEFAULT 0,
    consistency_score INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_character_clips_character ON character_clips(character_id);
CREATE INDEX idx_character_clips_category ON character_clips(category);
CREATE INDEX idx_character_clips_usage ON character_clips(times_used);
CREATE INDEX idx_character_clips_quality ON character_clips(quality_score DESC);

COMMENT ON TABLE character_clips IS 'Character video clips library from Runway Gen-3';
COMMENT ON COLUMN character_clips.category IS 'talking, pointing, emotion_happy, emotion_serious, action_typing, gesture_explaining';
COMMENT ON COLUMN character_clips.quality_score IS '0-100 based on visual quality';
COMMENT ON COLUMN character_clips.consistency_score IS '0-100 character look consistency vs reference';

-- ============================================================
-- 3. VIDEO SCRIPTS TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS video_scripts (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    brand_id INTEGER NOT NULL REFERENCES brands(id),
    
    -- Script Components
    hook TEXT NOT NULL,
    problem TEXT,
    story TEXT NOT NULL,
    cta TEXT NOT NULL,
    full_script TEXT NOT NULL,
    
    -- Metadata
    word_count INTEGER,
    estimated_duration FLOAT,
    topic VARCHAR(255),
    keywords TEXT[],
    
    -- Generation Info
    generated_by VARCHAR(50) DEFAULT 'ollama_8b',
    prompt_used TEXT,
    temperature FLOAT DEFAULT 0.8,
    
    -- Quality Scores
    quality_score INTEGER DEFAULT 0,
    hook_strength INTEGER DEFAULT 0,
    cta_clarity INTEGER DEFAULT 0,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_video_scripts_video ON video_scripts(video_id);
CREATE INDEX idx_video_scripts_brand ON video_scripts(brand_id);
CREATE INDEX idx_video_scripts_quality ON video_scripts(quality_score DESC);
CREATE INDEX idx_video_scripts_topic ON video_scripts(topic);

COMMENT ON TABLE video_scripts IS 'AI-generated video scripts with quality scoring';
COMMENT ON COLUMN video_scripts.hook IS 'First 1-3 seconds - must grab attention';
COMMENT ON COLUMN video_scripts.problem IS 'Address audience pain point';
COMMENT ON COLUMN video_scripts.story IS 'Main content - solution/demonstration';
COMMENT ON COLUMN video_scripts.cta IS 'Call to action - clear next step';

-- ============================================================
-- 4. GENERATION QUEUE TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS generation_queue (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL REFERENCES brands(id),
    character_id INTEGER REFERENCES characters(id),
    
    -- Queue Management
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued',
    
    -- Generation Parameters
    topic VARCHAR(255),
    platform VARCHAR(50) DEFAULT 'tiktok',
    video_length_target INTEGER DEFAULT 60,
    
    -- Processing Info
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    video_id INTEGER REFERENCES videos(id),
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_gen_queue_status ON generation_queue(status);
CREATE INDEX idx_gen_queue_priority ON generation_queue(priority DESC, created_at ASC);
CREATE INDEX idx_gen_queue_brand ON generation_queue(brand_id);

COMMENT ON TABLE generation_queue IS 'Video generation job queue with priority system';
COMMENT ON COLUMN generation_queue.status IS 'queued, processing, completed, failed';
COMMENT ON COLUMN generation_queue.platform IS 'tiktok, instagram, youtube';
COMMENT ON COLUMN generation_queue.priority IS 'Higher number = higher priority (0-100)';

-- ============================================================
-- 5. APPROVAL QUEUE TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS approval_queue (
    id SERIAL PRIMARY KEY,
    
    -- Item to Approve
    item_type VARCHAR(50) NOT NULL,
    item_id INTEGER NOT NULL,
    brand_id INTEGER REFERENCES brands(id),
    
    -- Approval Status
    status VARCHAR(50) DEFAULT 'pending',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejected_reason TEXT,
    
    -- Preview & Metadata
    preview_url TEXT,
    metadata JSONB,
    
    -- AI Recommendation
    ai_recommendation VARCHAR(50),
    ai_confidence FLOAT,
    ai_notes TEXT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_queue_status ON approval_queue(status);
CREATE INDEX idx_approval_queue_type ON approval_queue(item_type);
CREATE INDEX idx_approval_queue_brand ON approval_queue(brand_id);
CREATE INDEX idx_approval_queue_created ON approval_queue(created_at DESC);

COMMENT ON TABLE approval_queue IS 'Items awaiting user approval';
COMMENT ON COLUMN approval_queue.item_type IS 'video, product, email, landing_page';
COMMENT ON COLUMN approval_queue.status IS 'pending, approved, rejected';
COMMENT ON COLUMN approval_queue.ai_recommendation IS 'approve, reject, review';
COMMENT ON COLUMN approval_queue.ai_confidence IS 'AI confidence 0.0-1.0';

-- ============================================================
-- 6. AI AGENTS LOGS TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS ai_agents_logs (
    id SERIAL PRIMARY KEY,
    
    -- Agent Info
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    
    -- Context
    brand_id INTEGER REFERENCES brands(id),
    video_id INTEGER REFERENCES videos(id),
    
    -- Log Data
    status VARCHAR(50),
    message TEXT,
    details JSONB,
    
    -- Performance
    duration_ms INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_logs_agent ON ai_agents_logs(agent_name);
CREATE INDEX idx_agents_logs_status ON ai_agents_logs(status);
CREATE INDEX idx_agents_logs_created ON ai_agents_logs(created_at DESC);
CREATE INDEX idx_agents_logs_brand ON ai_agents_logs(brand_id);
CREATE INDEX idx_agents_logs_video ON ai_agents_logs(video_id);

COMMENT ON TABLE ai_agents_logs IS 'Activity logs for all AI agents';
COMMENT ON COLUMN ai_agents_logs.duration_ms IS 'Execution time in milliseconds';

-- ============================================================
-- 7. STOCK FOOTAGE TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS stock_footage (
    id SERIAL PRIMARY KEY,
    
    -- File Info
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    source_id VARCHAR(255),
    source_url TEXT,
    
    -- Metadata
    category VARCHAR(100),
    tags TEXT[],
    duration FLOAT,
    resolution VARCHAR(20),
    
    -- Usage Tracking
    times_used INTEGER DEFAULT 0,
    last_used_at TIMESTAMP,
    
    -- Download Info
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    filesize_mb FLOAT,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stock_footage_category ON stock_footage(category);
CREATE INDEX idx_stock_footage_tags ON stock_footage USING GIN(tags);
CREATE INDEX idx_stock_footage_usage ON stock_footage(times_used);
CREATE INDEX idx_stock_footage_source ON stock_footage(source);

COMMENT ON TABLE stock_footage IS 'B-Roll stock footage from Pexels, Pixabay';
COMMENT ON COLUMN stock_footage.source IS 'pexels, pixabay, local';
COMMENT ON COLUMN stock_footage.times_used IS 'Usage count for rotation logic';

-- ============================================================
-- 8. BUDGET EXPENSES TABLE (NEU!)
-- ============================================================

CREATE TABLE IF NOT EXISTS budget_expenses (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(10) DEFAULT 'EUR',
    description TEXT,
    brand_id INTEGER REFERENCES brands(id),
    video_id INTEGER REFERENCES videos(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_budget_expenses_category ON budget_expenses(category);
CREATE INDEX idx_budget_expenses_created ON budget_expenses(created_at DESC);
CREATE INDEX idx_budget_expenses_brand ON budget_expenses(brand_id);

COMMENT ON TABLE budget_expenses IS 'Track all system expenses for budget monitoring';
COMMENT ON COLUMN budget_expenses.category IS 'runway_gen3, azure_tts, server, apis, other';

COMMIT;

-- ============================================================
-- VERIFY MIGRATION
-- ============================================================

DO $$
BEGIN
    RAISE NOTICE '? Migration completed successfully!';
    RAISE NOTICE 'New tables: character_clips, video_scripts, generation_queue, approval_queue, ai_agents_logs, stock_footage, budget_expenses';
    RAISE NOTICE 'Extended table: videos (13 new columns)';
    RAISE NOTICE 'Total new indexes: 20+';
END $$;
