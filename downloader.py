from pytubefix import YouTube
from pytubefix.cli import on_progress
from typing import Optional, Dict, Any
import os
from utils import generate_unique_filename, sanitize_filename

class YouTubeDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Dapatkan informasi detail video"""
        yt = YouTube(url)
        
        video_streams = []
        unique_res = {}
        # Kumpulkan semua stream mp4
        for stream in yt.streams.filter(file_extension='mp4'):
            res = stream.resolution
            if not res: continue
            
            # Simpan stream terbaik untuk setiap resolusi
            # Prioritaskan progressive, jika sama prioritaskan ukuran file
            if res not in unique_res:
                unique_res[res] = stream
            else:
                existing = unique_res[res]
                if stream.is_progressive and not existing.is_progressive:
                    unique_res[res] = stream
                elif stream.is_progressive == existing.is_progressive and stream.filesize > existing.filesize:
                    unique_res[res] = stream
                    
        # Filter hanya resolusi standar yang diinginkan (max 5)
        target_resolutions = ['1080p', '720p', '480p', '360p', '144p']
        for res in target_resolutions:
            if res in unique_res:
                stream = unique_res[res]
                video_streams.append({
                    "resolution": res,
                    "fps": stream.fps,
                    "filesize": stream.filesize,
                    "filesize_mb": round(stream.filesize / (1024 * 1024), 2),
                    "itag": stream.itag,
                    "type": "progressive" if stream.is_progressive else "adaptive"
                })
        
        audio_streams = []
        for stream in yt.streams.filter(only_audio=True):
            audio_streams.append({
                "abr": stream.abr or "Unknown",
                "filesize": stream.filesize,
                "filesize_mb": round(stream.filesize / (1024 * 1024), 2),
                "itag": stream.itag
            })
        
        return {
            "title": yt.title,
            "author": yt.author,
            "length": yt.length,
            "views": yt.views,
            "description": yt.description[:500] if yt.description else "",
            "thumbnail_url": yt.thumbnail_url,
            "video_streams": sorted(video_streams, key=lambda x: x.get('filesize', 0), reverse=True),
            "audio_streams": sorted(audio_streams, key=lambda x: x.get('filesize', 0), reverse=True)
        }
    
    def download_video(self, url: str, quality: str = "highest", filename: Optional[str] = None) -> Dict[str, Any]:
        """Download video dengan kualitas tertentu"""
        yt = YouTube(url, on_progress_callback=on_progress)
        
        if quality == "highest" or not quality:
            stream = yt.streams.get_highest_resolution()
        else:
            stream = yt.streams.filter(res=quality, progressive=True, file_extension='mp4').first()
            if not stream:
                # Coba cari di adaptive streams
                stream = yt.streams.filter(res=quality).first()
                if not stream:
                    return {"success": False, "message": f"Kualitas {quality} tidak tersedia"}
        
        if not stream:
            return {"success": False, "message": "Tidak ada stream yang tersedia"}
        
        # Generate filename
        if not filename:
            filename = generate_unique_filename(yt.title, "mp4")
        else:
            filename = sanitize_filename(filename) + ".mp4"
        
        file_path = os.path.join(self.download_dir, filename)
        stream.download(output_path=self.download_dir, filename=filename)
        
        return {
            "success": True,
            "message": "Download berhasil",
            "filename": filename,
            "filesize": stream.filesize,
            "path": file_path
        }
    
    def download_audio(self, url: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Download audio saja"""
        yt = YouTube(url, on_progress_callback=on_progress)
        
        stream = yt.streams.filter(only_audio=True).first()
        if not stream:
            return {"success": False, "message": "Tidak ada audio stream"}
        
        # Generate filename
        if not filename:
            filename = generate_unique_filename(yt.title, "m4a")
        else:
            filename = sanitize_filename(filename) + ".m4a"
        
        file_path = os.path.join(self.download_dir, filename)
        stream.download(output_path=self.download_dir, filename=filename)
        
        return {
            "success": True,
            "message": "Download audio berhasil",
            "filename": filename,
            "filesize": stream.filesize,
            "path": file_path
        }