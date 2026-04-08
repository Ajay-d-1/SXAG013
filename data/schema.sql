CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    topic TEXT,
    mode TEXT,
    confidence REAL,
    depth INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS papers (
    paper_id TEXT PRIMARY KEY,
    session_id TEXT,
    title TEXT,
    abstract TEXT,
    year INTEGER,
    credibility_score INTEGER,
    red_flags TEXT,
    main_claims TEXT
);

CREATE TABLE IF NOT EXISTS contradictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT,
    paper_a_title TEXT,
    paper_b_title TEXT,
    claim_a TEXT,
    claim_b TEXT,
    severity TEXT,
    explanation TEXT
);
