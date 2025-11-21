#!/usr/bin/env python3
"""
Phase 2 SQLite Migration Script for Mirix
Creates Phase 2 tables: work_session, project, task, pattern, insight, goal
Part of Phase 2: Growth & Productivity Tracking
"""

import os
import shutil
import sqlite3
import sys
from datetime import datetime


def backup_database(db_path):
    """Create a backup of the database before migration"""
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"✓ Created backup: {backup_path}")
    return backup_path


def check_table_exists(conn, table_name):
    """Check if a table exists"""
    cursor = conn.cursor()
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,)
    )
    return cursor.fetchone() is not None


def get_default_user_id(conn):
    """Get a default user ID for foreign key constraints"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users LIMIT 1")
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        raise Exception(
            "No users found in database. Please create a user before running Phase 2 migration."
        )


def get_default_organization_id(conn):
    """Get a default organization ID for foreign key constraints"""
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM organizations LIMIT 1")
    result = cursor.fetchone()

    if result:
        return result[0]
    else:
        raise Exception(
            "No organizations found in database. Please create an organization before running Phase 2 migration."
        )


def migrate_phase2_tables(db_path):
    """Create Phase 2 tables in SQLite database"""

    print(f"\n🚀 Starting Phase 2 migration for: {db_path}")

    # Create backup
    backup_path = backup_database(db_path)

    # Connect to the database
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = OFF")  # Disable foreign keys during migration

    try:
        # Verify that users and organizations exist
        default_user_id = get_default_user_id(conn)
        default_org_id = get_default_organization_id(conn)
        print(f"✓ Using user_id: {default_user_id}")
        print(f"✓ Using organization_id: {default_org_id}")

        # Migration steps for Phase 2 tables
        migrations = [
            # 1. Create work_session table
            {
                "name": "Create work_session table",
                "check": lambda: check_table_exists(conn, "work_session"),
                "execute": lambda: conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS work_session (
                        id VARCHAR PRIMARY KEY,
                        start_time TIMESTAMP NOT NULL,
                        end_time TIMESTAMP NOT NULL,
                        duration INTEGER NOT NULL,
                        project_id VARCHAR,
                        activity_type VARCHAR NOT NULL,
                        focus_score REAL NOT NULL DEFAULT 5.0,
                        app_breakdown JSON DEFAULT '{}' NOT NULL,
                        metadata_ JSON DEFAULT '{}',
                        last_modify JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        raw_memory_references JSON DEFAULT '[]' NOT NULL,
                        user_id VARCHAR NOT NULL,
                        organization_id VARCHAR NOT NULL,
                        updated_at TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0 NOT NULL,
                        _created_by_id VARCHAR,
                        _last_updated_by_id VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
                    )
                    """
                ),
            },
            # 2. Create project table
            {
                "name": "Create project table",
                "check": lambda: check_table_exists(conn, "project"),
                "execute": lambda: conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS project (
                        id VARCHAR PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        description VARCHAR NOT NULL,
                        status VARCHAR NOT NULL DEFAULT 'active',
                        priority INTEGER NOT NULL DEFAULT 5,
                        progress REAL NOT NULL DEFAULT 0.0,
                        total_time_spent INTEGER NOT NULL DEFAULT 0,
                        start_date TIMESTAMP NOT NULL,
                        target_end_date TIMESTAMP,
                        actual_end_date TIMESTAMP,
                        related_goals JSON DEFAULT '[]' NOT NULL,
                        metadata_ JSON DEFAULT '{}',
                        last_modify JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        embedding_config JSON,
                        description_embedding BLOB,
                        user_id VARCHAR NOT NULL,
                        organization_id VARCHAR NOT NULL,
                        updated_at TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0 NOT NULL,
                        _created_by_id VARCHAR,
                        _last_updated_by_id VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
                    )
                    """
                ),
            },
            # 3. Create task table
            {
                "name": "Create task table",
                "check": lambda: check_table_exists(conn, "task"),
                "execute": lambda: conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS task (
                        id VARCHAR PRIMARY KEY,
                        title VARCHAR NOT NULL,
                        description VARCHAR NOT NULL,
                        status VARCHAR NOT NULL DEFAULT 'todo',
                        priority INTEGER NOT NULL DEFAULT 5,
                        project_id VARCHAR,
                        estimated_hours REAL,
                        actual_hours REAL,
                        due_date TIMESTAMP,
                        completed_at TIMESTAMP,
                        dependencies JSON DEFAULT '[]' NOT NULL,
                        blocking JSON DEFAULT '[]' NOT NULL,
                        metadata_ JSON DEFAULT '{}',
                        last_modify JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        embedding_config JSON,
                        description_embedding BLOB,
                        user_id VARCHAR NOT NULL,
                        organization_id VARCHAR NOT NULL,
                        updated_at TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0 NOT NULL,
                        _created_by_id VARCHAR,
                        _last_updated_by_id VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
                    )
                    """
                ),
            },
            # 4. Create pattern table
            {
                "name": "Create pattern table",
                "check": lambda: check_table_exists(conn, "pattern"),
                "execute": lambda: conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS pattern (
                        id VARCHAR PRIMARY KEY,
                        pattern_type VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        description VARCHAR NOT NULL,
                        confidence REAL NOT NULL,
                        frequency VARCHAR NOT NULL,
                        evidence JSON DEFAULT '[]' NOT NULL,
                        first_detected TIMESTAMP NOT NULL,
                        last_confirmed TIMESTAMP NOT NULL,
                        metadata_ JSON DEFAULT '{}',
                        last_modify JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        embedding_config JSON,
                        description_embedding BLOB,
                        user_id VARCHAR NOT NULL,
                        organization_id VARCHAR NOT NULL,
                        updated_at TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0 NOT NULL,
                        _created_by_id VARCHAR,
                        _last_updated_by_id VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
                    )
                    """
                ),
            },
            # 5. Create insight table
            {
                "name": "Create insight table",
                "check": lambda: check_table_exists(conn, "insight"),
                "execute": lambda: conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS insight (
                        id VARCHAR PRIMARY KEY,
                        category VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        content VARCHAR NOT NULL,
                        action_items JSON DEFAULT '[]' NOT NULL,
                        priority INTEGER NOT NULL DEFAULT 5,
                        impact_score REAL NOT NULL,
                        related_patterns JSON DEFAULT '[]' NOT NULL,
                        status VARCHAR NOT NULL DEFAULT 'new',
                        generated_at TIMESTAMP NOT NULL,
                        acknowledged_at TIMESTAMP,
                        applied_at TIMESTAMP,
                        metadata_ JSON DEFAULT '{}',
                        last_modify JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        embedding_config JSON,
                        content_embedding BLOB,
                        user_id VARCHAR NOT NULL,
                        organization_id VARCHAR NOT NULL,
                        updated_at TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0 NOT NULL,
                        _created_by_id VARCHAR,
                        _last_updated_by_id VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
                    )
                    """
                ),
            },
            # 6. Create goal table
            {
                "name": "Create goal table",
                "check": lambda: check_table_exists(conn, "goal"),
                "execute": lambda: conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS goal (
                        id VARCHAR PRIMARY KEY,
                        goal_type VARCHAR NOT NULL,
                        title VARCHAR NOT NULL,
                        description VARCHAR NOT NULL,
                        target_date TIMESTAMP,
                        progress REAL NOT NULL DEFAULT 0.0,
                        status VARCHAR NOT NULL DEFAULT 'active',
                        milestones JSON DEFAULT '[]' NOT NULL,
                        related_projects JSON DEFAULT '[]' NOT NULL,
                        related_insights JSON DEFAULT '[]' NOT NULL,
                        metadata_ JSON DEFAULT '{}',
                        last_modify JSON NOT NULL,
                        created_at TIMESTAMP NOT NULL,
                        achieved_at TIMESTAMP,
                        embedding_config JSON,
                        description_embedding BLOB,
                        user_id VARCHAR NOT NULL,
                        organization_id VARCHAR NOT NULL,
                        updated_at TIMESTAMP,
                        is_deleted BOOLEAN DEFAULT 0 NOT NULL,
                        _created_by_id VARCHAR,
                        _last_updated_by_id VARCHAR,
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                        FOREIGN KEY (organization_id) REFERENCES organizations(id) ON DELETE CASCADE
                    )
                    """
                ),
            },
        ]

        # Execute migrations
        print("\n📊 Executing migrations:")
        for migration in migrations:
            if not migration["check"]():
                print(f"  ⏳ {migration['name']}")
                migration["execute"]()
                conn.commit()
                print(f"  ✓ Completed: {migration['name']}")
            else:
                print(f"  ✓ Skipped (already exists): {migration['name']}")

        # Create indexes for better query performance
        print("\n📇 Creating indexes:")
        indexes = [
            # work_session indexes
            "CREATE INDEX IF NOT EXISTS idx_work_session_user_id ON work_session(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_work_session_organization_id ON work_session(organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_work_session_start_time ON work_session(start_time DESC)",
            "CREATE INDEX IF NOT EXISTS idx_work_session_project_id ON work_session(project_id)",
            # project indexes
            "CREATE INDEX IF NOT EXISTS idx_project_user_id ON project(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_project_organization_id ON project(organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_project_status ON project(status)",
            "CREATE INDEX IF NOT EXISTS idx_project_priority ON project(priority DESC)",
            # task indexes
            "CREATE INDEX IF NOT EXISTS idx_task_user_id ON task(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_organization_id ON task(organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_task_status ON task(status)",
            "CREATE INDEX IF NOT EXISTS idx_task_project_id ON task(project_id)",
            # pattern indexes
            "CREATE INDEX IF NOT EXISTS idx_pattern_user_id ON pattern(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_pattern_organization_id ON pattern(organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_pattern_pattern_type ON pattern(pattern_type)",
            # insight indexes
            "CREATE INDEX IF NOT EXISTS idx_insight_user_id ON insight(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_insight_organization_id ON insight(organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_insight_status ON insight(status)",
            "CREATE INDEX IF NOT EXISTS idx_insight_priority ON insight(priority DESC)",
            # goal indexes
            "CREATE INDEX IF NOT EXISTS idx_goal_user_id ON goal(user_id)",
            "CREATE INDEX IF NOT EXISTS idx_goal_organization_id ON goal(organization_id)",
            "CREATE INDEX IF NOT EXISTS idx_goal_status ON goal(status)",
        ]

        for index_sql in indexes:
            conn.execute(index_sql)
        conn.commit()
        print(f"  ✓ Created {len(indexes)} indexes")

        # Re-enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        conn.commit()

        print("\n🔍 Verifying migration...")
        verify_migration(conn)

        print("\n✅ Phase 2 migration completed successfully!")
        print(f"  Database: {db_path}")
        print(f"  Backup: {backup_path}")
        print(
            "  Tables created: work_session, project, task, pattern, insight, goal"
        )

    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()


def verify_migration(conn):
    """Verify that the migration was successful"""
    required_tables = [
        "work_session",
        "project",
        "task",
        "pattern",
        "insight",
        "goal",
    ]

    for table in required_tables:
        if check_table_exists(conn, table):
            print(f"  ✓ {table} table exists")
        else:
            print(f"  ❌ {table} table missing")


def main():
    # Default to migrating ~/.mirix/sqlite.db
    mirix_db_path = os.path.expanduser("~/.mirix/sqlite.db")

    if len(sys.argv) == 1:
        # No arguments - migrate ~/.mirix/sqlite.db
        db_path = mirix_db_path
    elif len(sys.argv) == 2:
        # One argument - custom database path
        db_path = sys.argv[1]
    else:
        print("Usage:")
        print(
            "  python run_phase2_sqlite_migration.py                    # Migrate ~/.mirix/sqlite.db"
        )
        print(
            "  python run_phase2_sqlite_migration.py <db_path>          # Migrate custom database"
        )
        print("")
        print("Examples:")
        print("  python run_phase2_sqlite_migration.py")
        print("  python run_phase2_sqlite_migration.py /path/to/mirix.db")
        sys.exit(1)

    # Validate database path
    if not os.path.exists(db_path):
        print(f"❌ Database not found: {db_path}")
        print("Make sure Mirix has been run at least once to create the database.")
        sys.exit(1)

    print("=" * 70)
    print("MIRIX Phase 2 Database Migration")
    print("=" * 70)
    print(f"\n📁 Database: {db_path}")
    print("📦 Tables to create: work_session, project, task, pattern, insight, goal")
    print("\n⚠️  A backup will be created automatically")

    response = input("\n❓ Proceed with migration? (y/N): ")
    if response.lower() != "y":
        print("Migration cancelled.")
        sys.exit(0)

    try:
        migrate_phase2_tables(db_path)
    except Exception as e:
        print(f"\n❌ Migration failed: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
