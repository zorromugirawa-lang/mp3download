import os
import re
import uuid
from datetime import datetime

def sanitize_filename(filename: str) -> str:
    """Bersihkan nama file dari karakter ilegal"""
    # Hapus karakter ilegal untuk Windows/Linux
    filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Batasi panjang nama
    if len(filename) > 200:
        filename = filename[:200]
    return filename.strip()

def generate_unique_filename(original: str, extension: str = "mp4") -> str:
    """Generate nama file unik"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = uuid.uuid4().hex[:8]
    base = sanitize_filename(original)
    return f"{base}_{timestamp}_{unique_id}.{extension}"

def format_filesize(bytes: int) -> str:
    """Format ukuran file ke MB/GB"""
    if bytes < 1024 * 1024:
        return f"{bytes / 1024:.2f} KB"
    elif bytes < 1024 * 1024 * 1024:
        return f"{bytes / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes / (1024 * 1024 * 1024):.2f} GB"

def get_file_extension(file_type: str) -> str:
    """Dapatkan ekstensi file berdasarkan tipe"""
    extensions = {
        "video": "mp4",
        "audio": "mp3",
        "audio_raw": "m4a"
    }
    return extensions.get(file_type, "mp4")