import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent.parent
DOWNLOADS_DIR = BASE_DIR / "downloads"
STORAGE_STATE_FILE = BASE_DIR / "storage_state.json"
LOG_DIR = BASE_DIR / "logs"

# Browser Configuration
HEADLESS = True  # Default to True, can be overridden by CLI
BROWSER_TIMEOUT = 30000  # 30 seconds
VIEWPORT = {"width": 1920, "height": 1080}
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# Concurrency
MAX_CONCURRENT_PAGES = 5

# Create dirs if they don't exist
DOWNLOADS_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)
