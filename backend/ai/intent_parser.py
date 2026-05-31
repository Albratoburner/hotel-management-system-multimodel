import json
from pydantic import BaseModel, Field
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class Intent(BaseModel):
    action: str = Field(description="The action to perform: CREATE_BOOKING, CANCEL_BOOKING, ISSUE_BONUS, UPDATE_SALARY, ISSUE_REFUND")
    guest_name: Optional[str] = Field(None, description="Name of the guest")
    room_type: Optional[str] = Field(None, description="Type of room (e.g., Standard, Deluxe, Suite)")
    check_in_date: Optional[str] = Field(None, description="Check-in date YYYY-MM-DD")
    check_out_date: Optional[str] = Field(None, description="Check-out date YYYY-MM-DD")
    booking_id: Optional[str] = Field(None, description="Booking ID to cancel")
    employee_name: Optional[str] = Field(None, description="Name of the employee")
    amount: Optional[float] = Field(None, description="Bonus amount or new salary amount")
    reason: Optional[str] = Field(None, description="Reason for the bonus")

def parse_intent(query: str, user_role: str = "staff") -> dict:
    api_key = os.environ.get("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0).with_structured_output(Intent)
    
    prompt = PromptTemplate.from_template(
        "You are an AI assistant for a hotel management system.\n"
        "The user's role is: {user_role}\n"
        "Extract the intent from the following user request.\n"
        "IMPORTANT RULES based on role:\n"
        "- If user_role is 'staff', they CANNOT issue bonuses, update salaries, or issue refunds. If they try, do NOT extract the intent. Instead, return an Intent with action='UNKNOWN' or something invalid (which will cause a failure later), but ideally just extract what they said if it maps, the backend will block it. Actually, better yet, just extract the intent normally. The backend will block it.\n"
        "If dates are mentioned without a year, assume it is for the current year (2026).\n"
        "User request: {query}"
    )
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({"query": query, "user_role": user_role})
        return result.model_dump(exclude_none=True)
    except Exception as e:
        return {"error": str(e)}
