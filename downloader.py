import os
import requests
import re
import time
from typing import Dict, Any, Optional

RAPIDAPI_HOST = "youtube-media-downloader.p.rapidapi.com"
# Sebaiknya pindahkan ke .env (os.getenv("RAPIDAPI_KEY")) di tahap produksi
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "336b94c1f0mshdc0e4d3812bed2dp127c33jsn4f7673bda404")

class YouTubeDownloader:
    def __init__(self, download_dir: str = "downloads"):
        # Kita sebenarnya tidak menyimpan file lagi di sini, tapi
        # untuk menjaga kompatibilitas dengan sisa kode, kita biarkan init-nya.
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
        
    def _extract_video_id(self, url: str) -> str:
        """Ekstrak ID video YouTube dari berbagai format URL"""
        patterns = [
            r'(?:v=|\/)([0-9A-Za-z_-]{11}).*',
            r'(?:youtu\.be\/)([0-9A-Za-z_-]{11})',
            r'(?:embed\/)([0-9A-Za-z_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
                
        raise ValueError("URL YouTube tidak valid atau ID tidak ditemukan.")

    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Dapatkan info video menggunakan RapidAPI dan oEmbed"""
        video_id = self._extract_video_id(url)
        
        # 1. Ambil Metadata via YouTube oEmbed (gratis, tanpa blokir IP)
        oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
        try:
            oembed_resp = requests.get(oembed_url, timeout=5)
            oembed_data = oembed_resp.json() if oembed_resp.ok else {}
        except Exception:
            oembed_data = {}
            
        # 2. Ambil Link Download via RapidAPI
        rapid_url = f"https://{RAPIDAPI_HOST}/v2/video/details"
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
            "Content-Type": "application/json"
        }
        
        params = {
            "videoId": video_id,
            "urlAccess": "normal",
            "videos": "auto",
            "audios": "auto"
        }
        
        rapid_resp = requests.get(rapid_url, headers=headers, params=params, timeout=15)
        if not rapid_resp.ok:
            raise Exception(f"Gagal menghubungi API ({rapid_resp.status_code}): {rapid_resp.text}")
            
        rapid_data = rapid_resp.json()
        
        # Cek Error dari API baru
        if rapid_data.get("errorId") and rapid_data.get("errorId") != "Success":
            raise Exception(f"API Error: {rapid_data.get('errorId')}")
            
        # Ambil audio
        audios = rapid_data.get("audios", {}).get("items", [])
        if not audios:
            raise Exception("API tidak mengembalikan link audio yang valid.")
            
        audio_streams = []
        for audio in audios:
            fsize = audio.get("size", 0)
            fsize_mb = fsize / (1024 * 1024) if fsize else 0
            extension = audio.get("extension", "m4a")
            
            audio_streams.append({
                'abr': f'Audio {extension.upper()}',
                'filesize': fsize,
                'filesize_mb': fsize_mb,
                'itag': 'rapidapi',
                'link': audio.get("url")
            })

        # Ambil thumbnail
        thumbnails_list = rapid_data.get("thumbnails", [])
        if thumbnails_list:
            thumb_url = thumbnails_list[-1].get("url") # Ambil resolusi terbesar
        else:
            thumb_url = oembed_data.get("thumbnail_url") if oembed_data else f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
            
        author = rapid_data.get("channel", {}).get("name") or oembed_data.get("author_name") or "YouTube"
        
        return {
            'title': rapid_data.get("title") or oembed_data.get("title") or "Unknown Title",
            'author': author,
            'length': rapid_data.get("lengthSeconds") or 0,
            'views': rapid_data.get("viewCount") or 0,
            'description': rapid_data.get("description") or "",
            'thumbnail_url': thumb_url,
            'video_streams': [], # Kosong karena antarmuka kita fokus ke audio
            'audio_streams': audio_streams
        }