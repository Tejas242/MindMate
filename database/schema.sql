-- MindMate Database Schema
-- SQLite version for demo/development

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(20) DEFAULT 'student' CHECK (role IN ('student', 'counsellor', 'admin')),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Student-specific fields
    student_id VARCHAR(100),
    campus VARCHAR(255),
    year_of_study INTEGER,
    
    -- Counsellor-specific fields
    license_number VARCHAR(100),
    specialization VARCHAR(255)
);

-- Chat sessions table
CREATE TABLE IF NOT EXISTS chat_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    session_token VARCHAR(255) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT true,
    
    -- Risk assessment
    current_risk_level VARCHAR(20) DEFAULT 'low' CHECK (current_risk_level IN ('low', 'medium', 'high', 'crisis')),
    risk_score REAL DEFAULT 0.0,
    risk_factors TEXT, -- JSON
    
    -- Crisis handling
    crisis_flagged BOOLEAN DEFAULT false,
    counsellor_notified BOOLEAN DEFAULT false,
    
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Chat messages table
CREATE TABLE IF NOT EXISTS chat_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    sender VARCHAR(20) NOT NULL CHECK (sender IN ('user', 'assistant')),
    content TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- AI metadata
    tokens_used INTEGER,
    response_time REAL,
    model_used VARCHAR(100),
    
    -- Safety filtering
    safety_filtered BOOLEAN DEFAULT false,
    original_content TEXT,
    
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Risk assessments table
CREATE TABLE IF NOT EXISTS risk_assessments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id INTEGER NOT NULL,
    message_id INTEGER,
    
    -- Assessment scores
    overall_risk_score REAL NOT NULL,
    risk_level VARCHAR(20) NOT NULL CHECK (risk_level IN ('low', 'medium', 'high', 'crisis')),
    
    -- Specific assessment scores
    depression_score REAL DEFAULT 0.0,
    anxiety_score REAL DEFAULT 0.0,
    suicide_risk_score REAL DEFAULT 0.0,
    self_harm_score REAL DEFAULT 0.0,
    
    -- Detected indicators
    risk_factors TEXT, -- JSON
    protective_factors TEXT, -- JSON  
    crisis_keywords_detected TEXT, -- JSON
    
    -- AI explanation
    explanation TEXT,
    confidence_level REAL,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id),
    FOREIGN KEY (message_id) REFERENCES chat_messages(id)
);

-- Interventions table
CREATE TABLE IF NOT EXISTS interventions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100) NOT NULL,
    description TEXT,
    content TEXT NOT NULL,
    
    -- Targeting
    min_risk_level VARCHAR(20) DEFAULT 'low',
    max_risk_level VARCHAR(20) DEFAULT 'high',
    
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Counsellor assignments table  
CREATE TABLE IF NOT EXISTS counsellor_assignments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    counsellor_id INTEGER NOT NULL,
    session_id INTEGER NOT NULL,
    
    assigned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'pending' CHECK (status IN ('pending', 'contacted', 'resolved')),
    priority VARCHAR(20) DEFAULT 'medium' CHECK (priority IN ('low', 'medium', 'high', 'crisis')),
    
    notes TEXT,
    resolved_at TIMESTAMP,
    
    FOREIGN KEY (student_id) REFERENCES users(id),
    FOREIGN KEY (counsellor_id) REFERENCES users(id),
    FOREIGN KEY (session_id) REFERENCES chat_sessions(id)
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);
CREATE INDEX IF NOT EXISTS idx_users_role ON users(role);

CREATE INDEX IF NOT EXISTS idx_chat_sessions_user_id ON chat_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_token ON chat_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_chat_sessions_risk_level ON chat_sessions(current_risk_level);

CREATE INDEX IF NOT EXISTS idx_chat_messages_session_id ON chat_messages(session_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_timestamp ON chat_messages(timestamp);

CREATE INDEX IF NOT EXISTS idx_risk_assessments_session_id ON risk_assessments(session_id);
CREATE INDEX IF NOT EXISTS idx_risk_assessments_risk_level ON risk_assessments(risk_level);

CREATE INDEX IF NOT EXISTS idx_interventions_category ON interventions(category);
CREATE INDEX IF NOT EXISTS idx_interventions_active ON interventions(is_active);

CREATE INDEX IF NOT EXISTS idx_counsellor_assignments_counsellor ON counsellor_assignments(counsellor_id);
CREATE INDEX IF NOT EXISTS idx_counsellor_assignments_student ON counsellor_assignments(student_id);
CREATE INDEX IF NOT EXISTS idx_counsellor_assignments_status ON counsellor_assignments(status);

-- Insert default interventions
INSERT OR IGNORE INTO interventions (name, category, description, content, min_risk_level, max_risk_level) VALUES
('5-4-3-2-1 Grounding', 'breathing', 'A grounding technique for anxiety', 'Let''s try the 5-4-3-2-1 grounding technique:

5 things you can see around you
4 things you can touch  
3 things you can hear
2 things you can smell
1 thing you can taste

Take your time with each step and focus on the present moment.', 'low', 'high'),

('Box Breathing', 'breathing', 'Simple breathing exercise for stress relief', 'Let''s do some box breathing together:

1. Breathe in for 4 counts
2. Hold for 4 counts
3. Breathe out for 4 counts
4. Hold for 4 counts

Repeat this cycle 4-6 times. Focus only on your breathing.', 'low', 'high'),

('Quick Mood Check-in', 'cbt', 'Cognitive behavioral technique for self-awareness', 'Take a moment to check in with yourself:

• What am I feeling right now?
• What thoughts are going through my mind?
• What''s happening in my body?
• What do I need right now?

There are no wrong answers - just observe without judgment.', 'low', 'medium'),

('Thought Challenge', 'cbt', 'Challenge negative thought patterns', 'When we''re struggling, our thoughts can become very negative. Let''s examine them:

1. What''s the specific thought bothering you?
2. Is this thought helpful or accurate?
3. What would you tell a friend having this thought?
4. What''s a more balanced way to think about this?

Remember: thoughts are not facts.', 'medium', 'high'),

('Values Reminder', 'journaling', 'Connect with personal values and meaning', 'Sometimes when we''re struggling, we lose sight of what matters to us. Take a moment to think about:

• What are 3 things that are important to you?
• What gives your life meaning?
• What would your best self do in this situation?
• What small step could you take today that aligns with your values?

Your worth isn''t determined by your struggles.', 'medium', 'high');

-- Create demo users (password is 'password123' hashed with bcrypt)
INSERT OR IGNORE INTO users (email, username, hashed_password, full_name, role, campus, year_of_study) VALUES
('student@demo.com', 'demo_student', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz.t/2OOd3z0gMnfhFbEZqJQCq6XAPO', 'Demo Student', 'student', 'Demo University', 2),
('counsellor@demo.com', 'demo_counsellor', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz.t/2OOd3z0gMnfhFbEZqJQCq6XAPO', 'Demo Counsellor', 'counsellor', NULL, NULL),
('admin@demo.com', 'demo_admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz.t/2OOd3z0gMnfhFbEZqJQCq6XAPO', 'Demo Admin', 'admin', NULL, NULL);