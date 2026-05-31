from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.db import get_db
from backend.services.booking_service import get_rooms, create_booking, cancel_booking
from pydantic import BaseModel

router = APIRouter(prefix="/staff", tags=["Staff"])

class BookingRequest(BaseModel):
    guest_name: str
    room_type: str
    check_in_date: str
    check_out_date: str

class CancelRequest(BaseModel):
    booking_id: str

@router.get("/rooms")
def list_rooms(db: Session = Depends(get_db)):
    return get_rooms(db)

@router.post("/book")
def book_room(req: BookingRequest, db: Session = Depends(get_db)):
    return create_booking(db, req.guest_name, req.room_type, req.check_in_date, req.check_out_date)

@router.post("/cancel")
def cancel(req: CancelRequest, db: Session = Depends(get_db)):
    return cancel_booking(db, req.booking_id)
