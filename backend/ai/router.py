from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
import os
from dotenv import load_dotenv

load_dotenv()

class Route(BaseModel):
    destination: str = Field(description="The destination for the query. Either 'CRUD' for operations like booking or bonuses, or 'RAG' for questions about policies, FAQs, or rules.")

def route_query(query: str) -> str:
    llm = ChatGroq(model="llama3-70b-8192", temperature=0).with_structured_output(Route)
    
    prompt = PromptTemplate.from_template(
        "You are an intelligent router for a hotel management system.\n"
        "Determine where to send the user query.\n"
        "- If it involves creating, updating, or deleting records (e.g., booking a room, giving a bonus), route to 'CRUD'.\n"
        "- If it is a question about rules, policies, or general knowledge (e.g., cancellation policy, HR rules), route to 'RAG'.\n"
        "Query: {query}"
    )
    
    chain = prompt | llm
    
    try:
        result = chain.invoke({"query": query})
        return result.destination
    except Exception:
        return "RAG" # Default fallback
