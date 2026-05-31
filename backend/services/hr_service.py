from sqlalchemy.orm import Session
from typing import List, Optional
from backend.db.models import Employee, Bonus
import uuid
import datetime

def get_employees(db: Session, department: Optional[str] = None) -> List[Employee]:
    query = db.query(Employee)
    if department:
        query = query.filter(Employee.department == department)
    return query.all()

def get_employee_by_name(db: Session, name: str) -> Optional[Employee]:
    return db.query(Employee).filter(Employee.name.ilike(f"%{name}%")).first()

def issue_bonus(db: Session, employee_name: str, amount: float, reason: str) -> dict:
    # 1. Find the employee
    employee = get_employee_by_name(db, employee_name)
    if not employee:
        return {"error": f"Employee '{employee_name}' not found."}
    
    if employee.status != "Active":
        return {"error": f"Cannot issue bonus. Employee '{employee_name}' is inactive."}

    # 2. Issue the bonus
    bonus_id = f"BN{str(uuid.uuid4())[:5].upper()}"
    today_date = datetime.date.today().strftime("%Y-%m-%d")
    
    bonus = Bonus(
        bonus_id=bonus_id,
        employee_id=employee.employee_id,
        amount=amount,
        reason=reason,
        date=today_date
    )
    
    db.add(bonus)
    db.commit()
    db.refresh(bonus)
    
    return {
        "message": "Bonus issued successfully", 
        "bonus_id": bonus.bonus_id, 
        "employee_name": employee.name, 
        "amount": amount
    }

def update_employee_salary(db: Session, employee_name: str, new_salary: float) -> dict:
    employee = get_employee_by_name(db, employee_name)
    if not employee:
        return {"error": f"Employee '{employee_name}' not found."}
    
    employee.salary = new_salary
    db.commit()
    
    return {"message": f"Salary for {employee_name} updated to {new_salary}"}
