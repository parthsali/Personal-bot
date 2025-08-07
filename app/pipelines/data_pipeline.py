import json
import os
from typing import Union
from services.github_service import GitHubService
from services.pdf_service import PDFService
from config import Config


def run_data_pipeline():
    """
    Orchestrates the fetching and processing of data from various services.
    This function acts as a central pipeline for all data-related tasks.
    """
 
    
    # Initialize all services with their respective configurations
    try:
        github_service = GitHubService(Config.GITHUB_PERSONAL_ACCESS_TOKEN)
        pdf_service = PDFService(Config.RESUME_URL)
    except Exception as e:
        print(f"Error initializing services: {e}")
        return

    # --- GitHub Data Processing ---
    print("--- Starting GitHub Data Fetch ---")
    try:
        github_data = github_service.fetch_all_detailed_repos()
        if github_data:
            github_file_path = "github_data.txt"
            with open(github_file_path, 'w', encoding='utf-8') as github_file:
                # The `json.dump()` function correctly converts the list
                # of dictionaries into a JSON string before writing.
                json.dump(github_data, github_file, indent=4)
            print(f"GitHub data successfully saved to {github_file_path}")
        else:
            print("No GitHub data fetched.")
    except Exception as e:
        print(f"An error occurred during GitHub data fetching: {e}")

    # --- PDF Data Processing ---
    print("\n--- Starting PDF Processing ---")
    try:
        resume_data = pdf_service.process_pdf()
        if resume_data:
            resume_file_path = "resume_data.txt"
            with open(resume_file_path, "w", encoding="utf-8") as resume_file:
                resume_file.write(resume_data)
            print(f"Text successfully extracted and saved to {resume_file_path}")
        else:
            print("Failed to process the PDF.")
    except Exception as e:
        print(f"An error occurred during PDF processing: {e}")
