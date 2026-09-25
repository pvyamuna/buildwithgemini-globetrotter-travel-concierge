import os
from dotenv import load_dotenv

# Load .env file automatically for pytest
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))
