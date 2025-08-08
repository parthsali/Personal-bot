import logging
from app.config import Config
from app.services.gemini_service import GeminiService
from app.services.vector_store.vector_store_service import VectorStoreService
from app.pipelines.data_pipeline import run_data_pipeline
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class BotService:
    """
    Encapsulates the bot's functionality, including session management.
    """
    def __init__(self, config: Config):
        logger.info("Initializing Bot Service...")
        self.config = config
        self.vector_store = VectorStoreService()
        self.gemini_service = GeminiService(config.GEMINI_API_KEY, self.vector_store)
        self.sessions = {} # In-memory dictionary to store chat sessions
        logger.info("Bot Service initialized successfully.")

    def setup_data(self, reindex: bool = False):
        """Runs the data pipeline and ensures the vector store is loaded."""
        logger.info("Bot service is triggering the data pipeline.")
        run_data_pipeline(reindex)
        logger.info("Loading vector index into the bot's memory...")
        self.vector_store.load_index()

    def get_greeting(self) -> str:
        """Gets a dynamic, AI-generated greeting."""
        return self.gemini_service.generate_greeting()

    def ask(self, user_query: str, session_id: str) -> str:
        """
        Handles user queries using a session_id to maintain conversation history.
        """
        # Get or create a chat session for the user
        if session_id not in self.sessions:
            logger.info(f"Creating new chat session for session_id: {session_id}")
            self.sessions[session_id] = self.gemini_service.start_new_chat()
        
        current_session = self.sessions[session_id]

        logger.info(f"Forwarding query to Gemini Service for session: {session_id}")
        return self.gemini_service.chat(user_query, current_session)