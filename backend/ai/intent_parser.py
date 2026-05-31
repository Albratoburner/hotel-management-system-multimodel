import json
from pydantic import BaseModel, Field
from typing import Optional
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class Intent(BaseModel):
    action: str = Field(description="The action to perform: CREATE_BOOKING, CANCEL_BOOKING, ISSUE_BONUS, UPDATE_SALARY")
    guest_name: Optional[str] = Field(None, description="Name of the guest")
    room_type: Optional[str] = Field(None, description="Type of room (e.g., Standard, Deluxe, Suite)")
    check_in_date: Optional[str] = Field(None, description="Check-in date YYYY-MM-DD")
    check_out_date: Optional[str] = Field(None, description="Check-out date YYYY-MM-DD")
    booking_id: Optional[str] = Field(None, description="Booking ID to cancel")
    employee_name: Optional[str] = Field(None, description="Name of the employee")
    amount: Optional[float] = Field(None, description="Bonus amount or new salary amount")
    reason: Optional[str] = Field(None, description="Reason for the bonus")

def parse_intent(query: str) -> dict:
    llm = ChatGroq(model="llama3-70b-8192", temperature=0).with_structured_output(Intent)
    
    prompt = PromptTemplate.from_template(
        "Extract the intent from the following user request.\n"
        "If dates are mentioned without a year, assume it is for the current year (2026). "
        "User request: {query}"
    )
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({"query": query})
        return result.model_dump(exclude_none=True)
    except Exception as e:
        return {"error": str(e)}
