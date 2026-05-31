import sys
import os
import pandas as pd

# Add the parent directory to sys.path so we can import backend modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.db.db import engine

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../backend/data/db_data'))

def seed_db():
    print("Seeding database with CSV data...")
    try:
        # Load CSVs
        rooms_df = pd.read_csv(os.path.join(DATA_DIR, 'rooms.csv'))
        bookings_df = pd.read_csv(os.path.join(DATA_DIR, 'bookings.csv'))
        guests_df = pd.read_csv(os.path.join(DATA_DIR, 'guests.csv'))
        employees_df = pd.read_csv(os.path.join(DATA_DIR, 'employees.csv'))
        bonuses_df = pd.read_csv(os.path.join(DATA_DIR, 'bonuses.csv'))

        # Insert into DB
        rooms_df.to_sql('rooms', engine, if_exists='replace', index=False)
        print("Loaded rooms.csv into 'rooms' table.")

        bookings_df.to_sql('bookings', engine, if_exists='replace', index=False)
        print("Loaded bookings.csv into 'bookings' table.")

        guests_df.to_sql('guests', engine, if_exists='replace', index=False)
        print("Loaded guests.csv into 'guests' table.")

        employees_df.to_sql('employees', engine, if_exists='replace', index=False)
        print("Loaded employees.csv into 'employees' table.")

        bonuses_df.to_sql('bonuses', engine, if_exists='replace', index=False)
        print("Loaded bonuses.csv into 'bonuses' table.")

        print("Seeding completed successfully!")
    except Exception as e:
        print(f"Error seeding database: {e}")

if __name__ == "__main__":
    seed_db()
