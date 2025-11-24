from contextlib import contextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mirix.config import MirixConfig
import os

_SessionLocal = None

def get_session_factory():
    global _SessionLocal
    if _SessionLocal is None:
        config = MirixConfig.load()
        sqlite_db_path = os.path.join(config.recall_storage_path, "sqlite.db")
        engine = create_engine(f"sqlite:///{sqlite_db_path}")
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return _SessionLocal

@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    Session = get_session_factory()
    session = Session()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()
