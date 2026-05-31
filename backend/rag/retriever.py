import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

load_dotenv()

DB_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../vectorstore/chroma_db'))

def get_rag_chain():
    # Load ChromaDB
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vectorstore = Chroma(persist_directory=DB_DIR, embedding_function=embeddings)
    retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

    # Load LLM
    llm = ChatGroq(model="llama3-70b-8192", temperature=0)

    # Create Prompt
    system_prompt = (
        "You are an AI assistant for a hotel management system. "
        "Use the following pieces of retrieved context to answer the user's question. "
        "If you don't know the answer, just say that you don't know. "
        "Context: {context}"
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "{input}"),
    ])

    # Create Chain
    question_answer_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, question_answer_chain)
    
    return rag_chain

def answer_policy_query(query: str) -> str:
    try:
        chain = get_rag_chain()
        response = chain.invoke({"input": query})
        return response["answer"]
    except Exception as e:
        return f"Error processing query: {str(e)}"
