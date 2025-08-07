import sys
import os
import logging
import random
from app.config import Config
from app.services.bot_service import BotService
from colorama import Fore, Style, init

# --- Project Root Setup ---
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("app.log", mode='w')
    ]
)
logger = logging.getLogger(__name__)

def main():
    """
    The main function to run the bot.
    """
    init(autoreset=True)

    logger.info("=========================================")
    logger.info("      Starting the AI Assistant Bot      ")
    logger.info("=========================================")

    try:
        Config.initialize_paths(project_root)
        logger.info(f"Data path set to: {Config.DATA_PATH}")

        Config.validate()
        logger.info("Configuration validated successfully.")

        bot_service = BotService(Config)
        bot_service.setup_data(reindex=False) 

        # --- AI-POWERED DYNAMIC GREETING ---
        initial_greeting = bot_service.get_greeting()

        logger.info("Starting interactive chat session. Type 'exit' to quit.")
        print(f"\n{Fore.YELLOW}Gemini: {initial_greeting}")

        while True:
            user_input = input(f"{Fore.CYAN}You: {Style.RESET_ALL}")
            if user_input.lower().strip() == 'exit':
                logger.info("Chat session ended by user.")
                break

            response = bot_service.ask(user_input)
            print(f"{Fore.YELLOW}Gemini: {Style.RESET_ALL}{response}")

    except ValueError as e:
        logger.error(f"Configuration error: {e}", exc_info=True)
    except Exception as e:
        logger.critical(f"An unrecoverable error occurred: {e}", exc_info=True)
    finally:
        logger.info("Bot shutting down.")


if __name__ == '__main__':
    main()