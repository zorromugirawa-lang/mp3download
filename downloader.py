import os
import yt_dlp
from typing import Dict, Any, Optional

class YouTubeDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = download_dir
        os.makedirs(download_dir, exist_ok=True)
    
    def get_video_info(self, url: str) -> Dict[str, Any]:
        """Dapatkan informasi detail video menggunakan yt-dlp"""
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'skip_download': True
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            
        video_streams = []
        unique_res = {}
        
        # Cari format video
        for f in info.get('formats', []):
            if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                height = f.get('height')
                if not height:
                    continue
                    
                res_str = f"{height}p"
                
                if res_str not in ['1080p', '720p', '480p', '360p', '144p']:
                    continue
                    
                fsize = f.get('filesize') or f.get('filesize_approx') or 0
                fsize_mb = fsize / (1024 * 1024) if fsize else 0
                
                # yt-dlp memisahkan video+audio (progressive) dan video only.
                # Kita lebih menyukai video yang memiliki codec audio (acodec != none)
                # untuk menghindari video tanpa suara.
                has_audio = f.get('acodec') != 'none'
                
                # Simpan resolusi (update jika ada yang punya audio, atau ukuran lebih masuk akal)
                if res_str not in unique_res or (has_audio and not unique_res[res_str].get('has_audio')):
                    unique_res[res_str] = {
                        'resolution': res_str,
                        'fps': f.get('fps', 30),
                        'filesize': fsize,
                        'filesize_mb': fsize_mb,
                        'itag': f.get('format_id'), 
                        'type': 'video/mp4',
                        'has_audio': has_audio
                    }
                    
        # Urutkan resolusi
        res_order = {'1080p': 1, '720p': 2, '480p': 3, '360p': 4, '144p': 5}
        sorted_res = sorted(unique_res.values(), key=lambda x: res_order.get(x['resolution'], 99))
        
        # Hapus flag has_audio agar tidak membingungkan frontend
        for s in sorted_res:
            s.pop('has_audio', None)
            
        video_streams = sorted_res

        # Cari format audio
        audio_streams = []
        unique_abr = {}
        
        for f in info.get('formats', []):
            if f.get('vcodec') == 'none' and f.get('acodec') != 'none':
                abr = f.get('abr')
                if not abr:
                    continue
                    
                abr_str = f"{int(abr)}kbps"
                
                fsize = f.get('filesize') or f.get('filesize_approx') or 0
                fsize_mb = fsize / (1024 * 1024) if fsize else 0
                
                if abr_str not in unique_abr:
                    unique_abr[abr_str] = {
                        'abr': abr_str,
                        'filesize': fsize,
                        'filesize_mb': fsize_mb,
                        'itag': f.get('format_id')
                    }
                    
        audio_streams = sorted(unique_abr.values(), key=lambda x: int(x['abr'].replace('kbps', '')), reverse=True)

        return {
            'title': info.get('title', 'Unknown Title'),
            'author': info.get('uploader', 'Unknown Author'),
            'length': info.get('duration', 0),
            'views': info.get('view_count', 0),
            'description': info.get('description', '')[:500] + '...' if info.get('description') else '',
            'thumbnail_url': info.get('thumbnail', ''),
            'video_streams': video_streams,
            'audio_streams': audio_streams
        }

    def download_video(self, url: str, quality: str = "highest", filename: Optional[str] = None) -> Dict[str, Any]:
        """Download video menggunakan yt-dlp"""
        height = quality.replace('p', '') if quality and quality != "highest" else None
        
        # best[height<=...][ext=mp4] akan mencari video terbaik yang ukurannya maksimal sebesar height
        # yang merupakan format pre-merged (video+audio).
        if height:
            format_selector = f'best[height<={height}][ext=mp4]/best'
        else:
            format_selector = 'best[ext=mp4]/best'
            
        out_tpl = os.path.join(self.download_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': format_selector,
            'outtmpl': out_tpl,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            dl_filename = ydl.prepare_filename(info)
            
        return {
            'success': True,
            'message': 'Download berhasil',
            'filename': os.path.basename(dl_filename),
            'filepath': dl_filename,
            'filesize': os.path.getsize(dl_filename) if os.path.exists(dl_filename) else 0
        }

    def download_audio(self, url: str, filename: Optional[str] = None) -> Dict[str, Any]:
        """Download audio menggunakan yt-dlp"""
        out_tpl = os.path.join(self.download_dir, '%(title)s.%(ext)s')
        
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': out_tpl,
            'quiet': True,
            'no_warnings': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            # Karena kita tidak memaksa transcode mp3 via ffmpeg, file aslinya (.webm/.m4a) yang akan dikembalikan
            dl_filename = ydl.prepare_filename(info)
            
        return {
            'success': True,
            'message': 'Download audio berhasil',
            'filename': os.path.basename(dl_filename),
            'filepath': dl_filename,
            'filesize': os.path.getsize(dl_filename) if os.path.exists(dl_filename) else 0
        }