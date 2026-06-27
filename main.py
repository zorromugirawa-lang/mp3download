from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv
from downloader import YouTubeDownloader
from models import VideoInfo, DownloadRequest, DownloadResponse
from utils import format_filesize

load_dotenv()

app = FastAPI(
    title=os.getenv("APP_NAME", "YouTube Downloader API"),
    version=os.getenv("APP_VERSION", "1.0.0")
)

# CORS
origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:8000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inisialisasi downloader
DOWNLOAD_DIR = os.getenv("DOWNLOAD_DIR", "downloads")
downloader = YouTubeDownloader(DOWNLOAD_DIR)

# Buat folder downloads jika belum ada
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Mount folder static untuk frontend
frontend_path = os.path.dirname(__file__)
if os.path.exists(os.path.join(frontend_path, "index.html")):
    app.mount("/frontend", StaticFiles(directory=frontend_path, html=True), name="frontend")

# ============== ENDPOINTS ==============

from fastapi.responses import RedirectResponse

@app.get("/")
async def root():
    # Langsung arahkan ke halaman frontend
    return RedirectResponse(url="/frontend/index.html")

@app.get("/health")
async def health():
    return {"status": "healthy", "download_dir": DOWNLOAD_DIR}

@app.get("/info")
async def get_info(url: str = Query(..., description="YouTube URL")):
    """
    Mendapatkan informasi detail video
    """
    try:
        info = downloader.get_video_info(url)
        return info
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/download/video")
async def download_video(
    url: str = Query(..., description="YouTube URL"),
    quality: str = Query("highest", description="Kualitas: 1080p, 720p, 480p, 360p, atau 'highest'"),
    filename: str = Query(None, description="Nama file custom")
):
    """
    Download video dengan kualitas yang dipilih
    """
    try:
        result = downloader.download_video(url, quality, filename)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        # Kirim file
        return FileResponse(
            path=result["path"],
            media_type="video/mp4",
            filename=result["filename"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.get("/download/audio")
async def download_audio(
    url: str = Query(..., description="YouTube URL"),
    filename: str = Query(None, description="Nama file custom")
):
    """
    Download audio saja
    """
    try:
        result = downloader.download_audio(url, filename)
        
        if not result["success"]:
            raise HTTPException(status_code=400, detail=result["message"])
        
        return FileResponse(
            path=result["path"],
            media_type="audio/mp4",
            filename=result["filename"]
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

@app.delete("/cleanup")
async def cleanup():
    """
    Hapus semua file di folder downloads
    """
    try:
        count = 0
        for file in os.listdir(DOWNLOAD_DIR):
            file_path = os.path.join(DOWNLOAD_DIR, file)
            if os.path.isfile(file_path):
                os.remove(file_path)
                count += 1
        return {"success": True, "message": f"{count} file dihapus"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )