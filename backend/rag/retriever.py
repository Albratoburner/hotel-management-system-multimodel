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
    llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=api_key, temperature=0)

    # Create Prompt
    prompt = ChatPromptTemplate.from_template(
        "You are an AI assistant for a hotel management system. "
        "Use the following pieces of retrieved context to answer the user's question. "
        "If you don't know the answer, just say that you don't know.\n\n"
        "Context: {context}\n\n"
        "Question: {input}"
    )

    def format_docs(docs):
        return "\\n\\n".join(doc.page_content for doc in docs)

    # Create Chain
    rag_chain = (
        {"context": retriever | format_docs, "input": RunnablePassthrough()}
        | prompt
        | llm
    )
    
    return rag_chain

def answer_policy_query(query: str) -> str:
    try:
        chain = get_rag_chain()
        response = chain.invoke(query)
        return response.content
    except Exception as e:
        return f"Error processing query: {str(e)}"
