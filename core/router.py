from urllib.parse import urlparse

class URLRouter:
    YTDLP_DOMAINS = [
        "youtube.com", "youtu.be",
        "instagram.com", 
        "twitter.com", "x.com",
        "tiktok.com",
        "vimeo.com",
        "dailymotion.com",
        "twitch.tv",
        "facebook.com"
    ]
    
    @staticmethod
    def get_route_strategy(url: str) -> str:
        """
        Determines the best strategy based on URL.
        Returns: 'DIRECT_MEDIA', 'GENERIC_BROWSER'
        """
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Check against known yt-dlp supported domains
        for d in URLRouter.YTDLP_DOMAINS:
            if d in domain:
                return "DIRECT_MEDIA"
        
        return "GENERIC_BROWSER"
