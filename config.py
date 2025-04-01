import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
load_dotenv()

# Get the base directory
BASE_DIR = Path(__file__).parent

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-key-123')
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR}/database/stylist.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
    OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
    OPENROUTER_APP_NAME = "StyleBot"
    
    @classmethod
    def check_config(cls):
        if not cls.OPENROUTER_API_KEY:
            raise ValueError("OpenRouter API key is missing. Please set OPENROUTER_API_KEY in .env file")