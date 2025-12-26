from database import SessionLocal, Base, engine
from models import User
from auth import get_password_hash

# Create tables
Base.metadata.create_all(bind=engine)

db = SessionLocal()
admin = User(username="superadmin", hashed_password=get_password_hash("password123"), is_super_admin=True)
db.add(admin)
db.commit()
db.close()
print("Super admin user created: username=superadmin, password=password123")