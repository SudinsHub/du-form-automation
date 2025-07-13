#!/usr/bin/env python3
"""
Debug script to check table creation
Run this separately to debug the issue
"""

from database import engine, Base
from sqlalchemy import inspect
import models  # This should import all models

def debug_tables():
    print("=== TABLE CREATION DEBUG ===")
    
    # Check what tables are registered with Base
    print("\n1. Tables registered with Base.metadata:")
    for table_name in Base.metadata.tables.keys():
        print(f"   - {table_name}")
    
    # Check what models are in the models module
    print("\n2. Models found in models module:")
    import inspect as py_inspect
    for name, obj in py_inspect.getmembers(models):
        if py_inspect.isclass(obj) and hasattr(obj, '__tablename__'):
            print(f"   - {name} -> {obj.__tablename__}")
    
    # Check database before creation
    print("\n3. Tables in database BEFORE creation:")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"   {existing_tables}")
    
    # Try to create tables
    print("\n4. Creating tables...")
    try:
        Base.metadata.create_all(bind=engine)
        print("   ✓ Tables created successfully!")
    except Exception as e:
        print(f"   ✗ Error creating tables: {e}")
        return
    
    # Check database after creation
    print("\n5. Tables in database AFTER creation:")
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    print(f"   {existing_tables}")
    
    # Check if specific table exists
    if 'question_preparations' in existing_tables:
        print("\n6. ✓ question_preparations table exists!")
    else:
        print("\n6. ✗ question_preparations table NOT found!")
        print("   This indicates the model is not properly registered.")
    
    print("\n=== DEBUG COMPLETE ===")

if __name__ == "__main__":
    debug_tables()