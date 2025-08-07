import os
from dotenv import load_dotenv

# load env variables
load_dotenv()

class Config:
    GITHUB_PERSONAL_ACCESS_TOKEN = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    ENVORNMENT = os.getenv('ENVORNMENT')

