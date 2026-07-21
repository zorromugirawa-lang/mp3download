import os
import requests
import re
from typing import Dict, Any, Optional

RAPIDAPI_HOST = "youtube-mp3-audio-video-downloader.p.rapidapi.com"
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
        rapid_url = f"https://{RAPIDAPI_HOST}/get_mp3_download_link/{video_id}"
        headers = {
            "x-rapidapi-host": RAPIDAPI_HOST,
            "x-rapidapi-key": RAPIDAPI_KEY,
            "Content-Type": "application/json"
        }
        
        # Gunakan parameter sesuai API baru
        params = {
            "quality": "high", 
            "wait_until_the_file_is_ready": "false"
        }
        
        rapid_resp = requests.get(rapid_url, headers=headers, params=params, timeout=15)
        if not rapid_resp.ok:
            raise Exception(f"Gagal menghubungi API ({rapid_resp.status_code})")
            
        rapid_data = rapid_resp.json()
        
        download_link = rapid_data.get("file")
        
        if not download_link:
            raise Exception(f"API tidak mengembalikan link audio yang valid. Respons API: {rapid_data.get('message', 'Tidak diketahui')}")
            
        # API baru tidak mengembalikan ukuran file, kita set 0
        fsize = 0
        fsize_mb = 0
        extension = "mp3"
        
        audio_streams = [{
            'abr': f'Audio {extension.upper()}',
            'filesize': fsize,
            'filesize_mb': fsize_mb,
            'itag': 'rapidapi',
            'link': download_link
        }]

        thumbnails = oembed_data.get('thumbnail_url') if oembed_data else f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
        thumb_url = thumbnails
        
        return {
            'title': oembed_data.get('title') or 'Unknown Title',
            'author': oembed_data.get('author_name') or 'YouTube',
            'length': 0, # Oembed tidak memberikan durasi secara default
            'views': 0, 
            'description': '',
            'thumbnail_url': thumb_url,
            'video_streams': [], # Kosong karena sekarang hanya Audio
            'audio_streams': audio_streams
        }