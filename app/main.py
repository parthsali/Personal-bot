import uvicorn
import logging
import sys

# --- Logging Configuration ---
# Configure logging for the entire application
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    logger.info("=========================================")
    logger.info("    Starting FastAPI Server for AI Bot   ")
    logger.info("=========================================")
    logger.info("Navigate to http://127.0.0.1:8000/docs for the API documentation.")
    
    # Run the FastAPI server using uvicorn
    uvicorn.run("app.server:app", host="127.0.0.1", port=8000, reload=True)