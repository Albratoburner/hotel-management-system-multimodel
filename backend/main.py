from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import staff, hr, chat, auth, stats
from backend.db.db import engine, Base
import backend.db.models

Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Hotel Management System")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api")
app.include_router(stats.router, prefix="/api")
app.include_router(staff.router, prefix="/api")
app.include_router(hr.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

@app.get("/")
def root():
    return {"message": "Welcome to the AI Hotel Management System API"}
