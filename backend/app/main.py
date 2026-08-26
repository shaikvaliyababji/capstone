from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.database.init_db import init_db
from app.api.routes.devices import router as devices_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize and seed database on startup
    init_db()
    print("Database Initialized and Seeded.")
    yield
    # Cleanup on shutdown (if any)
    print("Application shutdown complete.")


from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Smart Home Backend",
    description="Backend API for capstone project: AI-SmartHome.",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware configuration
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(devices_router)


@app.get("/")
def root():
    return {
        "message": "AI Smart Home Running"
    }