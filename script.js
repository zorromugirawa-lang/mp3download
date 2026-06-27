// Konfigurasi
const API_BASE = window.location.protocol + "//" + window.location.hostname + ":8000";

// DOM Elements
const urlInput = document.getElementById('urlInput');
const fetchBtn = document.getElementById('fetchBtn');
const loading = document.getElementById('loading');
const errorMessage = document.getElementById('errorMessage');
const videoInfo = document.getElementById('videoInfo');
const thumbnail = document.getElementById('thumbnail');
const videoTitle = document.getElementById('videoTitle');
const videoAuthor = document.getElementById('videoAuthor');
const videoStats = document.getElementById('videoStats');
const videoDescription = document.getElementById('videoDescription');
const videoStreams = document.getElementById('videoStreams');
const audioStreams = document.getElementById('audioStreams');
const tabBtns = document.querySelectorAll('.tab-btn');

// Event Listeners
fetchBtn.addEventListener('click', fetchVideoInfo);
urlInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') fetchVideoInfo();
});

tabBtns.forEach(btn => {
    btn.addEventListener('click', function() {
        tabBtns.forEach(b => b.classList.remove('active'));
        this.classList.add('active');
        
        const tab = this.dataset.tab;
        if (tab === 'video') {
            videoStreams.classList.remove('hidden');
            audioStreams.classList.add('hidden');
        } else {
            videoStreams.classList.add('hidden');
            audioStreams.classList.remove('hidden');
        }
    });
});

// ============== FUNCTIONS ==============

async function fetchVideoInfo() {
    const url = urlInput.value.trim();
    if (!url) {
        showError('Silakan masukkan URL YouTube terlebih dahulu!');
        return;
    }

    if (!isValidYouTubeUrl(url)) {
        showError('URL tidak valid! Pastikan URL adalah link YouTube yang benar.');
        return;
    }

    showLoading(true);
    hideError();
    hideVideoInfo();

    try {
        const response = await fetch(`${API_BASE}/info?url=${encodeURIComponent(url)}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Gagal mengambil informasi video');
        }

        const data = await response.json();
        displayVideoInfo(data, url);
        
    } catch (error) {
        showError(error.message || 'Terjadi kesalahan. Silakan coba lagi.');
        console.error('Error:', error);
    } finally {
        showLoading(false);
    }
}

function isValidYouTubeUrl(url) {
    const patterns = [
        /(?:youtube\.com\/watch\?v=)/,
        /(?:youtu\.be\/)/,
        /(?:youtube\.com\/embed\/)/,
        /(?:youtube\.com\/v\/)/
    ];
    return patterns.some(pattern => pattern.test(url));
}

function displayVideoInfo(data, url) {
    // Meta
    thumbnail.src = data.thumbnail_url || '';
    videoTitle.textContent = data.title || 'Tidak ada judul';
    videoAuthor.textContent = `👤 ${data.author || 'Unknown'}`;
    videoStats.textContent = `⏱️ ${formatDuration(data.length)} • 👁️ ${formatNumber(data.views)} views`;
    videoDescription.textContent = data.description || '';

    // Video Streams
    videoStreams.innerHTML = '';
    if (data.video_streams && data.video_streams.length > 0) {
        data.video_streams.forEach(stream => {
            const item = createStreamItem(
                stream.resolution || 'Unknown',
                stream.filesize_mb || 0,
                'video',
                url,
                stream.resolution
            );
            videoStreams.appendChild(item);
        });
    } else {
        videoStreams.innerHTML = '<p class="no-stream">Tidak ada stream video tersedia</p>';
    }

    // Audio Streams
    audioStreams.innerHTML = '';
    if (data.audio_streams && data.audio_streams.length > 0) {
        data.audio_streams.forEach(stream => {
            const item = createStreamItem(
                stream.abr || 'Audio',
                stream.filesize_mb || 0,
                'audio',
                url
            );
            audioStreams.appendChild(item);
        });
    } else {
        audioStreams.innerHTML = '<p class="no-stream">Tidak ada stream audio tersedia</p>';
    }

    videoInfo.classList.remove('hidden');
}

function createStreamItem(label, sizeMB, type, url, quality = null) {
    const div = document.createElement('div');
    div.className = 'stream-item';
    
    const labelSpan = document.createElement('div');
    labelSpan.className = 'quality-label';
    labelSpan.textContent = label;
    
    const sizeCol = document.createElement('div');
    sizeCol.className = 'size-col';
    
    const sizeNum = document.createElement('span');
    sizeNum.className = 'size-num';
    sizeNum.textContent = sizeMB.toFixed(2);
    
    const sizeUnit = document.createElement('span');
    sizeUnit.className = 'size-unit';
    sizeUnit.textContent = 'MB';
    
    sizeCol.appendChild(sizeNum);
    sizeCol.appendChild(sizeUnit);
    
    const downloadBtn = document.createElement('button');
    downloadBtn.className = 'btn btn-download';
    downloadBtn.innerHTML = '⬇<br>Download';
    
    downloadBtn.addEventListener('click', () => {
        let downloadUrl;
        if (type === 'video') {
            downloadUrl = `${API_BASE}/download/video?url=${encodeURIComponent(url)}&quality=${quality}`;
        } else {
            downloadUrl = `${API_BASE}/download/audio?url=${encodeURIComponent(url)}`;
        }
        window.open(downloadUrl, '_blank');
    });
    
    div.appendChild(labelSpan);
    div.appendChild(sizeCol);
    div.appendChild(downloadBtn);
    
    return div;
}

function formatDuration(seconds) {
    if (!seconds) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

function formatNumber(num) {
    if (!num) return '0';
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
}

// ============== UI HELPERS ==============

function showLoading(show) {
    if (show) {
        loading.classList.remove('hidden');
    } else {
        loading.classList.add('hidden');
    }
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.classList.remove('hidden');
}

function hideError() {
    errorMessage.classList.add('hidden');
    errorMessage.textContent = '';
}

function hideVideoInfo() {
    videoInfo.classList.add('hidden');
}

// ============== CLEANUP ==============

async function cleanupFiles() {
    if (!confirm('Hapus semua file download yang tersimpan?')) return;
    
    try {
        const response = await fetch(`${API_BASE}/cleanup`, {
            method: 'DELETE'
        });
        
        if (response.ok) {
            alert('✅ File cache berhasil dibersihkan!');
        } else {
            alert('❌ Gagal membersihkan file');
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

// ============== KEYBOARD SHORTCUT ==============

document.addEventListener('keydown', (e) => {
    // Ctrl+Enter untuk fetch
    if (e.ctrlKey && e.key === 'Enter') {
        fetchVideoInfo();
    }
});

console.log('🎬 YouTube Downloader loaded successfully!');
console.log(`API Base: ${API_BASE}`);