import asyncio
from typing import Dict, Any, List
from extractors.base import BaseExtractor
from core.types import ContentType
import yt_dlp
import logging
from pathlib import Path

class MediaExtractor(BaseExtractor):
    def __init__(self, page):
        super().__init__(page)
        self.logger = logging.getLogger("MediaExtractor")

    def supports(self, content_type: ContentType) -> bool:
        return content_type in [ContentType.VIDEO_PLATFORM, ContentType.VIDEO_EMBED]

    async def extract(self) -> Dict[str, Any]:
        """
        Uses yt-dlp to extract video info. 
        It generally performs better on the URL itself rather than the DOM, 
        but for embeds we might need to find the src.
        """
        url = self.page.url
        self.logger.info(f"Attempting media extraction on {url}")
        
        # Get cookies from browser to pass to yt-dlp (Fixes 403 Forbidden)
        cookies = await self.page.context.cookies()
        user_agent = await self.page.evaluate("navigator.userAgent") # Get actual UA
        
        try:
            # We run yt-dlp in a separate thread/process to stay async
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(None, self._run_ytdlp, url, cookies, user_agent)
            return {
                "type": "media",
                "media_type": "video", # or audio
                "title": info.get("title"),
                "url": url,
                "download_url": info.get("url"), # The direct stream url if resolved
                "id": info.get("id"),
                "thumbnail": info.get("thumbnail"),
                "formats": info.get("formats", [])[:5] # Just keeping a few for debug
            }
        except Exception as e:
            self.logger.error(f"yt-dlp extraction failed: {e}")
            # Fallback: manually look for <video src="...">
            video_src = await self.page.locator("video").get_attribute("src")
            if video_src:
                return {
                     "type": "media",
                     "media_type": "video_raw",
                     "url": url,
                     "download_url": video_src,
                     "title": await self.page.title()
                }
            return {"error": "No media found"}

    def _run_ytdlp(self, url: str, cookies: List[dict], user_agent: str):
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True,
            'user_agent': user_agent, 
        }
        
        import tempfile
        import os
        
        def write_netscape_cookies(cookies, path):
             with open(path, 'w') as f:
                 f.write("# Netscape HTTP Cookie File\\n")
                 for c in cookies:
                     domain = c.get('domain', '')
                     flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                     path_attr = c.get('path', '/')
                     secure = 'TRUE' if c.get('secure', False) else 'FALSE'
                     expiry = str(int(c.get('expires', 0)))
                     name = c.get('name', '')
                     value = c.get('value', '')
                     f.write(f"{domain}\\t{flag}\\t{path_attr}\\t{secure}\\t{expiry}\\t{name}\\t{value}\\n")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            cookie_path = tmp.name
        
        try:
            write_netscape_cookies(cookies, cookie_path)
            ydl_opts['cookiefile'] = cookie_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        finally:
            if os.path.exists(cookie_path):
                os.remove(cookie_path)

    async def download(self, msg_logger=None) -> Path:
        """
        Downloads the video using yt-dlp with the current browser session.
        """
        url = self.page.url
        self.logger.info(f"Starting download for: {url}")
        
        cookies = await self.page.context.cookies()
        user_agent = await self.page.evaluate("navigator.userAgent")
        
        loop = asyncio.get_event_loop()
        path = await loop.run_in_executor(None, self._run_ytdlp_download, url, cookies, user_agent)
        return path

    def _run_ytdlp_download(self, url: str, cookies: List[dict], user_agent: str) -> Path:
        import tempfile
        import os
        from config import settings
        
        save_dir = settings.DOWNLOADS_DIR / "video"
        save_dir.mkdir(parents=True, exist_ok=True)
        
        # Output template
        out_tmpl = str(save_dir / '%(title)s.%(ext)s')
        
        ydl_opts = {
            'quiet': False, 
            'no_warnings': True,
            'user_agent': user_agent,
            'outtmpl': out_tmpl,
            'format': 'best',
        }
        
        def write_netscape_cookies(cookies, path):
             with open(path, 'w') as f:
                 f.write("# Netscape HTTP Cookie File\\n")
                 for c in cookies:
                     domain = c.get('domain', '')
                     flag = 'TRUE' if domain.startswith('.') else 'FALSE'
                     path_attr = c.get('path', '/')
                     secure = 'TRUE' if c.get('secure', False) else 'FALSE'
                     expiry = str(int(c.get('expires', 0)))
                     name = c.get('name', '')
                     value = c.get('value', '')
                     f.write(f"{domain}\\t{flag}\\t{path_attr}\\t{secure}\\t{expiry}\\t{name}\\t{value}\\n")

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp:
            cookie_path = tmp.name
        
        try:
            write_netscape_cookies(cookies, cookie_path)
            ydl_opts['cookiefile'] = cookie_path
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                return save_dir
        except Exception as e:
            self.logger.error(f"Download failed: {e}")
            raise e
        finally:
            if os.path.exists(cookie_path):
                os.remove(cookie_path)
