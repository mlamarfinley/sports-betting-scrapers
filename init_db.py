"""Initialize database tables"""
import os
from src.database.connection import engine
from src.database.models import Base

def init_database():
    """Create all tables in the database"""
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("✓ All tables created successfully!")
    
    # List all tables
    from sqlalchemy import inspect
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    print(f"\nCreated {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  - {table}")

if __name__ == "__main__":
    init_database()
