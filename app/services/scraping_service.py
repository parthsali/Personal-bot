import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import Set, List

logger = logging.getLogger(__name__)

class ScrapingService:
    """
    A service to scrape a website, extract text, and find internal links.
    """
    def __init__(self, root_url: str):
        if not root_url:
            raise ValueError("A root URL must be provided.")
        self.root_url = root_url
        self.domain = urlparse(root_url).netloc
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def _is_valid_url(self, url: str) -> bool:
        """
        Checks if a URL is valid, on the same domain, and not an anchor/media link.
        """
        parsed_url = urlparse(url)
        # Ensure it's a web link and on the same domain
        if parsed_url.scheme not in ['http', 'https'] or parsed_url.netloc != self.domain:
            return False
        # Ignore links to files or special protocols
        if parsed_url.path.split('.')[-1] in ['pdf', 'jpg', 'png', 'zip', 'mailto:', 'tel:']:
            return False
        return True

    def scrape_page(self, url: str) -> (str, List[str]):
        """
        Scrapes a single page for its text content and all valid internal links.
        Returns a tuple of (page_text, found_links).
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            # Ensure we are handling HTML content
            if 'text/html' not in response.headers.get('Content-Type', ''):
                logger.warning(f"Skipping non-HTML content at {url}")
                return "", []

            soup = BeautifulSoup(response.text, 'lxml')

            # Remove script and style elements
            for script_or_style in soup(['script', 'style']):
                script_or_style.decompose()

            # Get text and clean it up
            text = soup.get_text()
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            page_text = '\n'.join(chunk for chunk in chunks if chunk)
            
            # Find all links and resolve them
            links = []
            for a_tag in soup.find_all('a', href=True):
                href = a_tag['href']
                full_url = urljoin(self.root_url, href)
                if self._is_valid_url(full_url):
                    links.append(full_url)
            
            return page_text, links

        except requests.RequestException as e:
            logger.error(f"Failed to scrape {url}: {e}")
            return "", []

    def crawl_website(self) -> str:
        """
        Recursively crawls the entire website starting from the root URL.
        Returns all extracted text from all pages combined.
        """
        if not self.root_url:
            logger.info("No website URL provided. Skipping web scraping.")
            return ""

        urls_to_visit = [self.root_url]
        visited_urls: Set[str] = set()
        all_website_text = ""

        logger.info(f"Starting crawl of {self.root_url}")

        while urls_to_visit:
            url = urls_to_visit.pop(0)
            if url in visited_urls:
                continue

            logger.info(f"Scraping: {url}")
            visited_urls.add(url)

            text, new_links = self.scrape_page(url)
            if text:
                all_website_text += f"\n\n--- Content from {url} ---\n{text}"
            
            for link in new_links:
                if link not in visited_urls:
                    urls_to_visit.append(link)
        
        logger.info(f"Finished crawling. Visited {len(visited_urls)} pages.")
        return all_website_text