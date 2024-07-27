import pytest
from dotenv import load_dotenv
import os

# Load environment variables from .env file before running tests
load_dotenv()

def test_openai_api_key_exists():
    """Test that the OPENAI_API_KEY environment variable is set."""
    api_key = os.getenv('OPENAI_API_KEY')
    assert api_key is not None, "OPENAI_API_KEY should not be None"

def test_eraserio_api_key_exists():
    """Test that the ERASER_IO_API_KEY environment variable is set."""
    api_key = os.getenv('ERASER_IO_API_KEY')
    assert api_key is not None, "ERASER_IO_API_KEY should not be None"

test_openai_api_key_exists()
test_eraserio_api_key_exists()