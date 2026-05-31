from sqlalchemy.orm import Session
from typing import List, Optional
from backend.db.models import Booking, Room, Guest
import uuid

def get_rooms(db: Session, status: Optional[str] = None) -> List[Room]:
    query = db.query(Room)
    if status:
        query = query.filter(Room.status == status)
    return query.all()

def create_booking(db: Session, guest_name: str, room_type: str, check_in_date: str, check_out_date: str) -> dict:
    # 1. Find an available room of the requested type
    room = db.query(Room).filter(Room.room_type == room_type, Room.status == "Available").first()
    if not room:
        return {"error": f"No available rooms of type {room_type}"}

    # 2. Check if guest exists by name (simplified for demo), otherwise create
    guest = db.query(Guest).filter(Guest.name == guest_name).first()
    if not guest:
        guest_id = f"G{str(uuid.uuid4())[:6].upper()}"
        guest = Guest(
            guest_id=guest_id, 
            name=guest_name, 
            phone="Unknown", 
            email="Unknown", 
            nationality="Unknown"
        )
        db.add(guest)
        db.commit()
        db.refresh(guest)

    # 3. Create booking
    booking_id = f"B{str(uuid.uuid4())[:6].upper()}"
    booking = Booking(
        booking_id=booking_id,
        guest_id=guest.guest_id,
        guest_name=guest.name,
        room_number=room.room_number,
        check_in_date=check_in_date,
        check_out_date=check_out_date,
        status="Confirmed"
    )
    
    # Update room status
    room.status = "Booked"

    db.add(booking)
    db.commit()
    db.refresh(booking)
    
    return {"message": "Booking created successfully", "booking_id": booking.booking_id, "room_number": room.room_number}

def cancel_booking(db: Session, booking_id: str) -> dict:
    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        return {"error": f"Booking {booking_id} not found"}
    
    booking.status = "Cancelled"
    
    # Free up the room
    room = db.query(Room).filter(Room.room_number == booking.room_number).first()
    if room:
        room.status = "Available"
        
    db.commit()
    return {"message": f"Booking {booking_id} cancelled successfully"}

def issue_refund(db: Session, booking_id: str, amount: float, reason: str) -> dict:
    from backend.db.models import Refund
    import datetime
    import uuid

    booking = db.query(Booking).filter(Booking.booking_id == booking_id).first()
    if not booking:
        return {"error": f"Booking {booking_id} not found."}

    if booking.status != "Cancelled":
        return {"error": f"Refund not acceptable. Booking {booking_id} must be 'Cancelled' first."}

    refund_id = f"REF{str(uuid.uuid4())[:5].upper()}"
    today_date = datetime.date.today().strftime("%Y-%m-%d")

    refund = Refund(
        refund_id=refund_id,
        booking_id=booking_id,
        amount=amount,
        reason=reason,
        date=today_date
    )

    db.add(refund)
    db.commit()
    db.refresh(refund)

    return {"message": f"Refund of {amount} issued successfully for booking {booking_id}"}
