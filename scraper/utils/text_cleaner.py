import re
import html

class TextCleaner:
    @staticmethod
    def clean(text: str) -> str:
        """
        Cleans raw text by removing HTML tags, extra whitespace, and normalizing Unicode.
        """
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove HTML tags (fallback if not using a parser)
        text = re.sub(r'<[^>]+>', '', text)
        
        # Replace multiple whitespace/newlines with single space
        text = re.sub(r'\s+', ' ', text)
        
        # Trim
        return text.strip()

    @staticmethod
    def normalize_date(date_str: str) -> str:
        """
        Attempts to normalize date strings to ISO format. 
        (Simplified version, can be expanded with dateparser)
        """
        if not date_str:
            return ""
        return date_str.strip()
