from typing import Dict, Any, List
from extractors.base import BaseExtractor
from core.types import ContentType
import logging

class TextExtractor(BaseExtractor):
    def __init__(self, page):
        super().__init__(page)
        self.logger = logging.getLogger("TextExtractor")

    def supports(self, content_type: ContentType) -> bool:
        return content_type == ContentType.ARTICLE

    async def extract(self) -> Dict[str, Any]:
        self.logger.info("Extracting text content...")
        
        # Simple extraction strategy:
        # 1. Look for <article> content
        # 2. If not, fallback to grabbing all <p> tags
        
        data = await self.page.evaluate("""() => {
            const article = document.querySelector('article');
            if (article) {
                return {
                    title: document.querySelector('h1')?.innerText,
                    content: article.innerText,
                    html: article.innerHTML
                };
            }
            
            // Fallback
            const paragraphs = Array.from(document.querySelectorAll('p')).map(p => p.innerText).join('\\n\\n');
            return {
                title: document.title,
                content: paragraphs,
                html: ''
            };
        }""")

        return {
            "type": "text",
            "data": data
        }
