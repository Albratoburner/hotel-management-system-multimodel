from sqlalchemy import Column, String, Integer, Float, Date
from backend.db.db import Base

class Room(Base):
    __tablename__ = "rooms"

    room_id = Column(String, primary_key=True, index=True)
    room_number = Column(Integer, unique=True, index=True)
    room_type = Column(String)
    price_per_night = Column(Float)
    status = Column(String)  # Available, Booked, Maintenance

class Booking(Base):
    __tablename__ = "bookings"

    booking_id = Column(String, primary_key=True, index=True)
    guest_id = Column(String)
    guest_name = Column(String)
    room_number = Column(Integer)
    check_in_date = Column(String) # Storing as YYYY-MM-DD string for simplicity with SQLite
    check_out_date = Column(String)
    status = Column(String) # Completed, Checked-in, Confirmed, Cancelled

class Guest(Base):
    __tablename__ = "guests"

    guest_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    phone = Column(String)
    email = Column(String)
    nationality = Column(String)

class Employee(Base):
    __tablename__ = "employees"

    employee_id = Column(String, primary_key=True, index=True)
    name = Column(String)
    role = Column(String)
    department = Column(String)
    salary = Column(Float)
    status = Column(String) # Active, Inactive

class Bonus(Base):
    __tablename__ = "bonuses"

    bonus_id = Column(String, primary_key=True, index=True)
    employee_id = Column(String)
    amount = Column(Float)
    reason = Column(String)
    date = Column(String) # YYYY-MM-DD string

class Refund(Base):
    __tablename__ = "refunds"

    refund_id = Column(String, primary_key=True, index=True)
    booking_id = Column(String)
    amount = Column(Float)
    reason = Column(String)
    date = Column(String)

class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_email = Column(String)
    role = Column(String)
    query = Column(String)
    response = Column(String)
    timestamp = Column(String)
