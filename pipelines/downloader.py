import aiohttp
import asyncio
import logging
from pathlib import Path
from config import settings
import aiofiles

class Downloader:
    def __init__(self):
        self.logger = logging.getLogger("Downloader")

    async def download_file(self, url: str, folder: str = "misc", filename: str = None) -> Path:
        """Downloads a single file to the specified folder."""
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Determine filename
                        if not filename:
                            filename = url.split("/")[-1].split("?")[0]
                            if not filename:
                                filename = "downloaded_file"
                        
                        # Clean filename
                        filename = "".join([c for c in filename if c.isalpha() or c.isdigit() or c in "._- "])
                        
                        save_dir = settings.DOWNLOADS_DIR / folder
                        save_dir.mkdir(parents=True, exist_ok=True)
                        save_path = save_dir / filename
                        
                        self.logger.info(f"Downloading {url} to {save_path}")
                        
                        f = await aiofiles.open(save_path, mode='wb')
                        await f.write(await response.read())
                        await f.close()
                        
                        return save_path
                    else:
                        self.logger.error(f"Failed to download {url}, status: {response.status}")
                        return None
            except Exception as e:
                self.logger.error(f"Error downloading {url}: {e}")
                return None

    async def download_batch(self, urls: list, folder: str):
        """Downloads multiple files concurrently."""
        tasks = [self.download_file(url, folder) for url in urls]
        return await asyncio.gather(*tasks)
