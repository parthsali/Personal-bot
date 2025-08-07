import os
from dotenv import load_dotenv

# load env variables
load_dotenv()

class Config:
    GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    RESUME_URL=os.getenv('RESUME_URL')
    ENVORNMENT = os.getenv('ENVORNMENT')
    

