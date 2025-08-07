import requests
import PyPDF2
import io
import logging
from typing import Union

logger = logging.getLogger(__name__)

class PDFService:
    """
    A service for downloading and extracting text from PDF files.
    """
    def __init__(self, pdf_url: str):
        self.session = requests.Session()
        self.url = pdf_url

    def download_pdf(self) -> Union[bytes, None]:
        """
        Downloads a PDF file from the instance's URL.
        """
        if not self.url:
            logger.warning("No PDF URL provided.")
            return None
        try:
            logger.info(f"Downloading PDF from: {self.url}")
            response = self.session.get(self.url, stream=True)
            response.raise_for_status()
            logger.info("PDF downloaded successfully.")
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading PDF from {self.url}: {e}", exc_info=True)
            return None

    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Union[str, None]:
        """
        Extracts all text from the binary content of a PDF file.
        """
        try:
            logger.info("Extracting text from PDF bytes.")
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PyPDF2.PdfReader(pdf_file)
            all_text = "".join(page.extract_text() for page in reader.pages)
            logger.info("Text extracted successfully.")
            return all_text
        except PyPDF2.errors.PdfReadError:
            logger.error("Error: The file is not a valid PDF or is corrupted.")
            return None
        except Exception as e:
            logger.error(f"An unexpected error occurred during text extraction: {e}", exc_info=True)
            return None

    def process_pdf(self) -> Union[str, None]:
        """
        Downloads a PDF and extracts all text from it.
        """
        pdf_content = self.download_pdf()
        if pdf_content:
            return self.extract_text_from_bytes(pdf_content)
        return None