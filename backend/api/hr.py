from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.db.db import get_db
from backend.services.hr_service import get_employees, issue_bonus, update_employee_salary
from pydantic import BaseModel

router = APIRouter(prefix="/hr", tags=["HR"])

class BonusRequest(BaseModel):
    employee_name: str
    amount: float
    reason: str

class SalaryRequest(BaseModel):
    employee_name: str
    amount: float

@router.get("/employees")
def list_employees(db: Session = Depends(get_db)):
    return get_employees(db)

@router.post("/bonus")
def give_bonus(req: BonusRequest, db: Session = Depends(get_db)):
    return issue_bonus(db, req.employee_name, req.amount, req.reason)

@router.post("/salary")
def update_salary(req: SalaryRequest, db: Session = Depends(get_db)):
    return update_employee_salary(db, req.employee_name, req.amount)
