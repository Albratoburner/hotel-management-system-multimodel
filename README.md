# Multi-AI Hotel Management System

A state-of-the-art, AI-powered hotel management control center that leverages Large Language Models (LLMs) to intelligently automate operations. The system features a fully authenticated, role-based frontend, a powerful CRUD AI intent parser, and a Retrieval-Augmented Generation (RAG) engine for natural language policy inquiries.

## 🚀 Key Features

### 1. Role-Based Access Control (RBAC)
- **Strict Authorization**: Operations are strictly segregated based on user roles (`hr` vs `staff`). 
- **HR Capabilities**: Can manage sensitive data, issue employee bonuses, update salaries, and authorize booking refunds.
- **Staff Capabilities**: Can manage room bookings and cancellations, but are strictly blocked by the backend and AI prompts from performing HR or financial refund tasks.
- **Dynamic UI**: The dashboard intelligently adapts to the logged-in user, hiding sensitive HR statistics and data tables from standard staff.

### 2. Intelligent AI Engine (LangChain + Groq)
- **Natural Language CRUD**: Users can type commands like *"Issue a $500 bonus to John"* or *"Cancel booking B12345"*. The system uses **Groq (llama-3.3-70b-versatile)** to parse the intent, extract relevant entities, and ask for any missing fields.
- **Human-in-the-Loop Approval**: Before executing any destructive or financial operation, the AI presents a clear "Approve / Reject" prompt to the user.
- **RAG Policy Engine**: Ask questions like *"What is our refund policy?"*. The system uses **ChromaDB** and HuggingFace embeddings (`all-MiniLM-L6-v2`) to retrieve exact policy text from ingested PDF documents. It also injects real-time SQLite database pricing into the context so the AI can accurately quote current room rates alongside static policies.

### 3. Premium Frontend (Vite + React)
- **Glassmorphism Design**: A stunning, modern dark-mode aesthetic with vibrant color gradients and micro-animations (via Framer Motion).
- **Persistent Chat History**: All AI interactions are logged to the database. When you log in, your previous conversations seamlessly load into the chat window.
- **Live Data Tables**: Interactive HTML data tables for Bookings, Employees, and Refunds, natively rendered alongside top-level metrics like Occupancy Rate and Active Bookings.

## 🛠️ Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, SQLite, Uvicorn (managed by `uv`)
- **AI & RAG**: LangChain, ChromaDB, Groq API (LLaMA 3)
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

## 🧠 System Architecture Notes

- **Avoiding Hallucinations**: The RAG pipeline separates semantic vector searches (which only use the raw user query) from dynamic context injection (like live DB room rates). System Prompts are strictly separated from Human Messages to prevent LLaMA 3 continuation hallucinations.
- **Data Ingestion**: If policies change, drop the existing `chroma_db` folder and run `uv run python scripts/03_ingest_docs.py` to re-chunk and index the PDF documents with high-precision chunking parameters.
- **Logging**: All chat events are persisted to the `chat_logs` table, allowing for historical auditing of AI actions.