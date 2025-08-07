import logging
from app.config import Config
from app.services.gemini_service import GeminiService
from app.services.vector_store.vector_store_service import VectorStoreService
from app.pipelines.data_pipeline import run_data_pipeline
from typing import Dict, Tuple

logger = logging.getLogger(__name__)

class BotService:
    """
    Encapsulates the bot's functionality, acting as a bridge to the Gemini service.
    """
    def __init__(self, config: Config):
        logger.info("Initializing Bot Service...")
        self.config = config
        self.vector_store = VectorStoreService()
        self.gemini_service = GeminiService(config.GEMINI_API_KEY, self.vector_store)
        logger.info("Bot Service initialized successfully.")

    def setup_data(self, reindex: bool = False):
        """
        Runs the data pipeline and ensures the vector store is loaded.
        """
        logger.info("Bot service is triggering the data pipeline.")
        run_data_pipeline(reindex)
        
        logger.info("Loading vector index into the bot's memory...")
        self.vector_store.load_index()

    def get_greeting(self) -> str:
        """
        Gets a dynamic, AI-generated greeting.
        """
        return self.gemini_service.generate_greeting()

    def ask(self, user_query: str) -> str:
        """
        Handles user queries by forwarding them to the GeminiService.
        """
        logger.info("Forwarding query to Gemini Service for a personality-driven response.")
        return self.gemini_service.chat(user_query)