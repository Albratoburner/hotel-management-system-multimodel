# Multi-AI Hotel Management System

A state-of-the-art, AI-powered hotel management control center that leverages a multi-model architecture to intelligently automate operations. The system features a fully authenticated, role-based frontend, a powerful CRUD AI intent parser, and an optimized Retrieval-Augmented Generation (RAG) engine for natural language policy inquiries.

## 🚀 Key Features

### 1. Role-Based Access Control (RBAC)
- **Strict Authorization**: Operations are strictly segregated based on user roles (`hr` vs `staff`). 
- **HR Capabilities**: Can manage sensitive data, issue employee bonuses, update salaries, and authorize booking refunds.
- **Staff Capabilities**: Can manage room bookings and cancellations, but are strictly blocked by the backend and AI prompts from performing HR or financial refund tasks.
- **Dynamic UI**: The dashboard intelligently adapts to the logged-in user, hiding sensitive HR statistics and data tables from standard staff.

### 2. Multi-Model AI Engine Architecture (LangChain + Groq)
To eliminate hallucination loops while maintaining high reasoning capabilities, this project uses a specialized multi-model architecture via Groq:
- **Natural Language CRUD (Llama-3.3-70b-versatile)**: Users can type commands like *"Issue a $500 bonus to John"* or *"Cancel booking B12345"*. The system uses the 70B Llama model to parse the intent, extract relevant entities, and ask for any missing fields.
- **Human-in-the-Loop Approval**: Before executing any destructive or financial operation, the AI presents a clear "Approve / Reject" prompt to the user.
- **RAG Policy Engine (Qwen 3 32B)**: Ask questions like *"What is our refund policy?"*. The system uses **ChromaDB** and HuggingFace embeddings (`all-MiniLM-L6-v2`) to retrieve exact policy text from ingested PDF documents. The **Qwen** model is used specifically for RAG generation because it avoids the bulleted-list repetition bugs present in Llama inference implementations. It strips out internal `<think>` tags and delivers a clean, concise response.

### 3. Premium Frontend (Vite + React)
- **Glassmorphism Design**: A stunning, modern dark-mode aesthetic with vibrant color gradients and micro-animations (via Framer Motion).
- **Persistent Chat History**: All AI interactions are logged to the database. When you log in, your previous conversations seamlessly load into the chat window. Includes a "New Chat" button to clear the session database logs instantly.
- **Live Data Tables**: Interactive HTML data tables for Bookings, Employees, and Refunds, natively rendered alongside top-level metrics like Occupancy Rate and Active Bookings.

## 🧠 RAG implementation & Chunking Strategy

- **Document Ingestion**: Internal PDFs (policies, HR rules, FAQs) are parsed using `PyPDFLoader`.
- **Chunking Profile**: To make the small internal documents highly "RAGable" without fracturing context, we use a `RecursiveCharacterTextSplitter` with an optimized `chunk_size` of `2000` characters and a `chunk_overlap` of `200`. This ensures that when the AI searches for an answer, it pulls down cohesive, uninterrupted blocks of text.
- **Hybrid Context Injection**: The RAG pipeline separates semantic vector searches (which only use the raw user query) from dynamic context injection (like live DB room rates). System Prompts are strictly separated from Human Messages, and real-time database lookups are appended to the static vector search results.

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, Uvicorn (managed by `uv`)
- **AI & RAG**: LangChain, ChromaDB, Groq API (Llama 3 & Qwen 3)
- **Frontend**: React, Vite, TypeScript, Framer Motion, Lucide React

## 📦 How to Run

### 1. Start the Backend
Navigate to the root directory and run the FastAPI server using `uv`:
```bash
uv run uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```
*(Ensure that your `.env` file contains your `GROQ_API_KEY`)*

### 2. Start the Frontend
In a new terminal, navigate to the `frontend` directory and start the Vite development server:
```bash
cd frontend
npm install
npm run dev
```

### 3. Login Credentials
Access the application at `http://localhost:5173/` (or the port Vite provides) and use the following test accounts:
- **HR Access**: `hr@gmail.com` / `admin`
- **Staff Access**: `staff@gmail.com` / `admin`