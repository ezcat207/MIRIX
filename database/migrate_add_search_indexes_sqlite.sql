-- SQLite Database Migration Script for Mirix
-- Adds search indexes for Memory Search and Pagination (Phase 2)
-- Improves search performance across all memory types
-- Date: 2025-11-23

-- Note: SQLite doesn't support GIN indexes or partial indexes like PostgreSQL
-- We use standard B-tree indexes which are still effective for LIKE queries

BEGIN TRANSACTION;

-- ============================================================================
-- Raw Memory Indexes
-- ============================================================================

-- Index on source_app for filtering by application
CREATE INDEX IF NOT EXISTS idx_raw_memory_source_app ON raw_memory(source_app);

-- Index on source_url for URL searches
CREATE INDEX IF NOT EXISTS idx_raw_memory_source_url ON raw_memory(source_url);

-- Index on captured_at for time-based sorting
CREATE INDEX IF NOT EXISTS idx_raw_memory_captured_at ON raw_memory(captured_at DESC);

-- Note: SQLite FTS (Full-Text Search) could be added via virtual table for ocr_text
-- For now, we rely on the standard index for LIKE queries

-- ============================================================================
-- Semantic Memory Indexes
-- ============================================================================

-- Index on name for name searches
CREATE INDEX IF NOT EXISTS idx_semantic_memory_name ON semantic_memory(name);

-- Index on summary for searches (B-tree index, helps with LIKE queries)
CREATE INDEX IF NOT EXISTS idx_semantic_memory_summary ON semantic_memory(summary);

-- Note: SQLite doesn't support functional indexes on JSON fields
-- We can't create an index on (last_modify->>'timestamp')
-- Sorting will rely on sequential scan, which is acceptable for development

-- ============================================================================
-- Episodic Memory Indexes
-- ============================================================================

-- Index on summary for searches
CREATE INDEX IF NOT EXISTS idx_episodic_memory_summary ON episodic_memory(summary);

-- Index on event_type for filtering
CREATE INDEX IF NOT EXISTS idx_episodic_memory_event_type ON episodic_memory(event_type);

-- Index on actor for filtering
CREATE INDEX IF NOT EXISTS idx_episodic_memory_actor ON episodic_memory(actor);

-- Index on occurred_at for time-based sorting
CREATE INDEX IF NOT EXISTS idx_episodic_memory_occurred_at ON episodic_memory(occurred_at DESC);

-- ============================================================================
-- Procedural Memory Indexes
-- ============================================================================

-- Index on summary for searches
CREATE INDEX IF NOT EXISTS idx_procedural_memory_summary ON procedural_memory(summary);

-- Index on entry_type for filtering
CREATE INDEX IF NOT EXISTS idx_procedural_memory_entry_type ON procedural_memory(entry_type);

-- ============================================================================
-- Resource Memory Indexes
-- ============================================================================

-- Index on title for title searches
CREATE INDEX IF NOT EXISTS idx_resource_memory_title ON resource_memory(title);

-- Index on summary for searches
CREATE INDEX IF NOT EXISTS idx_resource_memory_summary ON resource_memory(summary);

-- Index on resource_type for filtering
CREATE INDEX IF NOT EXISTS idx_resource_memory_resource_type ON resource_memory(resource_type);

-- ============================================================================
-- Analyze tables to update statistics
-- ============================================================================

ANALYZE raw_memory;
ANALYZE semantic_memory;
ANALYZE episodic_memory;
ANALYZE procedural_memory;
ANALYZE resource_memory;

COMMIT;

-- Print summary (SQLite doesn't have RAISE NOTICE, so this is just a comment)
-- ============================================
-- Search Index Migration Completed!
-- ============================================
-- Created indexes for:
-- - Raw Memory: 3 indexes (source_app, source_url, captured_at)
-- - Semantic Memory: 2 indexes (name, summary)
-- - Episodic Memory: 4 indexes (summary, event_type, actor, occurred_at)
-- - Procedural Memory: 2 indexes (summary, entry_type)
-- - Resource Memory: 3 indexes (title, summary, resource_type)
--
-- Total: 14 indexes created for optimal search performance
-- ============================================
