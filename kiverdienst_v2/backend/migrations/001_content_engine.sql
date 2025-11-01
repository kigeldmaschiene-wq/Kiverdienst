BEGIN;

ALTER TABLE videos ADD COLUMN IF NOT EXISTS approval_status VARCHAR(50) DEFAULT 'pending';
ALTER TABLE videos ADD COLUMN IF NOT EXISTS approved_by VARCHAR(100);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS approved_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS rejected_reason TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS duration FLOAT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS script TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS hook TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS cta TEXT;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS topic VARCHAR(255);
ALTER TABLE videos ADD COLUMN IF NOT EXISTS quality_score INTEGER DEFAULT 0;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS generation_started_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS generation_completed_at TIMESTAMP;
ALTER TABLE videos ADD COLUMN IF NOT EXISTS generation_error TEXT;

CREATE TABLE IF NOT EXISTS character_clips (
    id SERIAL PRIMARY KEY,
    character_id INTEGER NOT NULL REFERENCES characters(id) ON DELETE CASCADE,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    duration FLOAT NOT NULL,
    resolution VARCHAR(20) DEFAULT '1080x1920',
    runway_prompt TEXT,
    runway_job_id VARCHAR(255),
    runway_cost DECIMAL(10,2) DEFAULT 0.00,
    times_used INTEGER DEFAULT 0,
    quality_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_character_clips_character ON character_clips(character_id);
CREATE INDEX idx_character_clips_category ON character_clips(category);

CREATE TABLE IF NOT EXISTS video_scripts (
    id SERIAL PRIMARY KEY,
    video_id INTEGER REFERENCES videos(id) ON DELETE CASCADE,
    brand_id INTEGER NOT NULL REFERENCES brands(id),
    hook TEXT NOT NULL,
    problem TEXT,
    story TEXT NOT NULL,
    cta TEXT NOT NULL,
    full_script TEXT NOT NULL,
    word_count INTEGER,
    estimated_duration FLOAT,
    topic VARCHAR(255),
    quality_score INTEGER DEFAULT 0,
    hook_strength INTEGER DEFAULT 0,
    cta_clarity INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_video_scripts_brand ON video_scripts(brand_id);
CREATE INDEX idx_video_scripts_quality ON video_scripts(quality_score DESC);

CREATE TABLE IF NOT EXISTS generation_queue (
    id SERIAL PRIMARY KEY,
    brand_id INTEGER NOT NULL REFERENCES brands(id),
    priority INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'queued',
    topic VARCHAR(255),
    platform VARCHAR(50) DEFAULT 'tiktok',
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

CREATE TABLE IF NOT EXISTS approval_queue (
    id SERIAL PRIMARY KEY,
    item_type VARCHAR(50) NOT NULL,
    item_id INTEGER NOT NULL,
    brand_id INTEGER REFERENCES brands(id),
    status VARCHAR(50) DEFAULT 'pending',
    approved_by VARCHAR(100),
    approved_at TIMESTAMP,
    rejected_reason TEXT,
    preview_url TEXT,
    metadata JSONB,
    ai_recommendation VARCHAR(50),
    ai_confidence FLOAT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_approval_queue_status ON approval_queue(status);

CREATE TABLE IF NOT EXISTS ai_agents_logs (
    id SERIAL PRIMARY KEY,
    agent_name VARCHAR(100) NOT NULL,
    action VARCHAR(100) NOT NULL,
    brand_id INTEGER REFERENCES brands(id),
    video_id INTEGER REFERENCES videos(id),
    status VARCHAR(50),
    message TEXT,
    details JSONB,
    duration_ms INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_agents_logs_agent ON ai_agents_logs(agent_name);
CREATE INDEX idx_agents_logs_created ON ai_agents_logs(created_at DESC);

CREATE TABLE IF NOT EXISTS stock_footage (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    filepath TEXT NOT NULL,
    source VARCHAR(50) NOT NULL,
    category VARCHAR(100),
    tags TEXT[],
    duration FLOAT,
    times_used INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_stock_footage_category ON stock_footage(category);

CREATE TABLE IF NOT EXISTS budget_expenses (
    id SERIAL PRIMARY KEY,
    category VARCHAR(100) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    description TEXT,
    brand_id INTEGER REFERENCES brands(id),
    video_id INTEGER REFERENCES videos(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

COMMIT;
