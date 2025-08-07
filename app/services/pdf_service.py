import requests
import PyPDF2
import io
import os
from typing import Union

class PDFService:
    """
    A service class for downloading and extracting text from PDF files.
    
    This class uses requests to download a PDF from a URL and PyPDF2
    to parse the text content.
    """
    def __init__(self, pdf_url: str):
        # A session can be used to persist parameters across requests
        self.session = requests.Session()
        # The URL is now an instance attribute, set on creation
        self.url = pdf_url

    def download_pdf(self) -> Union[bytes, None]:
        """
        Downloads a PDF file from the instance's URL.

        Returns:
            bytes | None: The raw binary content of the PDF file, or None on error.
        """
        try:
            print(f"Downloading PDF from: {self.url}")
            # Corrected: Use self.url here
            response = self.session.get(self.url, stream=True)
            response.raise_for_status() # Raise an HTTPError for bad responses
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF from {self.url}: {e}")
            return None

    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Union[str, None]:
        """
        Extracts all text from the binary content of a PDF file.

        Args:
            pdf_bytes (bytes): The raw binary content of the PDF.

        Returns:
            str | None: The extracted text as a single string, or None on error.
        """
        try:
            # Use a BytesIO object to treat the bytes as a file-like object
            # without saving it to disk.
            pdf_file = io.BytesIO(pdf_bytes)
            reader = PyPDF2.PdfReader(pdf_file)
            
            all_text = ""
            for page in reader.pages:
                all_text += page.extract_text()
                
            return all_text
        except PyPDF2.errors.PdfReadError:
            print("Error: The file is not a valid PDF or is corrupted.")
            return None
        except Exception as e:
            print(f"An unexpected error occurred during text extraction: {e}")
            return None

    def process_pdf(self) -> Union[str, None]:
        """
        Downloads a PDF using the instance's URL and extracts all text from it.

        Returns:
            str | None: The extracted text as a single string, or None on failure.
        """
        pdf_content = self.download_pdf()
        if pdf_content:
            return self.extract_text_from_bytes(pdf_content)
        return None