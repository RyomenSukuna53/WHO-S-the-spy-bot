import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Required variables
API_ID = int(os.getenv("25698862", 0))  # Default 0 if missing
API_HASH = os.getenv("7d7739b44f5f8c825d48cc6787889dbc", "")
TOKEN = os.getenv("7979148246:AAF1QDrslVCsOXWoGy9-XMbr05Ya9In-X1E", "")

# Ensure all required variables are present
if not all([API_ID, API_HASH, TOKEN]):
    raise ValueError("Missing required environment variables: API_ID, API_HASH, TOKEN")