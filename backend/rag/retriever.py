import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from dotenv import load_dotenv

load_dotenv()

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vectorstore/chroma_db'))

def get_rag_chain():
    # Load ChromaDB
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Load LLM
    api_key = os.environ.get("GROQ_API_KEY")
    llm = ChatGroq(model="qwen/qwen3-32b", api_key=api_key, temperature=0.1)

    # Create Prompt (using proper system and human messages to prevent Llama 3 from hallucinating text completions)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an AI assistant for a hotel management system.\nUse the following pieces of retrieved context to answer the user's question.\nIf you don't know the answer, just say that you don't know.\nCRITICAL: Keep your answer extremely concise. DO NOT repeat the same phrase or sentence multiple times. Stop immediately once you have answered the question.\n\nContext:\n{context}"),
        ("human", "{input}")
    ])

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    # Create Chain
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
    )
    
    return rag_chain

def answer_policy_query(query: str) -> str:
    try:
        # 1. Fetch current room rates from DB to provide additional context
        from backend.db.db import SessionLocal
        from backend.db.models import Room
        db = SessionLocal()
        rooms = db.query(Room).all()
        db.close()
        
        rates_context = "Current Room Rates:\n"
        for r in rooms:
            rates_context += f"- {r.room_type}: ${r.price_per_night} per night\n"
            
        # 2. Retrieve documents using ONLY the raw query (to avoid semantic search confusion)
        chain = get_rag_chain()
        
        # We need to manually perform the retrieval and then call the chain, or modify the chain logic.
        # Actually, if we just inject the rates into the query string, we still corrupt semantic search.
        # Let's bypass the rag_chain's internal retriever step by calling retriever directly:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        from langchain_chroma import Chroma
        import os
        
        DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vectorstore/chroma_db'))
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
        retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
        
        # Get docs based on raw user query
        docs = retriever.invoke(query)
        doc_context = "\n\n".join(doc.page_content for doc in docs)
        
        # 3. Combine retrieved docs with our dynamic DB data
        combined_context = f"{rates_context}\n\nRetrieved Knowledge:\n{doc_context}"
        
        # 4. Prompt the LLM directly
        from langchain_groq import ChatGroq
        from langchain_core.prompts import ChatPromptTemplate
        
        api_key = os.environ.get("GROQ_API_KEY")
        llm = ChatGroq(model="qwen/qwen3-32b", api_key=api_key, temperature=0.1)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant for a hotel management system.\nUse the following pieces of retrieved context to answer the user's question.\nIf you don't know the answer, just say that you don't know.\nCRITICAL: Keep your answer extremely concise. DO NOT repeat the same phrase or sentence multiple times. Stop immediately once you have answered the question.\n\nContext:\n{context}"),
            ("human", "{input}")
        ])
        
        final_chain = prompt | llm
        response = final_chain.invoke({"context": combined_context, "input": query})
        import re
        content = response.content
        content = re.sub(r'<think>.*?</think>', '', content, flags=re.DOTALL).strip()
        
        return content
    except Exception as e:
        return f"Error processing query: {str(e)}"
