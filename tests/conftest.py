"""
pytest fixtures for MIRIX test suite
"""

import os
import pytest
from datetime import datetime, timezone

# Force PostgreSQL mode and disable embeddings for faster testing
os.environ.setdefault("MIRIX_PG_URI", "postgresql+pg8000://power@localhost:5432/mirix")
os.environ["BUILD_EMBEDDINGS_FOR_MEMORY"] = "false"


@pytest.fixture(scope="session")
def db_context():
    """提供数据库上下文"""
    from mirix.server.server import db_context as _db_context
    return _db_context


@pytest.fixture(scope="session")
def test_organization(db_context):
    """创建或获取测试组织"""
    from mirix.orm import Organization

    org_id = "test-org-growth-analysis"
    with db_context() as session:
        org = session.query(Organization).filter_by(id=org_id).first()
        if not org:
            org = Organization(
                id=org_id,
                name="Test Organization for Growth Analysis"
            )
            session.add(org)
            session.commit()
            session.refresh(org)
    return org


@pytest.fixture(scope="session")
def test_user(db_context, test_organization):
    """创建或获取测试用户 (ORM)"""
    from mirix.orm.user import User

    # Use proper user ID format matching '^user-[a-fA-F0-9]{8}'
    user_id = "user-12345678"  # Test user ID
    with db_context() as session:
        user = session.query(User).filter_by(id=user_id).first()
        if not user:
            user = User(
                id=user_id,
                name="Test User for Growth Analysis",
                status="active",
                timezone="UTC",
                organization_id=test_organization.id
            )
            session.add(user)
            session.commit()
            session.refresh(user)
    return user


@pytest.fixture(scope="session")
def test_pydantic_user(test_user):
    """将 ORM User 转换为 Pydantic User"""
    from mirix.schemas.user import User as PydanticUser

    return PydanticUser(
        id=test_user.id,
        name=test_user.name,
        timezone=test_user.timezone,
        organization_id=test_user.organization_id
    )


@pytest.fixture(scope="function")
def clean_work_sessions(db_context, test_user, test_organization):
    """清理测试数据 - 在每个测试函数后清理"""
    yield

    # 清理 WorkSession, Pattern, Insight
    from mirix.orm.work_session import WorkSession
    from mirix.orm.pattern import Pattern
    from mirix.orm.insight import Insight
    from mirix.services.raw_memory_manager import RawMemoryManager

    with db_context() as session:
        # 删除测试创建的 WorkSession
        session.query(WorkSession).filter(
            WorkSession.user_id == test_user.id
        ).delete()

        # 删除测试创建的 Pattern
        session.query(Pattern).filter(
            Pattern.user_id == test_user.id
        ).delete()

        # 删除测试创建的 Insight
        session.query(Insight).filter(
            Insight.user_id == test_user.id
        ).delete()

        session.commit()

    # 清理 RawMemoryItem (如果需要)
    # 注意：RawMemoryItem 可能被其他测试使用，所以谨慎清理
    raw_manager = RawMemoryManager()
    # raw_manager 的清理逻辑可以在这里添加
