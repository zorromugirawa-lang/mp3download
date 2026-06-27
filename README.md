# 🎬 YouTube Downloader

Aplikasi lengkap untuk download video dan audio dari YouTube dengan antarmuka web.

## ✨ Fitur
- ✅ Download video dengan berbagai kualitas (1080p, 720p, 480p, dll)
- ✅ Download audio (MP3/M4A)
- ✅ Tampilan informasi video (judul, author, views, dll)
- ✅ Antarmuka web yang responsif dan modern
- ✅ Progress download
- ✅ Cleanup file cache

## 🚀 Cara Menjalankan

### Metode 1: Langsung (Tanpa Docker)
```bash
# Clone atau download project
cd youtube-downloader-app

# Install dependencies
pip install -r backend/requirements.txt

# Jalankan server
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload