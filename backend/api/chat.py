from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.db.db import get_db
from backend.ai.router import route_query
from backend.ai.intent_parser import parse_intent
from backend.ai.approval import generate_approval_request
from backend.rag.retriever import answer_policy_query
from backend.services.booking_service import create_booking, cancel_booking
from backend.services.hr_service import issue_bonus, update_employee_salary

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

class ApprovalAction(BaseModel):
    intent_data: dict
    approved: bool

@router.post("/")
def chat_endpoint(req: ChatRequest):
    # 1. Route the query
    destination = route_query(req.message)
    
    if destination == "RAG":
        # Handle via knowledge base
        answer = answer_policy_query(req.message)
        return {"status": "SUCCESS", "type": "RAG", "message": answer}
    
    elif destination == "CRUD":
        # Parse intent
        intent_data = parse_intent(req.message)
        if "error" in intent_data:
            return {"status": "ERROR", "message": f"Failed to parse intent: {intent_data['error']}"}
        
        # Generate approval request
        approval_req = generate_approval_request(intent_data)
        return approval_req

@router.post("/execute")
def execute_action(action: ApprovalAction, db: Session = Depends(get_db)):
    if not action.approved:
        return {"status": "CANCELLED", "message": "Action cancelled by user."}
        
    intent = action.intent_data
    act = intent.get("action")
    
    if act == "CREATE_BOOKING":
        res = create_booking(db, intent.get("guest_name"), intent.get("room_type"), intent.get("check_in_date"), intent.get("check_out_date"))
        return res
    elif act == "CANCEL_BOOKING":
        res = cancel_booking(db, intent.get("booking_id"))
        return res
    elif act == "ISSUE_BONUS":
        res = issue_bonus(db, intent.get("employee_name"), intent.get("amount"), intent.get("reason"))
        return res
    elif act == "UPDATE_SALARY":
        res = update_employee_salary(db, intent.get("employee_name"), intent.get("amount"))
        return res
    
    return {"error": "Unknown action type"}
