from services.github_service import GitHubService
from services.pdf_service import PDFService
from config import Config
import json

github_service = GitHubService(Config.GITHUB_PERSONAL_ACCESS_TOKEN)
pdf_service = PDFService(Config.RESUME_URL)

    

# github_data = github_service.fetch_all_detailed_repos()
pdf_data = pdf_service.process_pdf()

extracted_text = pdf_service.process_pdf()
    
if extracted_text:
    output_file = "resume.txt"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(extracted_text)

# file_path = "data.json"

# with open(file_path, 'w') as json_file:
#     json.dump(github_data, json_file, indent=4)