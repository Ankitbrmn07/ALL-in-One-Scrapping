import yt_dlp
import logging
from typing import Dict, Any, List

class DirectMediaHandler:
    def __init__(self):
        self.logger = logging.getLogger("DirectMediaHandler")

    def extract(self, url: str) -> Dict[str, Any]:
        self.logger.info(f"Using Direct Media Extraction (yt-dlp) for: {url}")
        
        # We need to capture 403 errors specifically because they don't always raise exceptions in extract_info logic
        # if some formats are available.
        
        forbidden_detected = False
        
        def error_hook(msg):
            nonlocal forbidden_detected
            if "HTTP Error 403" in msg or "Forbidden" in msg:
                forbidden_detected = True

        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'logger': UrlLogger(error_hook)
        }
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if forbidden_detected:
                    raise Exception("HTTP 403 Forbidden detected during extraction (IP Blocked or Cookies required)")
                
                return {
                    "type": "media",
                    "strategy": "direct",
                    "media_type": "video",
                    "title": info.get("title"),
                    "url": url,
                    "download_url": info.get("url"), # Often a manifest
                    "id": info.get("id"),
                    "thumbnail": info.get("thumbnail"),
                    "metadata": {
                        "duration": info.get("duration"),
                        "uploader": info.get("uploader"),
                        "view_count": info.get("view_count")
                    }
                }
        except Exception as e:
            self.logger.warning(f"Direct extraction failed: {e}")
            return {"error": str(e)}

class UrlLogger:
    def __init__(self, callback):
        self.callback = callback
    
    def debug(self, msg):
        if "403" in msg: self.callback(msg)
    
    def warning(self, msg):
        self.callback(msg)
    
    def error(self, msg):
        self.callback(msg)
