
import os
from dotenv import load_dotenv # Needed to load API keys
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware # Crucial for frontend communication

# --- Import your routers here ---
# Assuming text_review.py contains 'router = APIRouter()'
from routes.text_review import router as text_review_router
# Assuming figma_review.py contains 'router = APIRouter()'
from routes.figma_review import router as figma_review_router


# Load environment variables from .env file
# This MUST be called BEFORE you try to access any env vars with os.getenv()
load_dotenv()

app = FastAPI()

# --- CORS Configuration ---
# This allows your Next.js frontend (e.g., on localhost:3000) to make requests to this backend
origins = [
    "http://localhost:3000", # Your Next.js development server URL
    # IMPORTANT: Add your production frontend URL(s) here when you deploy!
    # e.g., "https://www.your-design-pilot-app.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all standard methods like POST, GET, OPTIONS
    allow_headers=["*"], # Allows all standard headers like Content-Type
)

# --- Include your routers in the main application ---
# This tells your FastAPI app to recognize the endpoints defined in these routers
app.include_router(text_review_router)
app.include_router(figma_review_router)
