import os
import sys
import uuid
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel
import logging

# --- Project Root Setup ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import Config
from app.services.bot_service import BotService

# --- Initialize Services ---
Config.initialize_paths(project_root)
Config.validate()
bot_service = BotService(Config)

# --- FastAPI App Setup ---
limiter = Limiter(key_func=get_remote_address, default_limits=["20/minute"])
app = FastAPI(title="Personal AI Assistant API")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

logger = logging.getLogger(__name__)

# --- Pydantic Models (Simplified) ---
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

# --- API Endpoints ---
@app.on_event("startup")
async def startup_event():
    """On server startup, prepare the data."""
    logger.info("Server starting up...")
    bot_service.setup_data(reindex=False)
    logger.info("Data setup complete. The bot is ready to serve requests.")


@app.post("/chat", response_model=ChatResponse)
@limiter.limit("20/minute")
async def chat_with_bot(request: Request, chat_request: ChatRequest):
    """
    The main endpoint to chat with the AI assistant.
    Automatically maintains conversation history based on the user's IP address.
    """
    try:
        # Use the client's IP address as the automatic session ID.
        session_id = get_remote_address(request)
        if not session_id:
            # Fallback for environments where IP is not available
            raise HTTPException(status_code=400, detail="Could not identify client address.")

        logger.info(f"Received query: '{chat_request.query}' from session (IP): {session_id}")

        # The bot service handles the conversation using the IP as the session key.
        response_text = bot_service.ask(chat_request.query, session_id)
        
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"An error occurred while processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")

@app.get("/health", response_model=dict)
async def health_check(request: Request):
    """A simple health check endpoint."""
    return {"status": "ok"}