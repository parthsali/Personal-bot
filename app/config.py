import os
from dotenv import load_dotenv

# Load environment variables from a .env file
load_dotenv()

class Config:
    """
    Centralized class for managing all application settings.
    """
    # --- API Keys and URLs ---
    GITHUB_PAT = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    RESUME_URL = os.getenv('RESUME_URL')
    WEBSITE_URL = os.getenv('WEBSITE_URL')
    
    # --- Security ---
    UPDATE_TOKEN = os.getenv('UPDATE_TOKEN')

    # --- Application Settings ---
    ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')
    
    APP_ROOT = None 
    DATA_PATH = None
    LOG_FILE = None # <-- Add log file path

    @staticmethod
    def initialize_paths(app_root: str):
        """Sets the root and data paths for the application."""
        Config.APP_ROOT = app_root
        Config.DATA_PATH = os.path.join(app_root, 'data')
        Config.LOG_FILE = os.path.join(app_root, 'app.log') # <-- Define log file path
        os.makedirs(Config.DATA_PATH, exist_ok=True)


    @staticmethod
    def validate():
        """
        Validates that all essential environment variables are set.
        """
        required_vars = ['GITHUB_PAT', 'GEMINI_API_KEY', 'RESUME_URL', 'UPDATE_TOKEN']
        missing_vars = [var for var in required_vars if not getattr(Config, var)]
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")