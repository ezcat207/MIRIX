import os
from sqlalchemy import create_engine
from mirix.config import MirixConfig
from mirix.orm.base import Base
# Import all models to ensure they are registered
from mirix.orm import * 

def init_db():
    config = MirixConfig.load()
    sqlite_db_path = os.path.join(config.recall_storage_path, "sqlite.db")
    print(f"Initializing database at {sqlite_db_path}")
    
    engine = create_engine(f"sqlite:///{sqlite_db_path}")
    Base.metadata.create_all(bind=engine)
    print("Tables initialized.")

if __name__ == "__main__":
    init_db()
