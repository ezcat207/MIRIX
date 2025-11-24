-- PostgreSQL Database Migration Script for Mirix
-- Adds search indexes for Memory Search and Pagination (Phase 2)
-- Improves search performance across all memory types
-- Date: 2025-11-23

-- Start transaction to ensure atomicity
BEGIN;

-- Create a function to check if an index exists
CREATE OR REPLACE FUNCTION index_exists(idx_name text)
RETURNS boolean AS $$
BEGIN
    RETURN EXISTS (
        SELECT 1
        FROM pg_indexes
        WHERE schemaname = 'public'
        AND indexname = idx_name
    );
END;
$$ LANGUAGE plpgsql;

-- ============================================================================
-- Raw Memory Indexes
-- ============================================================================

-- Index on source_app for filtering by application
DO $$
BEGIN
    IF NOT index_exists('idx_raw_memory_source_app') THEN
        CREATE INDEX idx_raw_memory_source_app ON raw_memory(source_app);
        RAISE NOTICE 'Created index: idx_raw_memory_source_app';
    ELSE
        RAISE NOTICE 'Index already exists: idx_raw_memory_source_app';
    END IF;
END $$;

-- Index on source_url for URL searches
DO $$
BEGIN
    IF NOT index_exists('idx_raw_memory_source_url') THEN
        CREATE INDEX idx_raw_memory_source_url ON raw_memory(source_url);
        RAISE NOTICE 'Created index: idx_raw_memory_source_url';
    ELSE
        RAISE NOTICE 'Index already exists: idx_raw_memory_source_url';
    END IF;
END $$;

-- GIN index on ocr_text for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_raw_memory_ocr_text_gin') THEN
        CREATE INDEX idx_raw_memory_ocr_text_gin ON raw_memory USING gin(to_tsvector('english', COALESCE(ocr_text, '')));
        RAISE NOTICE 'Created GIN index: idx_raw_memory_ocr_text_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_raw_memory_ocr_text_gin';
    END IF;
END $$;

-- Index on captured_at for time-based sorting
DO $$
BEGIN
    IF NOT index_exists('idx_raw_memory_captured_at') THEN
        CREATE INDEX idx_raw_memory_captured_at ON raw_memory(captured_at DESC);
        RAISE NOTICE 'Created index: idx_raw_memory_captured_at';
    ELSE
        RAISE NOTICE 'Index already exists: idx_raw_memory_captured_at';
    END IF;
END $$;

-- ============================================================================
-- Semantic Memory Indexes
-- ============================================================================

-- Index on name for name searches
DO $$
BEGIN
    IF NOT index_exists('idx_semantic_memory_name') THEN
        CREATE INDEX idx_semantic_memory_name ON semantic_memory(name);
        RAISE NOTICE 'Created index: idx_semantic_memory_name';
    ELSE
        RAISE NOTICE 'Index already exists: idx_semantic_memory_name';
    END IF;
END $$;

-- GIN index on summary for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_semantic_memory_summary_gin') THEN
        CREATE INDEX idx_semantic_memory_summary_gin ON semantic_memory USING gin(to_tsvector('english', COALESCE(summary, '')));
        RAISE NOTICE 'Created GIN index: idx_semantic_memory_summary_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_semantic_memory_summary_gin';
    END IF;
END $$;

-- GIN index on details for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_semantic_memory_details_gin') THEN
        CREATE INDEX idx_semantic_memory_details_gin ON semantic_memory USING gin(to_tsvector('english', COALESCE(details, '')));
        RAISE NOTICE 'Created GIN index: idx_semantic_memory_details_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_semantic_memory_details_gin';
    END IF;
END $$;

-- Index on last_modify timestamp for sorting
DO $$
BEGIN
    IF NOT index_exists('idx_semantic_memory_last_modify') THEN
        CREATE INDEX idx_semantic_memory_last_modify ON semantic_memory((last_modify->>'timestamp') DESC);
        RAISE NOTICE 'Created index: idx_semantic_memory_last_modify';
    ELSE
        RAISE NOTICE 'Index already exists: idx_semantic_memory_last_modify';
    END IF;
END $$;

-- ============================================================================
-- Episodic Memory Indexes
-- ============================================================================

-- GIN index on summary for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_episodic_memory_summary_gin') THEN
        CREATE INDEX idx_episodic_memory_summary_gin ON episodic_memory USING gin(to_tsvector('english', COALESCE(summary, '')));
        RAISE NOTICE 'Created GIN index: idx_episodic_memory_summary_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_episodic_memory_summary_gin';
    END IF;
END $$;

-- GIN index on details for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_episodic_memory_details_gin') THEN
        CREATE INDEX idx_episodic_memory_details_gin ON episodic_memory USING gin(to_tsvector('english', COALESCE(details, '')));
        RAISE NOTICE 'Created GIN index: idx_episodic_memory_details_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_episodic_memory_details_gin';
    END IF;
END $$;

-- Index on event_type for filtering
DO $$
BEGIN
    IF NOT index_exists('idx_episodic_memory_event_type') THEN
        CREATE INDEX idx_episodic_memory_event_type ON episodic_memory(event_type);
        RAISE NOTICE 'Created index: idx_episodic_memory_event_type';
    ELSE
        RAISE NOTICE 'Index already exists: idx_episodic_memory_event_type';
    END IF;
END $$;

-- Index on actor for filtering
DO $$
BEGIN
    IF NOT index_exists('idx_episodic_memory_actor') THEN
        CREATE INDEX idx_episodic_memory_actor ON episodic_memory(actor);
        RAISE NOTICE 'Created index: idx_episodic_memory_actor';
    ELSE
        RAISE NOTICE 'Index already exists: idx_episodic_memory_actor';
    END IF;
END $$;

-- Index on occurred_at for time-based sorting
DO $$
BEGIN
    IF NOT index_exists('idx_episodic_memory_occurred_at') THEN
        CREATE INDEX idx_episodic_memory_occurred_at ON episodic_memory(occurred_at DESC);
        RAISE NOTICE 'Created index: idx_episodic_memory_occurred_at';
    ELSE
        RAISE NOTICE 'Index already exists: idx_episodic_memory_occurred_at';
    END IF;
END $$;

-- ============================================================================
-- Procedural Memory Indexes
-- ============================================================================

-- GIN index on summary for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_procedural_memory_summary_gin') THEN
        CREATE INDEX idx_procedural_memory_summary_gin ON procedural_memory USING gin(to_tsvector('english', COALESCE(summary, '')));
        RAISE NOTICE 'Created GIN index: idx_procedural_memory_summary_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_procedural_memory_summary_gin';
    END IF;
END $$;

-- Index on entry_type for filtering
DO $$
BEGIN
    IF NOT index_exists('idx_procedural_memory_entry_type') THEN
        CREATE INDEX idx_procedural_memory_entry_type ON procedural_memory(entry_type);
        RAISE NOTICE 'Created index: idx_procedural_memory_entry_type';
    ELSE
        RAISE NOTICE 'Index already exists: idx_procedural_memory_entry_type';
    END IF;
END $$;

-- Index on last_modify timestamp for sorting
DO $$
BEGIN
    IF NOT index_exists('idx_procedural_memory_last_modify') THEN
        CREATE INDEX idx_procedural_memory_last_modify ON procedural_memory((last_modify->>'timestamp') DESC);
        RAISE NOTICE 'Created index: idx_procedural_memory_last_modify';
    ELSE
        RAISE NOTICE 'Index already exists: idx_procedural_memory_last_modify';
    END IF;
END $$;

-- ============================================================================
-- Resource Memory Indexes
-- ============================================================================

-- Index on title for title searches
DO $$
BEGIN
    IF NOT index_exists('idx_resource_memory_title') THEN
        CREATE INDEX idx_resource_memory_title ON resource_memory(title);
        RAISE NOTICE 'Created index: idx_resource_memory_title';
    ELSE
        RAISE NOTICE 'Index already exists: idx_resource_memory_title';
    END IF;
END $$;

-- GIN index on summary for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_resource_memory_summary_gin') THEN
        CREATE INDEX idx_resource_memory_summary_gin ON resource_memory USING gin(to_tsvector('english', COALESCE(summary, '')));
        RAISE NOTICE 'Created GIN index: idx_resource_memory_summary_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_resource_memory_summary_gin';
    END IF;
END $$;

-- GIN index on content for full-text search
DO $$
BEGIN
    IF NOT index_exists('idx_resource_memory_content_gin') THEN
        CREATE INDEX idx_resource_memory_content_gin ON resource_memory USING gin(to_tsvector('english', COALESCE(content, '')));
        RAISE NOTICE 'Created GIN index: idx_resource_memory_content_gin';
    ELSE
        RAISE NOTICE 'Index already exists: idx_resource_memory_content_gin';
    END IF;
END $$;

-- Index on resource_type for filtering
DO $$
BEGIN
    IF NOT index_exists('idx_resource_memory_resource_type') THEN
        CREATE INDEX idx_resource_memory_resource_type ON resource_memory(resource_type);
        RAISE NOTICE 'Created index: idx_resource_memory_resource_type';
    ELSE
        RAISE NOTICE 'Index already exists: idx_resource_memory_resource_type';
    END IF;
END $$;

-- Index on last_modify timestamp for sorting
DO $$
BEGIN
    IF NOT index_exists('idx_resource_memory_last_modify') THEN
        CREATE INDEX idx_resource_memory_last_modify ON resource_memory((last_modify->>'timestamp') DESC);
        RAISE NOTICE 'Created index: idx_resource_memory_last_modify';
    ELSE
        RAISE NOTICE 'Index already exists: idx_resource_memory_last_modify';
    END IF;
END $$;

-- ============================================================================
-- Clean up helper function
-- ============================================================================

DROP FUNCTION IF EXISTS index_exists(text);

-- Commit transaction
COMMIT;

-- ============================================================================
-- Performance Analysis
-- ============================================================================

-- Analyze tables to update statistics for the query planner
ANALYZE raw_memory;
ANALYZE semantic_memory;
ANALYZE episodic_memory;
ANALYZE procedural_memory;
ANALYZE resource_memory;

-- Print summary
DO $$
BEGIN
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Search Index Migration Completed!';
    RAISE NOTICE '============================================';
    RAISE NOTICE 'Created indexes for:';
    RAISE NOTICE '- Raw Memory: 4 indexes (source_app, source_url, ocr_text GIN, captured_at)';
    RAISE NOTICE '- Semantic Memory: 4 indexes (name, summary GIN, details GIN, last_modify)';
    RAISE NOTICE '- Episodic Memory: 5 indexes (summary GIN, details GIN, event_type, actor, occurred_at)';
    RAISE NOTICE '- Procedural Memory: 3 indexes (summary GIN, entry_type, last_modify)';
    RAISE NOTICE '- Resource Memory: 5 indexes (title, summary GIN, content GIN, resource_type, last_modify)';
    RAISE NOTICE '';
    RAISE NOTICE 'Total: 21 indexes created for optimal search performance';
    RAISE NOTICE '============================================';
END $$;
