import sys
import os

# Add the parent directory to sys.path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.db import engine, Base
from backend.db.models import Room, Booking, Guest, Employee, Bonus

def init_db():
    print("Initializing Database...")
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully!")

if __name__ == "__main__":
    init_db()
