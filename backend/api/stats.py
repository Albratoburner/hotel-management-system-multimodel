from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.db import get_db
from backend.db.models import Booking, Room, Employee, Bonus
from sqlalchemy import func

router = APIRouter(prefix="/stats", tags=["Stats"])

@router.get("/dashboard")
def get_dashboard_stats(db: Session = Depends(get_db)):
    # Calculate key metrics
    total_bookings = db.query(Booking).count()
    active_bookings = db.query(Booking).filter(Booking.status.in_(["Checked-in", "Confirmed"])).count()
    
    total_rooms = db.query(Room).count()
    available_rooms = db.query(Room).filter(Room.status == "Available").count()
    
    total_employees = db.query(Employee).count()
    
    # Simple graph data: bookings by status
    status_counts = db.query(Booking.status, func.count(Booking.booking_id)).group_by(Booking.status).all()
    booking_chart = [{"name": status, "value": count} for status, count in status_counts]

    # Employee departments
    dept_counts = db.query(Employee.department, func.count(Employee.employee_id)).group_by(Employee.department).all()
    employee_chart = [{"name": dept, "value": count} for dept, count in dept_counts]

    return {
        "metrics": {
            "total_bookings": total_bookings,
            "active_bookings": active_bookings,
            "total_rooms": total_rooms,
            "available_rooms": available_rooms,
            "occupancy_rate": f"{((total_rooms - available_rooms) / total_rooms * 100):.1f}%" if total_rooms else "0%",
            "total_employees": total_employees
        },
        "charts": {
            "bookings_by_status": booking_chart,
            "employees_by_dept": employee_chart
        }
    }

from backend.api.auth import get_current_user
from backend.db.models import Refund

@router.get("/bookings")
def get_bookings(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    bookings = db.query(Booking).all()
    return bookings

@router.get("/employees")
def get_employees(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        return []
    employees = db.query(Employee).all()
    return employees

@router.get("/refunds")
def get_refunds(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    if current_user.get("role") != "hr":
        return []
    refunds = db.query(Refund).all()
    return refunds
