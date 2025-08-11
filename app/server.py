import os
import sys
import re
import logging # <-- Import logging
from fastapi import FastAPI, Request, HTTPException, Security, BackgroundTasks
from fastapi.security import APIKeyHeader
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from pydantic import BaseModel

# --- Project Root Setup ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from app.config import Config
from app.services.bot_service import BotService

# --- Initialize Config FIRST ---
Config.initialize_paths(project_root)

# --- Logging Configuration ---
# This is the new, correct location for the logging setup.
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        # Use Config.LOG_FILE and mode 'a' to append to the log file
        logging.FileHandler(Config.LOG_FILE, mode='a') 
    ]
)
logger = logging.getLogger(__name__)

# --- Initialize Services ---
Config.validate()
bot_service = BotService(Config)

# --- FastAPI App Setup ---
app = FastAPI(title="Personal AI Assistant API")
templates = Jinja2Templates(directory=os.path.join(os.path.dirname(__file__), "templates"))
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# --- Security Setup ---
api_key_header = APIKeyHeader(name="X-Update-Token", auto_error=True)

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header != Config.UPDATE_TOKEN:
        raise HTTPException(status_code=403, detail="Could not validate credentials")
    return api_key_header

# --- Pydantic Models ---
class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str

# --- Log Parsing Function ---
def parse_log_file():
    """Parses the application log file and returns a list of log entries."""
    logs = []
    log_pattern = re.compile(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) - ([\w.]+) - (\w+) - (.+)")
    try:
        with open(Config.LOG_FILE, 'r') as f:
            for line in f:
                match = log_pattern.match(line)
                if match:
                    logs.append({
                        "timestamp": match.group(1),
                        "module": match.group(2),
                        "level": match.group(3),
                        "message": match.group(4)
                    })
    except FileNotFoundError:
        logger.warning("Log file not found. It will be created upon first log event.")
    return sorted(logs, key=lambda x: x['timestamp'], reverse=True)


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
    """The main endpoint to chat with the AI assistant."""
    try:
        session_id = get_remote_address(request)
        if not session_id:
            raise HTTPException(status_code=400, detail="Could not identify client address.")

        logger.info(f"Received query: '{chat_request.query}' from session (IP): {session_id}")
        response_text = bot_service.ask(chat_request.query, session_id)
        
        return ChatResponse(response=response_text)
    except Exception as e:
        logger.error(f"An error occurred while processing chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="An internal server error occurred.")


@app.post("/update-context", status_code=202)
async def update_context(background_tasks: BackgroundTasks, api_key: str = Security(get_api_key)):
    """Triggers a full data pipeline refresh in the background."""
    logger.info("Received authenticated request to update context.")
    background_tasks.add_task(bot_service.setup_data, reindex=True)
    logger.info("Context update successfully initiated in the background.")
    return {"message": "Context update initiated. The process is running in the background."}


@app.get("/logs", response_class=HTMLResponse)
async def view_logs(request: Request):
    """Displays the application logs in a formatted HTML table."""
    logger.info(f"Log page accessed by {request.client.host}")
    logs = parse_log_file()
    return templates.TemplateResponse("logs.html", {"request": request, "logs": logs})


@app.get("/health", response_model=dict)
async def health_check(request: Request):
    """A simple health check endpoint."""
    return {"status": "ok"}