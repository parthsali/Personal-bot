import os
import logging
from app.services.github_service import GitHubService
from app.services.pdf_service import PDFService
from app.services.vector_store.vector_store_service import VectorStoreService
from app.config import Config

logger = logging.getLogger(__name__)

def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 50) -> list[str]:
    """
    Splits a string into a list of overlapping chunks.
    """
    if not isinstance(text, str) or not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def run_data_pipeline(reindex: bool = False):
    """
    Orchestrates the fetching and processing of data and builds the vector index.
    """
    logger.info("Initializing services for data pipeline...")
    try:
        github_service = GitHubService(Config.GITHUB_PAT)
        pdf_service = PDFService(Config.RESUME_URL)
        vector_store = VectorStoreService()
    except Exception as e:
        logger.error(f"Error initializing services: {e}", exc_info=True)
        return

    if reindex or not os.path.exists(vector_store.index_file):
        logger.info("Starting full data re-indexing...")
        try:
            # --- Data Fetching ---
            logger.info("Fetching data from all sources...")
            github_data = github_service.fetch_all_detailed_repos()
            pdf_text = pdf_service.process_pdf()
            logger.info("Data fetching complete.")

            # --- Data Processing and Chunking ---
            all_text_data = []
            logger.info("Processing and chunking GitHub data...")
            for repo in github_data:
                repo_text = (
                    f"Repository: {repo.get('name', 'N/A')}\n"
                    f"Description: {repo.get('description', 'N/A')}\n"
                    f"Link: {repo.get('html_url', 'N/A')}\n"
                    f"Total stars: {repo.get('stargazers_count', 'N/A')}\n"
                    f"Is it private: {repo.get('private', 'N/A')}\n"
                    f"README: {repo.get('readme_content', 'No README found.')}\n"
                )
                if repo_text.strip():
                    all_text_data.extend(_chunk_text(repo_text))
            logger.info("GitHub data processed.")

            logger.info("Processing and chunking PDF resume data...")
            if pdf_text and pdf_text.strip():
                all_text_data.extend(_chunk_text(pdf_text))
            logger.info("PDF resume data processed.")

            # --- Vector Index Creation ---
            if all_text_data:
                vector_store.create_and_save_index(all_text_data)
            else:
                logger.warning("No text data was processed. Vector index not created.")

        except Exception as e:
            logger.error(f"An error occurred during data fetching and indexing: {e}", exc_info=True)
            return
    else:
        logger.info("Loading existing vector index.")
        vector_store.load_index()

    logger.info("Data pipeline complete. The vector index is ready.")