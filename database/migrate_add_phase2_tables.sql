-- PostgreSQL Database Migration Script for Mirix
-- Adds Phase 2 tables: work_session, project, task, pattern, insight, goal
-- Part of Phase 2: Growth & Productivity Tracking

-- Start transaction to ensure atomicity
BEGIN;

-- Create a function to check if a column exists
CREATE OR REPLACE FUNCTION column_exists(tbl_name text, col_name text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND table_name = tbl_name
        AND column_name = col_name
    );
END;
$$ LANGUAGE plpgsql;

-- Create a function to check if a table exists
CREATE OR REPLACE FUNCTION table_exists(tbl_name text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM information_schema.tables
        WHERE table_schema = 'public'
        AND table_name = tbl_name
    );
END;
$$ LANGUAGE plpgsql;

-- Migration 1: Create work_session table if it doesn't exist
DO $$
BEGIN
    IF NOT table_exists('work_session') THEN
        CREATE TABLE work_session (
            -- Primary key
            id VARCHAR PRIMARY KEY,

            -- Time range
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP NOT NULL,
            duration INTEGER NOT NULL,

            -- Project association
            project_id VARCHAR,

            -- Activity classification
            activity_type VARCHAR NOT NULL,

            -- AI-calculated metrics
            focus_score REAL NOT NULL DEFAULT 5.0,

            -- App usage breakdown
            app_breakdown JSONB DEFAULT '{}'::jsonb NOT NULL,

            -- Additional metadata
            metadata_ JSONB DEFAULT '{}'::jsonb,

            -- Last modification tracking
            last_modify JSONB NOT NULL DEFAULT jsonb_build_object(
                'timestamp', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                'operation', 'created'
            ),

            -- Created timestamp
            created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),

            -- Raw memory references
            raw_memory_references JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Foreign keys
            user_id VARCHAR NOT NULL,
            organization_id VARCHAR NOT NULL,

            -- Audit fields (from SqlalchemyBase)
            updated_at TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false NOT NULL,
            _created_by_id VARCHAR,
            _last_updated_by_id VARCHAR,

            -- Constraints
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );

        -- Create indexes for common queries
        CREATE INDEX idx_work_session_user_id ON work_session(user_id);
        CREATE INDEX idx_work_session_organization_id ON work_session(organization_id);
        CREATE INDEX idx_work_session_start_time ON work_session(start_time DESC);
        CREATE INDEX idx_work_session_project_id ON work_session(project_id);
        CREATE INDEX idx_work_session_activity_type ON work_session(activity_type);

        RAISE NOTICE '✓ Created work_session table';
    ELSE
        RAISE NOTICE '✓ Skipped: work_session table already exists';
    END IF;
END;
$$;

-- Migration 2: Create project table if it doesn't exist
DO $$
BEGIN
    IF NOT table_exists('project') THEN
        CREATE TABLE project (
            -- Primary key
            id VARCHAR PRIMARY KEY,

            -- Basic info
            name VARCHAR NOT NULL,
            description VARCHAR NOT NULL,

            -- Status and priority
            status VARCHAR NOT NULL DEFAULT 'active',
            priority INTEGER NOT NULL DEFAULT 5,

            -- Progress tracking
            progress REAL NOT NULL DEFAULT 0.0,
            total_time_spent INTEGER NOT NULL DEFAULT 0,

            -- Date tracking
            start_date TIMESTAMP NOT NULL,
            target_end_date TIMESTAMP,
            actual_end_date TIMESTAMP,

            -- Goals association
            related_goals JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Additional metadata
            metadata_ JSONB DEFAULT '{}'::jsonb,

            -- Last modification tracking
            last_modify JSONB NOT NULL DEFAULT jsonb_build_object(
                'timestamp', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                'operation', 'created'
            ),

            -- Created timestamp
            created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),

            -- Embedding configuration
            embedding_config JSONB,

            -- Vector embedding field (pgvector)
            description_embedding vector(1536),

            -- Foreign keys
            user_id VARCHAR NOT NULL,
            organization_id VARCHAR NOT NULL,

            -- Audit fields
            updated_at TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false NOT NULL,
            _created_by_id VARCHAR,
            _last_updated_by_id VARCHAR,

            -- Constraints
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );

        -- Create indexes
        CREATE INDEX idx_project_user_id ON project(user_id);
        CREATE INDEX idx_project_organization_id ON project(organization_id);
        CREATE INDEX idx_project_status ON project(status);
        CREATE INDEX idx_project_priority ON project(priority DESC);
        CREATE INDEX idx_project_start_date ON project(start_date DESC);

        RAISE NOTICE '✓ Created project table';
    ELSE
        RAISE NOTICE '✓ Skipped: project table already exists';
    END IF;
END;
$$;

-- Migration 3: Create task table if it doesn't exist
DO $$
BEGIN
    IF NOT table_exists('task') THEN
        CREATE TABLE task (
            -- Primary key
            id VARCHAR PRIMARY KEY,

            -- Basic info
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,

            -- Status and priority
            status VARCHAR NOT NULL DEFAULT 'todo',
            priority INTEGER NOT NULL DEFAULT 5,

            -- Project association
            project_id VARCHAR,

            -- Time tracking
            estimated_hours REAL,
            actual_hours REAL,

            -- Date tracking
            due_date TIMESTAMP,
            completed_at TIMESTAMP,

            -- Task relationships
            dependencies JSONB DEFAULT '[]'::jsonb NOT NULL,
            blocking JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Additional metadata
            metadata_ JSONB DEFAULT '{}'::jsonb,

            -- Last modification tracking
            last_modify JSONB NOT NULL DEFAULT jsonb_build_object(
                'timestamp', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                'operation', 'created'
            ),

            -- Created timestamp
            created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),

            -- Embedding configuration
            embedding_config JSONB,

            -- Vector embedding field
            description_embedding vector(1536),

            -- Foreign keys
            user_id VARCHAR NOT NULL,
            organization_id VARCHAR NOT NULL,

            -- Audit fields
            updated_at TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false NOT NULL,
            _created_by_id VARCHAR,
            _last_updated_by_id VARCHAR,

            -- Constraints
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );

        -- Create indexes
        CREATE INDEX idx_task_user_id ON task(user_id);
        CREATE INDEX idx_task_organization_id ON task(organization_id);
        CREATE INDEX idx_task_status ON task(status);
        CREATE INDEX idx_task_priority ON task(priority DESC);
        CREATE INDEX idx_task_project_id ON task(project_id);
        CREATE INDEX idx_task_due_date ON task(due_date);

        RAISE NOTICE '✓ Created task table';
    ELSE
        RAISE NOTICE '✓ Skipped: task table already exists';
    END IF;
END;
$$;

-- Migration 4: Create pattern table if it doesn't exist
DO $$
BEGIN
    IF NOT table_exists('pattern') THEN
        CREATE TABLE pattern (
            -- Primary key
            id VARCHAR PRIMARY KEY,

            -- Pattern classification
            pattern_type VARCHAR NOT NULL,

            -- Basic info
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,

            -- AI metrics
            confidence REAL NOT NULL,
            frequency VARCHAR NOT NULL,

            -- Evidence
            evidence JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Time tracking
            first_detected TIMESTAMP NOT NULL,
            last_confirmed TIMESTAMP NOT NULL,

            -- Additional metadata
            metadata_ JSONB DEFAULT '{}'::jsonb,

            -- Last modification tracking
            last_modify JSONB NOT NULL DEFAULT jsonb_build_object(
                'timestamp', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                'operation', 'created'
            ),

            -- Created timestamp
            created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),

            -- Embedding configuration
            embedding_config JSONB,

            -- Vector embedding field
            description_embedding vector(1536),

            -- Foreign keys
            user_id VARCHAR NOT NULL,
            organization_id VARCHAR NOT NULL,

            -- Audit fields
            updated_at TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false NOT NULL,
            _created_by_id VARCHAR,
            _last_updated_by_id VARCHAR,

            -- Constraints
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );

        -- Create indexes
        CREATE INDEX idx_pattern_user_id ON pattern(user_id);
        CREATE INDEX idx_pattern_organization_id ON pattern(organization_id);
        CREATE INDEX idx_pattern_pattern_type ON pattern(pattern_type);
        CREATE INDEX idx_pattern_confidence ON pattern(confidence DESC);
        CREATE INDEX idx_pattern_last_confirmed ON pattern(last_confirmed DESC);

        RAISE NOTICE '✓ Created pattern table';
    ELSE
        RAISE NOTICE '✓ Skipped: pattern table already exists';
    END IF;
END;
$$;

-- Migration 5: Create insight table if it doesn't exist
DO $$
BEGIN
    IF NOT table_exists('insight') THEN
        CREATE TABLE insight (
            -- Primary key
            id VARCHAR PRIMARY KEY,

            -- Insight classification
            category VARCHAR NOT NULL,

            -- Basic info
            title VARCHAR NOT NULL,
            content VARCHAR NOT NULL,

            -- Actionable steps
            action_items JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Scoring
            priority INTEGER NOT NULL DEFAULT 5,
            impact_score REAL NOT NULL,

            -- Pattern relationships
            related_patterns JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Status tracking
            status VARCHAR NOT NULL DEFAULT 'new',

            -- Time tracking
            generated_at TIMESTAMP NOT NULL,
            acknowledged_at TIMESTAMP,
            applied_at TIMESTAMP,

            -- Additional metadata
            metadata_ JSONB DEFAULT '{}'::jsonb,

            -- Last modification tracking
            last_modify JSONB NOT NULL DEFAULT jsonb_build_object(
                'timestamp', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                'operation', 'created'
            ),

            -- Created timestamp
            created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),

            -- Embedding configuration
            embedding_config JSONB,

            -- Vector embedding field
            content_embedding vector(1536),

            -- Foreign keys
            user_id VARCHAR NOT NULL,
            organization_id VARCHAR NOT NULL,

            -- Audit fields
            updated_at TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false NOT NULL,
            _created_by_id VARCHAR,
            _last_updated_by_id VARCHAR,

            -- Constraints
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );

        -- Create indexes
        CREATE INDEX idx_insight_user_id ON insight(user_id);
        CREATE INDEX idx_insight_organization_id ON insight(organization_id);
        CREATE INDEX idx_insight_category ON insight(category);
        CREATE INDEX idx_insight_status ON insight(status);
        CREATE INDEX idx_insight_priority ON insight(priority DESC);
        CREATE INDEX idx_insight_impact_score ON insight(impact_score DESC);
        CREATE INDEX idx_insight_generated_at ON insight(generated_at DESC);

        RAISE NOTICE '✓ Created insight table';
    ELSE
        RAISE NOTICE '✓ Skipped: insight table already exists';
    END IF;
END;
$$;

-- Migration 6: Create goal table if it doesn't exist
DO $$
BEGIN
    IF NOT table_exists('goal') THEN
        CREATE TABLE goal (
            -- Primary key
            id VARCHAR PRIMARY KEY,

            -- Goal classification
            goal_type VARCHAR NOT NULL,

            -- Basic info
            title VARCHAR NOT NULL,
            description VARCHAR NOT NULL,

            -- Progress tracking
            target_date TIMESTAMP,
            progress REAL NOT NULL DEFAULT 0.0,
            status VARCHAR NOT NULL DEFAULT 'active',

            -- Milestones
            milestones JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Related entities
            related_projects JSONB DEFAULT '[]'::jsonb NOT NULL,
            related_insights JSONB DEFAULT '[]'::jsonb NOT NULL,

            -- Additional metadata
            metadata_ JSONB DEFAULT '{}'::jsonb,

            -- Last modification tracking
            last_modify JSONB NOT NULL DEFAULT jsonb_build_object(
                'timestamp', to_char(now() AT TIME ZONE 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS.MS"Z"'),
                'operation', 'created'
            ),

            -- Created timestamp
            created_at TIMESTAMP NOT NULL DEFAULT (now() AT TIME ZONE 'UTC'),

            -- Achievement timestamp
            achieved_at TIMESTAMP,

            -- Embedding configuration
            embedding_config JSONB,

            -- Vector embedding field
            description_embedding vector(1536),

            -- Foreign keys
            user_id VARCHAR NOT NULL,
            organization_id VARCHAR NOT NULL,

            -- Audit fields
            updated_at TIMESTAMP,
            is_deleted BOOLEAN DEFAULT false NOT NULL,
            _created_by_id VARCHAR,
            _last_updated_by_id VARCHAR,

            -- Constraints
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
        );

        -- Create indexes
        CREATE INDEX idx_goal_user_id ON goal(user_id);
        CREATE INDEX idx_goal_organization_id ON goal(organization_id);
        CREATE INDEX idx_goal_goal_type ON goal(goal_type);
        CREATE INDEX idx_goal_status ON goal(status);
        CREATE INDEX idx_goal_target_date ON goal(target_date);
        CREATE INDEX idx_goal_progress ON goal(progress DESC);

        RAISE NOTICE '✓ Created goal table';
    ELSE
        RAISE NOTICE '✓ Skipped: goal table already exists';
    END IF;
END;
$$;

-- Verification: Check that all required tables exist
DO $$
DECLARE
    table_name text;
    required_tables text[] := ARRAY[
        'work_session',
        'project',
        'task',
        'pattern',
        'insight',
        'goal'
    ];
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🔍 Verifying migration...';

    -- Check that all tables exist
    FOR i IN 1..array_length(required_tables, 1) LOOP
        table_name := required_tables[i];

        IF table_exists(table_name) THEN
            RAISE NOTICE '✓ % table exists', table_name;
        ELSE
            RAISE NOTICE '❌ % table missing', table_name;
        END IF;
    END LOOP;
END;
$$;

-- Clean up temporary functions
DROP FUNCTION IF EXISTS column_exists(text, text);
DROP FUNCTION IF EXISTS table_exists(text);

-- Commit the transaction
COMMIT;

-- Final success message
DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '✅ PostgreSQL migration for Phase 2 tables completed successfully!';
    RAISE NOTICE 'All schema changes have been applied and verified.';
    RAISE NOTICE 'Phase 2 tables: work_session, project, task, pattern, insight, goal';
END;
$$;
