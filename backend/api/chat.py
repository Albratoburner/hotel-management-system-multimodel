from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from backend.db.db import get_db
from backend.api.auth import get_current_user
from backend.ai.router import route_query
from backend.ai.intent_parser import parse_intent
from backend.ai.approval import generate_approval_request
from backend.rag.retriever import answer_policy_query
from backend.services.booking_service import create_booking, cancel_booking, issue_refund
from backend.services.hr_service import issue_bonus, update_employee_salary
from backend.db.models import ChatLog
import datetime

def log_chat(db: Session, email: str, role: str, query: str, response: str):
    log = ChatLog(
        user_email=email,
        role=role,
        query=query,
        response=response,
        timestamp=datetime.datetime.utcnow().isoformat()
    )
    db.add(log)
    db.commit()

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatRequest(BaseModel):
    message: str

class ApprovalAction(BaseModel):
    intent_data: dict
    approved: bool

@router.get("/history")
def get_chat_history(db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    logs = db.query(ChatLog).filter(ChatLog.user_email == current_user.get("email")).order_by(ChatLog.id.asc()).all()
    return [{"query": log.query, "response": log.response, "timestamp": log.timestamp} for log in logs]

@router.post("/")
def chat_endpoint(req: ChatRequest, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_role = current_user.get("role", "staff")
    user_email = current_user.get("email", "unknown")
    
    # 1. Route the query (pass role to router)
    destination = route_query(req.message, user_role)
    
    if destination == "RAG":
        # Handle via knowledge base
        answer = answer_policy_query(req.message)
        log_chat(db, user_email, user_role, req.message, answer)
        return {"status": "SUCCESS", "type": "RAG", "message": answer}
    
    elif destination == "CRUD":
        # Parse intent (pass role to parser)
        intent_data = parse_intent(req.message, user_role)
        if "error" in intent_data:
            return {"status": "ERROR", "message": f"Failed to parse intent: {intent_data['error']}"}
        
        # Validate required fields
        act = intent_data.get("action")
        missing_fields = []
        
        if act == "CREATE_BOOKING":
            if not intent_data.get("guest_name"): missing_fields.append("guest name")
            if not intent_data.get("room_type"): missing_fields.append("room type")
            if not intent_data.get("check_in_date"): missing_fields.append("check-in date")
            if not intent_data.get("check_out_date"): missing_fields.append("check-out date")
        elif act in ["CANCEL_BOOKING", "ISSUE_REFUND"]:
            if not intent_data.get("booking_id"): missing_fields.append("booking ID")
        elif act in ["ISSUE_BONUS", "UPDATE_SALARY"]:
            if not intent_data.get("employee_name"): missing_fields.append("employee name")
            if not intent_data.get("amount"): missing_fields.append("amount")
            
        if missing_fields:
            ans = f"Please provide the following missing information: {', '.join(missing_fields)}"
            log_chat(db, user_email, user_role, req.message, ans)
            return {"status": "SUCCESS", "type": "CRUD_MISSING", "message": ans}
            
        # Immediate RBAC Enforcement before showing Approval UI
        if act in ["ISSUE_BONUS", "UPDATE_SALARY", "ISSUE_REFUND"] and user_role != "hr":
            ans = f"I'm sorry, but as a {user_role}, you do not have permission to perform '{act}'. This action is restricted to HR."
            log_chat(db, user_email, user_role, req.message, ans)
            return {"status": "SUCCESS", "type": "CRUD_DENIED", "message": ans}
            
        # Generate approval request
        approval_req = generate_approval_request(intent_data)
        log_chat(db, user_email, user_role, req.message, f"[Awaiting Approval for {act}]")
        return approval_req

@router.post("/execute")
def execute_action(action: ApprovalAction, db: Session = Depends(get_db), current_user: dict = Depends(get_current_user)):
    user_email = current_user.get("email", "unknown")
    user_role = current_user.get("role", "staff")

    if not action.approved:
        ans = "Action cancelled by user."
        log_chat(db, user_email, user_role, f"[Action: {action.intent_data.get('action')}]", ans)
        return {"status": "CANCELLED", "message": ans}
        
    intent = action.intent_data
    act = intent.get("action")
    
    # RBAC Enforcement
    if act in ["ISSUE_BONUS", "UPDATE_SALARY", "ISSUE_REFUND"] and user_role != "hr":
        return {"status": "ERROR", "message": "Forbidden: You do not have permission to perform HR or Refund tasks."}
    
    if act == "CREATE_BOOKING":
        res = create_booking(db, intent.get("guest_name"), intent.get("room_type"), intent.get("check_in_date"), intent.get("check_out_date"))
        log_chat(db, user_email, user_role, f"[Execute CREATE_BOOKING]", str(res))
        return res
    elif act == "CANCEL_BOOKING":
        res = cancel_booking(db, intent.get("booking_id"))
        log_chat(db, user_email, user_role, f"[Execute CANCEL_BOOKING]", str(res))
        return res
    elif act == "ISSUE_BONUS":
        res = issue_bonus(db, intent.get("employee_name"), intent.get("amount"), intent.get("reason"))
        log_chat(db, user_email, user_role, f"[Execute ISSUE_BONUS]", str(res))
        return res
    elif act == "UPDATE_SALARY":
        res = update_employee_salary(db, intent.get("employee_name"), intent.get("amount"))
        log_chat(db, user_email, user_role, f"[Execute UPDATE_SALARY]", str(res))
        return res
    elif act == "ISSUE_REFUND":
        res = issue_refund(db, intent.get("booking_id"), intent.get("amount"), intent.get("reason") or "Refund issued")
        log_chat(db, user_email, user_role, f"[Execute ISSUE_REFUND]", str(res))
        return res
    
    return {"error": "Unknown action type"}
