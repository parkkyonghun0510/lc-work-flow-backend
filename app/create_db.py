from .database import Base, engine
from .models import user, branch, department, customer # Import all models to register them with Base.metadata

def create_db_tables():
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully.")

if __name__ == "__main__":
    create_db_tables()