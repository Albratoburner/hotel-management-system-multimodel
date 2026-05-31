from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class Route(BaseModel):
    destination: str = Field(description="The destination for the query. Either 'CRUD' for operations like booking or bonuses, or 'RAG' for questions about policies, FAQs, or rules.")

def route_query(query: str, user_role: str = "staff") -> str:
    api_key = os.environ.get("GROQ_API_KEY")
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0).with_structured_output(Route)
    
    prompt = PromptTemplate.from_template(
        "You are an intelligent router for a hotel management system.\n"
        "Determine where to send the user query.\n"
        "The user's role is: {user_role}\n"
        "- If it involves creating, updating, or deleting records (e.g., booking a room, giving a bonus), route to 'CRUD'.\n"
        "  (Note: Staff cannot issue bonuses, but if they ask, still route to CRUD so the system can reject it formally.)\n"
        "- If it is a question about rules, policies, or general knowledge (e.g., room rates, refund policy, cancellation policy, HR rules, bonus policies), route to 'RAG'.\n"
        "Query: {query}"
    )
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({"query": query, "user_role": user_role})
        return result.destination
    except Exception:
        return "RAG" # Default fallback
