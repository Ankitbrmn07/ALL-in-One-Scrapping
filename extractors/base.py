from abc import ABC, abstractmethod
from playwright.async_api import Page
from typing import List, Dict, Any
from core.types import ContentType

class BaseExtractor(ABC):
    def __init__(self, page: Page):
        self.page = page

    @abstractmethod
    async def extract(self) -> Dict[str, Any]:
        """Performs the extraction and returns structured data."""
        pass
    
    @abstractmethod
    def supports(self, content_type: ContentType) -> bool:
        """Returns True if this extractor handles the given content type."""
        pass
