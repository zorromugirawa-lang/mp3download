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
    # Sajikan index.html secara langsung tanpa redirect
    return FileResponse(os.path.join(frontend_path, "index.html"))

@app.get("/BingSiteAuth.xml")
async def bing_site_auth():
    return FileResponse(os.path.join(frontend_path, "BingSiteAuth.xml"), media_type="application/xml")

@app.get("/style.css")
async def style_css():
    return FileResponse(os.path.join(frontend_path, "style.css"))

@app.get("/script.js")
async def script_js():
    return FileResponse(os.path.join(frontend_path, "script.js"))

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


@app.get("/download/audio")
async def download_audio(
    url: str = Query(..., description="YouTube URL")
):
    """
    Mengarahkan (redirect) pengguna langsung ke link RapidAPI
    """
    try:
        info = downloader.get_video_info(url)
        
        if not info.get("audio_streams"):
            raise HTTPException(status_code=400, detail="Audio tidak ditemukan")
            
        link = info["audio_streams"][0].get("link")
        if not link:
            raise HTTPException(status_code=400, detail="Link download tidak valid")
            
        return RedirectResponse(url=link)
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
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )