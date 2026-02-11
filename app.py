import streamlit as st
import subprocess
import sys
import os
import re
import json
import tempfile
import time
import glob
from datetime import datetime

# ===== Page Config =====
st.set_page_config(
    page_title="🎵 MP3/MP4 Downloader",
    page_icon="🎵",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ===== Custom CSS =====
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Kanit:wght@300;400;600&display=swap');
    
    * { font-family: 'Kanit', sans-serif !important; }
    
    .stApp {
        background: linear-gradient(135deg, #0f0f0f 0%, #1a1a2e 100%);
    }
    
    .main-title {
        text-align: center;
        font-size: 2.5rem;
        font-weight: 600;
        background: linear-gradient(135deg, #6c5ce7, #a29bfe);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
    }
    
    .sub-title {
        text-align: center;
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    .download-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .status-success {
        color: #00b894;
        font-weight: 600;
    }
    
    .status-error {
        color: #d63031;
        font-weight: 600;
    }
    
    .log-entry {
        font-family: 'Consolas', monospace !important;
        font-size: 0.85rem;
        color: #888;
        padding: 2px 0;
    }
    
    /* Button styling */
    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stDownloadButton > button {
        background: linear-gradient(135deg, #00b894, #00a381) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
    }
    
    div[data-testid="stExpander"] {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 14px;
    }
</style>
""", unsafe_allow_html=True)

# ===== Constants =====
APP_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "streamlit_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)


# ===== History =====
def load_history() -> list:
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []


def save_history(history: list):
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history[-100:], f, ensure_ascii=False, indent=2)
    except Exception:
        pass


def add_history(url: str, title: str, fmt: str, status: str):
    h = load_history()
    h.append({
        "url": url, "title": title, "format": fmt,
        "status": status, "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
    })
    save_history(h)


# ===== Check dependencies =====
def check_yt_dlp() -> bool:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def check_ffmpeg() -> bool:
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.returncode == 0
    except Exception:
        return False


def get_yt_dlp_version() -> str:
    try:
        result = subprocess.run(
            [sys.executable, "-m", "yt_dlp", "--version"],
            capture_output=True, text=True, timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return "ไม่พบ"


# ===== Fetch title =====
def fetch_titles(urls: list[str]) -> list[str]:
    titles = []
    for url in urls:
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--no-download", "--print", "%(title)s",
                "--flat-playlist", url,
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=30,
                encoding="utf-8", errors="replace",
            )
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    titles.append(line.strip())
        except subprocess.TimeoutExpired:
            titles.append("(หมดเวลา)")
        except Exception as e:
            titles.append(f"(error: {e})")
    return titles


# ===== Download =====
def download_single(url: str, fmt: str, audio_quality: str, video_quality: str,
                    progress_bar, status_text, log_container):
    """Download a single URL and return (success, file_path, title)"""
    try:
        # Parse audio bitrate
        audio_br = "0"
        for br in ["320", "256", "192", "128", "96", "64"]:
            if br in audio_quality:
                audio_br = f"{br}K"
                break

        # Parse video height
        video_h = None
        if video_quality != "best":
            m = re.search(r"(\d+)p", video_quality)
            if m:
                video_h = int(m.group(1))

        # Clean download dir first
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
            try:
                os.remove(f)
            except Exception:
                pass

        template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

        cmd = [sys.executable, "-m", "yt_dlp", "--newline", "--no-playlist"]

        if fmt == "mp3":
            cmd += [
                "-x", "--audio-format", "mp3",
                "--audio-quality", audio_br,
                "--embed-thumbnail",
                "-o", template,
            ]
        else:  # mp4
            if video_h is None:
                vf = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                vf = (f"bestvideo[height<={video_h}][ext=mp4]+bestaudio[ext=m4a]"
                      f"/best[height<={video_h}]")
            cmd += ["-f", vf, "--merge-output-format", "mp4", "-o", template]
            if audio_br != "0":
                cmd += ["--postprocessor-args", f"ffmpeg:-b:a {audio_br}"]

        cmd.append(url)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            text=True, encoding="utf-8", errors="replace",
        )

        dl_title = url
        logs = []

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

            # Update progress
            pm = re.search(r"(\d+\.?\d*)%", line)
            if pm:
                pct = float(pm.group(1)) / 100.0
                progress_bar.progress(min(pct, 1.0))

                speed_match = re.search(r"(\d+\.?\d*\s*[KMG]iB/s)", line)
                eta_match = re.search(r"ETA\s+(\S+)", line)
                info = f"{pct*100:.0f}%"
                if speed_match:
                    info += f"  ·  {speed_match.group(1)}"
                if eta_match:
                    info += f"  ·  ETA {eta_match.group(1)}"
                status_text.text(info)

            # Capture title
            dest_match = re.search(r"Destination:\s*(.+)", line)
            if dest_match:
                dl_title = os.path.basename(dest_match.group(1))

            # Log important lines
            if any(k in line for k in [
                "[download]", "[ExtractAudio]", "Destination",
                "[Merger]", "[info]", "Deleting", "has already",
            ]):
                logs.append(line)
                log_container.code("\n".join(logs[-15:]), language=None)

        process.wait()

        if process.returncode == 0:
            # Find the downloaded file
            files = glob.glob(os.path.join(DOWNLOAD_DIR, f"*.{fmt}"))
            if not files:
                files = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))
            if files:
                # Get the most recently modified file
                latest = max(files, key=os.path.getmtime)
                add_history(url, dl_title, fmt, "สำเร็จ")
                return True, latest, dl_title
            else:
                add_history(url, dl_title, fmt, "ล้มเหลว - ไม่พบไฟล์")
                return False, None, dl_title
        else:
            add_history(url, url, fmt, "ล้มเหลว")
            return False, None, dl_title

    except Exception as e:
        add_history(url, url, fmt, f"ล้มเหลว: {e}")
        return False, None, str(e)


# ================================================================
# ===== UI =====
# ================================================================

# Header
st.markdown('<h1 class="main-title">🎵 Downloader</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">วาง URL เพื่อดาวน์โหลดเสียงหรือวิดีโอ</p>', unsafe_allow_html=True)

# Status bar
col_s1, col_s2 = st.columns([3, 1])
with col_s1:
    ytdlp_ok = check_yt_dlp()
    ffmpeg_ok = check_ffmpeg()
    if ytdlp_ok and ffmpeg_ok:
        st.success(f"✓ พร้อมใช้งาน  ·  yt-dlp {get_yt_dlp_version()}")
    else:
        issues = []
        if not ytdlp_ok:
            issues.append("yt-dlp ไม่พบ")
        if not ffmpeg_ok:
            issues.append("ffmpeg ไม่พบ")
        st.warning("⚠ " + " · ".join(issues))

# URL Input
st.markdown("### 📎 URL")
url_input = st.text_area(
    "วาง URL ที่นี่ (หลาย URL ได้ — บรรทัดละ 1)",
    height=100,
    placeholder="https://www.youtube.com/watch?v=...\nhttps://www.youtube.com/watch?v=...",
    label_visibility="collapsed",
)

# Settings
with st.expander("⚙️ ตั้งค่า", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        fmt = st.radio("รูปแบบ", ["mp3", "mp4"], horizontal=True)
    with col2:
        if fmt == "mp3":
            audio_q = st.selectbox("คุณภาพเสียง", [
                "best (VBR ~245kbps)", "320kbps", "256kbps",
                "192kbps", "128kbps", "96kbps", "64kbps",
            ])
            video_q = "best"
        else:
            video_q = st.selectbox("คุณภาพวิดีโอ", [
                "best", "2160p (4K)", "1440p (2K)", "1080p (Full HD)",
                "720p (HD)", "480p (SD)", "360p", "240p", "144p",
            ])
            audio_q = st.selectbox("คุณภาพเสียง", [
                "best (VBR ~245kbps)", "320kbps", "256kbps",
                "192kbps", "128kbps", "96kbps", "64kbps",
            ])

# Action Buttons
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])

with col_b1:
    fetch_clicked = st.button("🔍 ดึงชื่อ", use_container_width=True)

with col_b2:
    download_clicked = st.button("⬇️ ดาวน์โหลด", type="primary", use_container_width=True)

with col_b3:
    history_clicked = st.button("📜 ประวัติ", use_container_width=True)

# Parse URLs
urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()] if url_input else []

# Fetch Titles
if fetch_clicked:
    if not urls:
        st.warning("กรุณาใส่ URL ก่อน")
    else:
        with st.spinner("กำลังดึงชื่อ..."):
            titles = fetch_titles(urls)
        if titles:
            st.markdown("#### 📋 รายการ")
            for i, t in enumerate(titles, 1):
                st.text(f"  {i}. {t}")

# Download
if download_clicked:
    if not urls:
        st.warning("กรุณาใส่ URL ก่อน")
    else:
        st.markdown("---")
        st.markdown(f"#### ⬇️ กำลังดาวน์โหลด {len(urls)} รายการ")
        st.markdown(f"**{fmt.upper()}** · วิดีโอ: {video_q} · เสียง: {audio_q}")

        total_success = 0
        total_failed = 0
        downloaded_files = []

        for idx, url in enumerate(urls, 1):
            st.markdown(f"**▸ [{idx}/{len(urls)}]** `{url[:80]}{'...' if len(url) > 80 else ''}`")

            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.empty()

            success, file_path, title = download_single(
                url, fmt, audio_q, video_q,
                progress_bar, status_text, log_container,
            )

            if success and file_path:
                total_success += 1
                progress_bar.progress(1.0)
                status_text.markdown(f'<span class="status-success">✓ สำเร็จ: {title}</span>',
                                     unsafe_allow_html=True)
                downloaded_files.append((file_path, title))
            else:
                total_failed += 1
                status_text.markdown(f'<span class="status-error">✗ ล้มเหลว: {title}</span>',
                                     unsafe_allow_html=True)

        # Summary
        st.markdown("---")
        if total_failed == 0:
            st.success(f"🎉 ดาวน์โหลดเสร็จสิ้น — สำเร็จ {total_success} รายการ")
        else:
            st.warning(f"สำเร็จ {total_success} · ล้มเหลว {total_failed}")

        # Download buttons for each file
        if downloaded_files:
            st.markdown("#### 📥 ดาวน์โหลดไฟล์")
            for file_path, title in downloaded_files:
                try:
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    file_name = os.path.basename(file_path)
                    mime = "audio/mpeg" if fmt == "mp3" else "video/mp4"
                    st.download_button(
                        label=f"📥 {file_name}",
                        data=file_data,
                        file_name=file_name,
                        mime=mime,
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"ไม่สามารถอ่านไฟล์: {e}")

# History
if history_clicked:
    st.markdown("---")
    st.markdown("#### 📜 ประวัติดาวน์โหลด")
    history = load_history()
    if not history:
        st.info("ยังไม่มีประวัติ")
    else:
        for h in reversed(history[-30:]):
            status_icon = "✅" if h.get("status") == "สำเร็จ" else "❌"
            st.markdown(
                f"{status_icon} **{h.get('date', '')}** · "
                f"`{h.get('format', '').upper()}` · "
                f"{h.get('title', h.get('url', ''))}"
            )
    if st.button("🗑️ ล้างประวัติ"):
        save_history([])
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    '<p style="text-align:center; color:#555; font-size:0.8rem;">'
    'Made with ❤️ · Powered by yt-dlp + Streamlit'
    '</p>',
    unsafe_allow_html=True,
)
