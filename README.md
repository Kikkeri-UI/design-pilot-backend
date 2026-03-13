Title: AI Design Pilot — Backend Engine (FastAPI)
Description:
A high-performance Python backend built with FastAPI that powers the AI Design Pilot. It handles design data processing, manages LLM orchestrations (GPT-4), and serves heuristic-based UX critiques.

Key Technical Features:

Async Processing: Leverages FastAPI’s asynchronous capabilities for non-blocking AI model calls.

LLM Orchestration: Integrated with OpenAI (GPT-4 Vision/Text) to perform automated design audits.

Pydantic Schema Validation: Strict type-checking and data validation for incoming design prompts and outgoing critiques.

Modular Architecture: Designed with clear separation of concerns (Routes, Services, and AI Prompts).

Key Endpoints:

POST /critique: Accepts design data and returns a structured JSON critique based on UX heuristics.

Installation & Setup:

Bash
# Create a virtual environment
python -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Start the server
uvicorn main:app --reload
