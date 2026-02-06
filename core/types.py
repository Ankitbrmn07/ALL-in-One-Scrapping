from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Any

class ContentType(Enum):
    VIDEO_PLATFORM = "video_platform"  # Youtube, Vimeo, etc.
    VIDEO_EMBED = "video_embed"        # Page with <video> or <iframe>
    ARTICLE = "article"                # Text heavy
    IMAGE_GALLERY = "image_gallery"    # Many images
    PRODUCT = "product"                # E-commerce
    UNKNOWN = "unknown"

@dataclass
class PageAnalysis:
    content_type: ContentType
    title: str
    description: str
    score_details: Dict[str, float]
