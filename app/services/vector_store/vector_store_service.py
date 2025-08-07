import os
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import json
import logging
from app.config import Config
from typing import List

logger = logging.getLogger(__name__)

class VectorStoreService:
    """
    Manages vector indexing and similarity search for text data.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        logger.info(f"Initializing SentenceTransformer with model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.index = None
        self.text_store = []
        
        # Use the configured data path
        self.data_path = Config.DATA_PATH
        self.index_file = os.path.join(self.data_path, 'vector_index.bin')
        self.text_file = os.path.join(self.data_path, 'text_store.json')

    def create_and_save_index(self, data: List[str]):
        """
        Creates a new FAISS index from a list of text data and saves it.
        """
        if not data:
            logger.warning("No data provided to create vector index.")
            return

        logger.info("Creating new vector index...")
        self.text_store = data
        embeddings = self.model.encode(data, show_progress_bar=True)
        embeddings = np.array(embeddings).astype('float32')
        faiss.normalize_L2(embeddings)

        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)
        self.index.add(embeddings)

        logger.info(f"Saving FAISS index to {self.index_file}")
        faiss.write_index(self.index, self.index_file)

        logger.info(f"Saving text store to {self.text_file}")
        with open(self.text_file, 'w', encoding='utf-8') as f:
            json.dump(self.text_store, f)
        logger.info("Vector index created and saved successfully.")

    def load_index(self) -> bool:
        """
        Loads an existing FAISS index and text store from files.
        """
        if os.path.exists(self.index_file) and os.path.exists(self.text_file):
            logger.info(f"Loading existing vector index from: {self.index_file}")
            try:
                self.index = faiss.read_index(self.index_file)
                with open(self.text_file, 'r', encoding='utf-8') as f:
                    self.text_store = json.load(f)
                logger.info("Vector index and text store loaded successfully into memory.")
                return True
            except Exception as e:
                logger.error(f"Error loading index or text store: {e}", exc_info=True)
                return False
        logger.warning("Index files not found. A new index needs to be created.")
        return False


    def search(self, query: str, k: int = 5) -> List[str]:
        """
        Performs a similarity search on the index for a given query.
        """
        if self.index is None:
            logger.error("Index is not loaded in memory. Cannot perform search.")
            raise RuntimeError("Index is not loaded. Call create_and_save_index() or load_index() first.")

        logger.info(f"Performing similarity search for query: '{query}'")
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        faiss.normalize_L2(query_embedding)

        distances, indices = self.index.search(query_embedding, k)
        results = [self.text_store[i] for i in indices[0] if i < len(self.text_store)]
        logger.info(f"Found {len(results)} relevant text chunks.")
        return results