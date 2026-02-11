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
    page_title="yt-downloader",
    page_icon="⬇",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ===== i18n =====
LANG = {
    "TH": {
        "hero_sub": "วาง URL · เลือกรูปแบบ · ดาวน์โหลด",
        "ready": "พร้อมใช้งาน",
        "not_found": "ไม่พบ",
        "url": "URL",
        "url_placeholder": "วาง URL ที่นี่  ·  หลายลิงก์ได้ (บรรทัดละ 1)",
        "settings": "ตั้งค่า",
        "format": "รูปแบบ",
        "audio_q": "คุณภาพเสียง",
        "video_q": "คุณภาพวิดีโอ",
        "playlist": "ดาวน์โหลดทั้ง Playlist",
        "size_limit": "จำกัดขนาดไฟล์",
        "fetch": "ดึงชื่อ",
        "download": "ดาวน์โหลด",
        "history": "ประวัติ",
        "no_url": "กรุณาใส่ URL ก่อน",
        "fetching": "กำลังดึงข้อมูล...",
        "list": "รายการ",
        "items": "รายการ",
        "success": "ดาวน์โหลดสำเร็จ",
        "failed": "ล้มเหลว",
        "all_success": "สำเร็จทั้งหมด",
        "no_history": "ยังไม่มีประวัติ",
        "recent": "ประวัติล่าสุด",
        "clear_history": "ล้างประวัติ",
        "cant_read": "อ่านไฟล์ไม่ได้",
        "supported": "แพลตฟอร์มที่รองรับ",
        "preview": "ตัวอย่าง",
        "unlimited": "ไม่จำกัด",
        "cookies": "อัปโหลด Cookies",
        "cookies_help": "ใช้ cookies.txt เพื่อดาวน์โหลดวิดีโอที่ต้องล็อกอิน หรือข้ามข้อจำกัดบอท",
        "cookies_loaded": "โหลด cookies แล้ว",
    },
    "EN": {
        "hero_sub": "Paste URL · Choose format · Download",
        "ready": "Ready",
        "not_found": "Not found",
        "url": "URL",
        "url_placeholder": "Paste URL here · Multiple links supported (one per line)",
        "settings": "Settings",
        "format": "Format",
        "audio_q": "Audio quality",
        "video_q": "Video quality",
        "playlist": "Download full Playlist",
        "size_limit": "File size limit",
        "fetch": "Fetch",
        "download": "Download",
        "history": "History",
        "no_url": "Please enter a URL first",
        "fetching": "Fetching info...",
        "list": "List",
        "items": "items",
        "success": "Downloaded",
        "failed": "Failed",
        "all_success": "All completed",
        "no_history": "No history yet",
        "recent": "Recent",
        "clear_history": "Clear history",
        "cant_read": "Cannot read file",
        "supported": "Supported platforms",
        "preview": "Preview",
        "unlimited": "Unlimited",
        "cookies": "Upload Cookies",
        "cookies_help": "Use cookies.txt to download login-required or bot-restricted videos",
        "cookies_loaded": "Cookies loaded",
    },
}

# ===== Session state defaults =====
if "theme" not in st.session_state:
    st.session_state.theme = "dark"
if "lang" not in st.session_state:
    st.session_state.lang = "TH"

t = LANG[st.session_state.lang]
is_dark = st.session_state.theme == "dark"

# ===== Theme colors =====
if is_dark:
    BG = "#0a0a0a"; CARD = "#111111"; BORDER = "#1e1e1e"; TEXT1 = "#e0e0e0"
    TEXT2 = "#888"; TEXT3 = "#444"; INPUT_BG = "#0e0e0e"; BTN_BG = "#111"
    BTN_TEXT = "#ccc"; PRIMARY_BG = "#fff"; PRIMARY_TEXT = "#000"
    GREEN_C = "#10b981"; APP_BG = "#0a0a0a"
else:
    BG = "#fafafa"; CARD = "#ffffff"; BORDER = "#e8e8e8"; TEXT1 = "#1a1a1a"
    TEXT2 = "#666"; TEXT3 = "#aaa"; INPUT_BG = "#f5f5f5"; BTN_BG = "#f0f0f0"
    BTN_TEXT = "#333"; PRIMARY_BG = "#111"; PRIMARY_TEXT = "#fff"
    GREEN_C = "#059669"; APP_BG = "#fafafa"


# ===== CSS =====
st.markdown(f"""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Kanit:wght@200;300;400;500;600&display=swap" rel="stylesheet">

<style>
    /* ── Font ── */
    *, html, body, [class*="st-"], .stMarkdown, .stTextArea textarea,
    .stSelectbox, .stRadio, .stButton button, .stCheckbox, input, select, textarea,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] div {{
        font-family: 'Kanit', sans-serif !important;
    }}

    .stApp {{ background: {APP_BG}; }}
    section[data-testid="stSidebar"] {{ display: none; }}

    .block-container {{
        max-width: 640px !important;
        padding: 2rem 1.2rem 3rem !important;
    }}
    @media (max-width: 640px) {{
        .block-container {{ padding: 1rem 0.7rem 2rem !important; }}
    }}

    /* ── Hero ── */
    .hero {{ text-align: center; padding: 1.8rem 0 0.6rem; }}
    .hero h1 {{
        font-family: 'Kanit', sans-serif !important;
        font-weight: 500; font-size: 1.6rem;
        color: {TEXT1}; letter-spacing: -0.02em; margin: 0;
    }}
    .hero p {{
        font-family: 'Kanit', sans-serif !important;
        font-weight: 300; color: {TEXT3}; font-size: 0.85rem; margin-top: 0.2rem;
    }}

    /* ── Top bar ── */
    .topbar {{
        display: flex; justify-content: center; gap: 0.5rem;
        margin-bottom: 0.8rem; flex-wrap: wrap;
    }}
    .topbar-btn {{
        font-family: 'Kanit', sans-serif !important;
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 6px;
        padding: 0.2rem 0.6rem; font-size: 0.7rem; color: {TEXT2};
        cursor: pointer; transition: all 0.15s ease; text-decoration: none;
    }}
    .topbar-btn:hover {{ border-color: {TEXT2}; color: {TEXT1}; }}

    /* ── Card ── */
    .card {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px;
        padding: 1.2rem 1.4rem; margin-bottom: 0.8rem;
    }}
    .card-label {{
        font-family: 'Kanit', sans-serif !important;
        font-weight: 400; font-size: 0.7rem; text-transform: uppercase;
        letter-spacing: 0.08em; color: {TEXT3}; margin-bottom: 0.5rem;
    }}

    /* ── Pill ── */
    .pill {{
        display: inline-block; font-family: 'Kanit', sans-serif !important;
        font-size: 0.7rem; font-weight: 400; padding: 0.15rem 0.6rem;
        border-radius: 20px; margin-bottom: 0.5rem;
    }}
    .pill-ok {{
        background: rgba(16,185,129,0.1); color: {GREEN_C};
        border: 1px solid rgba(16,185,129,0.2);
    }}
    .pill-warn {{
        background: rgba(245,158,11,0.1); color: #f59e0b;
        border: 1px solid rgba(245,158,11,0.2);
    }}

    /* ── Platforms ── */
    .platforms {{
        display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.4rem;
    }}
    .plat-tag {{
        font-family: 'Kanit', sans-serif !important;
        font-size: 0.65rem; padding: 0.12rem 0.5rem; border-radius: 4px;
        background: {"#0e0e0e" if is_dark else "#f0f0f0"};
        color: {TEXT2}; border: 1px solid {BORDER};
    }}

    /* ── Thumbnail ── */
    .thumb-card {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 12px;
        overflow: hidden; margin-bottom: 0.8rem;
    }}
    .thumb-card img {{
        width: 100%; height: auto; display: block;
    }}
    .thumb-info {{
        padding: 0.8rem 1rem;
    }}
    .thumb-title {{
        font-family: 'Kanit', sans-serif !important;
        color: {TEXT1}; font-size: 0.9rem; font-weight: 400;
    }}
    .thumb-meta {{
        font-family: 'Kanit', sans-serif !important;
        color: {TEXT3}; font-size: 0.72rem; margin-top: 0.15rem;
    }}

    /* ── Inputs ── */
    .stTextArea textarea {{
        background: {INPUT_BG} !important; border: 1px solid {BORDER} !important;
        border-radius: 10px !important; color: {TEXT1} !important;
        font-size: 0.88rem !important;
    }}
    .stTextArea textarea:focus {{ border-color: {TEXT2} !important; box-shadow: none !important; }}
    .stTextArea label {{ display: none !important; }}

    .stSelectbox [data-baseweb="select"] > div {{
        background: {INPUT_BG} !important; border: 1px solid {BORDER} !important;
        border-radius: 8px !important;
    }}
    .stCheckbox label span {{
        color: {TEXT2} !important; font-size: 0.85rem !important;
    }}

    /* ── Buttons ── */
    .stButton > button {{
        font-family: 'Kanit', sans-serif !important; font-weight: 400;
        border-radius: 8px; border: 1px solid {BORDER};
        background: {BTN_BG} !important; color: {BTN_TEXT} !important;
        transition: all 0.15s ease; font-size: 0.85rem;
    }}
    .stButton > button:hover {{
        border-color: {TEXT2} !important; color: {TEXT1} !important;
    }}
    button[data-testid="stBaseButton-primary"] {{
        background: {PRIMARY_BG} !important; color: {PRIMARY_TEXT} !important;
        border: none !important; font-weight: 500 !important;
    }}
    button[data-testid="stBaseButton-primary"]:hover {{
        opacity: 0.85;
    }}
    .stDownloadButton > button {{
        background: {CARD} !important; color: {GREEN_C} !important;
        border: 1px solid {"rgba(16,185,129,0.2)" if is_dark else "rgba(5,150,105,0.3)"} !important;
        border-radius: 8px !important; font-weight: 400 !important;
        font-family: 'Kanit', sans-serif !important;
    }}
    .stDownloadButton > button:hover {{
        background: {"rgba(16,185,129,0.06)" if is_dark else "rgba(5,150,105,0.06)"} !important;
    }}

    /* ── Expander ── */
    div[data-testid="stExpander"] {{
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px;
    }}
    div[data-testid="stExpander"] summary {{ font-size: 0.82rem; color: {TEXT2}; }}

    /* ── Progress ── */
    .stProgress > div > div {{ background: {BORDER} !important; border-radius: 4px; }}
    .stProgress > div > div > div {{ background: {TEXT1} !important; border-radius: 4px; }}

    /* ── Alerts ── */
    .stAlert, div[data-testid="stAlert"] {{
        background: {CARD} !important; border: 1px solid {BORDER} !important;
        border-radius: 10px !important; font-size: 0.82rem;
    }}

    hr {{ border-color: {BORDER} !important; }}

    /* ── Results ── */
    .result-item {{
        font-family: 'Kanit', sans-serif !important;
        background: {CARD}; border: 1px solid {BORDER}; border-radius: 10px;
        padding: 0.8rem 1rem; margin: 0.4rem 0; font-size: 0.85rem;
    }}
    .result-ok {{ border-left: 3px solid {GREEN_C}; }}
    .result-fail {{ border-left: 3px solid #ef4444; }}
    .result-item .r-title {{ color: {TEXT1}; font-weight: 400; }}
    .result-item .r-sub {{ color: {TEXT3}; font-size: 0.72rem; margin-top: 0.1rem; }}

    /* ── History ── */
    .hist-item {{
        font-family: 'Kanit', sans-serif !important;
        display: flex; justify-content: space-between; align-items: center;
        padding: 0.5rem 0; border-bottom: 1px solid {"#141414" if is_dark else "#f0f0f0"};
        font-size: 0.8rem;
    }}
    .hist-item:last-child {{ border-bottom: none; }}
    .hist-title {{ color: {"#aaa" if is_dark else "#555"}; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }}
    .hist-meta {{ color: {TEXT3}; font-size: 0.68rem; text-align: right; white-space: nowrap; margin-left: 0.6rem; }}

    .footer {{
        text-align: center; color: {TEXT3}; font-size: 0.68rem;
        padding: 2rem 0 1rem; letter-spacing: 0.03em;
    }}

    #MainMenu, footer, header {{ visibility: hidden; }}
</style>
""", unsafe_allow_html=True)

# ===== Constants =====
APP_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(APP_DIR, "history.json")
DOWNLOAD_DIR = os.path.join(tempfile.gettempdir(), "streamlit_downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

SUPPORTED_PLATFORMS = [
    "YouTube", "YouTube Music", "TikTok", "Facebook", "Instagram",
    "X (Twitter)", "Reddit", "SoundCloud", "Vimeo", "Dailymotion",
    "Bilibili", "Twitch", "Bandcamp", "Spotify*",
]

SIZE_LIMITS = {
    "ไม่จำกัด": None, "Unlimited": None,
    "50 MB": 50, "100 MB": 100, "200 MB": 200, "500 MB": 500,
}


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
        return "?"


# ===== Fetch info (title + thumbnail) =====
def fetch_video_info(urls: list[str], cookies_path: str | None = None) -> list[dict]:
    """Return list of {title, thumbnail, duration, url}"""
    results = []
    for url in urls:
        try:
            cmd = [
                sys.executable, "-m", "yt_dlp",
                "--no-download", "--flat-playlist",
                "--print", "%(title)s\t%(thumbnail)s\t%(duration_string)s",
            ]
            if cookies_path and os.path.exists(cookies_path):
                cmd += ["--cookies", cookies_path]
            cmd.append(url)
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=45,
                encoding="utf-8", errors="replace",
            )
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    parts = line.strip().split("\t")
                    title = parts[0] if len(parts) > 0 else "?"
                    thumb = parts[1] if len(parts) > 1 and parts[1] != "NA" else ""
                    dur = parts[2] if len(parts) > 2 and parts[2] != "NA" else ""
                    results.append({
                        "title": title, "thumbnail": thumb,
                        "duration": dur, "url": url,
                    })
        except subprocess.TimeoutExpired:
            results.append({"title": "(timeout)", "thumbnail": "", "duration": "", "url": url})
        except Exception as e:
            results.append({"title": f"(error: {e})", "thumbnail": "", "duration": "", "url": url})
    return results


# ===== Download =====
def download_single(url: str, fmt: str, audio_quality: str, video_quality: str,
                    allow_playlist: bool, max_size_mb: int | None,
                    progress_bar, status_text, log_container,
                    cookies_path: str | None = None):
    """Download a single URL and return (success, file_path, title)"""
    try:
        audio_br = "0"
        for br in ["320", "256", "192", "128", "96", "64"]:
            if br in audio_quality:
                audio_br = f"{br}K"
                break

        video_h = None
        if video_quality != "best":
            m = re.search(r"(\d+)p", video_quality)
            if m:
                video_h = int(m.group(1))

        # Clean download dir
        for f in glob.glob(os.path.join(DOWNLOAD_DIR, "*")):
            try:
                os.remove(f)
            except Exception:
                pass

        template = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")
        cmd = [sys.executable, "-m", "yt_dlp", "--newline",
               "--no-cache-dir",
               "--extractor-args", "youtube:player_client=android,web",
               "--user-agent", "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
               ]

        # ใส่ cookies ถ้ามี
        if cookies_path and os.path.exists(cookies_path):
            cmd += ["--cookies", cookies_path]

        if not allow_playlist:
            cmd.append("--no-playlist")

        if fmt == "mp3":
            # --max-filesize doesn't work with -x, skip it for audio
            cmd += [
                "-x", "--audio-format", "mp3",
                "--audio-quality", audio_br,
                "--embed-thumbnail",
                "--convert-thumbnails", "jpg",
                "-o", template,
            ]
        else:
            if video_h is None:
                vf = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
            else:
                vf = (f"bestvideo[height<={video_h}][ext=mp4]+bestaudio[ext=m4a]"
                      f"/best[height<={video_h}]")
            cmd += ["-f", vf, "--merge-output-format", "mp4", "-o", template]
            if max_size_mb:
                cmd += ["--max-filesize", f"{max_size_mb}M"]
            if audio_br != "0":
                cmd += ["--postprocessor-args", f"ffmpeg:-b:a {audio_br}"]

        cmd.append(url)

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            text=True, encoding="utf-8", errors="replace",
        )

        dl_title = url
        logs = []

        for line in process.stdout:
            line = line.strip()
            if not line:
                continue

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

            dest_match = re.search(r"Destination:\s*(.+)", line)
            if dest_match:
                dl_title = os.path.basename(dest_match.group(1))

            if any(k in line for k in [
                "[download]", "[ExtractAudio]", "Destination",
                "[Merger]", "[info]", "Deleting", "has already",
                "ERROR", "error", "WARNING", "File is larger",
            ]):
                logs.append(line)
                log_container.code("\n".join(logs[-12:]), language=None)

        process.wait()

        # Capture stderr for error info
        stderr_output = process.stderr.read().strip() if process.stderr else ""
        if stderr_output and process.returncode != 0:
            logs.append(f"STDERR: {stderr_output[:300]}")
            log_container.code("\n".join(logs[-12:]), language=None)

        if process.returncode == 0:
            files = glob.glob(os.path.join(DOWNLOAD_DIR, f"*.{fmt}"))
            if not files:
                files = glob.glob(os.path.join(DOWNLOAD_DIR, "*"))
            if files:
                latest = max(files, key=os.path.getmtime)
                add_history(url, dl_title, fmt, "สำเร็จ")
                return True, latest, dl_title
            else:
                add_history(url, dl_title, fmt, "ล้มเหลว")
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

# ── Hero ──
st.markdown(f"""
<div class="hero">
    <h1>⬇ yt-downloader</h1>
    <p>{t["hero_sub"]}</p>
</div>
""", unsafe_allow_html=True)

# ── Top bar: Theme + Language ──
top_col1, top_col2, top_col3 = st.columns([1, 4, 1])
with top_col1:
    if st.button("☀" if is_dark else "☾", key="theme_toggle", use_container_width=True):
        st.session_state.theme = "light" if is_dark else "dark"
        st.rerun()
with top_col3:
    if st.button("EN" if st.session_state.lang == "TH" else "TH", key="lang_toggle", use_container_width=True):
        st.session_state.lang = "EN" if st.session_state.lang == "TH" else "TH"
        st.rerun()

# ── Status ──
ytdlp_ok = check_yt_dlp()
ffmpeg_ok = check_ffmpeg()
if ytdlp_ok and ffmpeg_ok:
    ver = get_yt_dlp_version()
    st.markdown(f'<span class="pill pill-ok">{t["ready"]} · yt-dlp {ver}</span>', unsafe_allow_html=True)
else:
    issues = []
    if not ytdlp_ok:
        issues.append("yt-dlp")
    if not ffmpeg_ok:
        issues.append("ffmpeg")
    st.markdown(f'<span class="pill pill-warn">{t["not_found"]} {" · ".join(issues)}</span>', unsafe_allow_html=True)

# ── Supported platforms ──
with st.expander(f"🌐 {t['supported']}"):
    tags_html = "".join(f'<span class="plat-tag">{p}</span>' for p in SUPPORTED_PLATFORMS)
    st.markdown(f'<div class="platforms">{tags_html}</div>', unsafe_allow_html=True)
    st.caption("*Spotify = metadata only (yt-dlp limitation)")

# ── URL Input ──
st.markdown(f'<div class="card"><div class="card-label">{t["url"]}</div>', unsafe_allow_html=True)
url_input = st.text_area(
    "url_input",
    height=90,
    placeholder=t["url_placeholder"],
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Settings ──
st.markdown(f'<div class="card"><div class="card-label">{t["settings"]}</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    fmt = st.radio(t["format"], ["mp3", "mp4"], horizontal=True, label_visibility="collapsed")
with col2:
    if fmt == "mp3":
        audio_q = st.selectbox(t["audio_q"], [
            "best (VBR ~245kbps)", "320kbps", "256kbps",
            "192kbps", "128kbps", "96kbps", "64kbps",
        ])
        video_q = "best"
    else:
        video_q = st.selectbox(t["video_q"], [
            "best", "1080p (Full HD)", "720p (HD)", "480p (SD)", "360p",
        ])
        audio_q = st.selectbox(t["audio_q"], [
            "best (VBR ~245kbps)", "320kbps", "256kbps",
            "192kbps", "128kbps", "96kbps", "64kbps",
        ])

opt_col1, opt_col2 = st.columns(2)
with opt_col1:
    allow_playlist = st.checkbox(t["playlist"], value=False)
with opt_col2:
    limit_label = t["unlimited"] if st.session_state.lang == "TH" else "Unlimited"
    size_options = [limit_label, "50 MB", "100 MB", "200 MB", "500 MB"]
    size_limit_str = st.selectbox(t["size_limit"], size_options, label_visibility="visible")
    max_size_mb = SIZE_LIMITS.get(size_limit_str)
st.markdown('</div>', unsafe_allow_html=True)

# ── Cookies Upload (ช่วย bypass login / bot detection) ──
cookies_path = None
with st.expander(f"🍪 {t['cookies']}"):
    st.caption(t["cookies_help"])
    cookies_file = st.file_uploader(
        "cookies.txt", type=["txt"], label_visibility="collapsed",
    )
    if cookies_file is not None:
        cookies_path = os.path.join(tempfile.gettempdir(), "yt_cookies.txt")
        with open(cookies_path, "wb") as cf:
            cf.write(cookies_file.getvalue())
        st.markdown(f'<span class="pill pill-ok">{t["cookies_loaded"]}</span>', unsafe_allow_html=True)

# ── Action Buttons ──
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b1:
    fetch_clicked = st.button(t["fetch"], use_container_width=True)
with col_b2:
    download_clicked = st.button(t["download"], type="primary", use_container_width=True)
with col_b3:
    history_clicked = st.button(t["history"], use_container_width=True)

# ── Parse URLs ──
urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()] if url_input else []

# ── Fetch Info + Thumbnail ──
if fetch_clicked:
    if not urls:
        st.warning(t["no_url"])
    else:
        with st.spinner(t["fetching"]):
            infos = fetch_video_info(urls, cookies_path=cookies_path)
        if infos:
            st.markdown(f'<div class="card"><div class="card-label">{t["list"]} — {len(infos)} {t["items"]}</div>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            for info in infos:
                thumb_html = ""
                if info["thumbnail"]:
                    thumb_html = f'<img src="{info["thumbnail"]}" alt="thumbnail">'
                dur_str = f' · {info["duration"]}' if info["duration"] else ""
                st.markdown(
                    f'<div class="thumb-card">'
                    f'{thumb_html}'
                    f'<div class="thumb-info">'
                    f'<div class="thumb-title">{info["title"]}</div>'
                    f'<div class="thumb-meta">{info["url"][:60]}{dur_str}</div>'
                    f'</div></div>',
                    unsafe_allow_html=True,
                )

# ── Download ──
if download_clicked:
    if not urls:
        st.warning(t["no_url"])
    else:
        st.markdown("---")
        st.markdown(
            f'<div style="color:{TEXT2};font-size:0.8rem;margin-bottom:0.6rem;">'
            f'{fmt.upper()} · {len(urls)} {t["items"]} · {audio_q}'
            f'{"" if fmt == "mp3" else f" · {video_q}"}'
            f'{f" · max {size_limit_str}" if max_size_mb else ""}'
            f'</div>',
            unsafe_allow_html=True,
        )

        total_success = 0
        total_failed = 0
        downloaded_files = []

        for idx, url in enumerate(urls, 1):
            st.markdown(
                f'<div style="color:{TEXT3};font-size:0.78rem;margin-top:0.4rem;">'
                f'[{idx}/{len(urls)}] {url[:65]}{"..." if len(url) > 65 else ""}</div>',
                unsafe_allow_html=True,
            )

            progress_bar = st.progress(0)
            status_text = st.empty()
            log_container = st.empty()

            success, file_path, title = download_single(
                url, fmt, audio_q, video_q,
                allow_playlist, max_size_mb,
                progress_bar, status_text, log_container,
                cookies_path=cookies_path,
            )

            if success and file_path:
                total_success += 1
                progress_bar.progress(1.0)
                status_text.markdown(
                    f'<div class="result-item result-ok">'
                    f'<div class="r-title">{title}</div>'
                    f'<div class="r-sub">{t["success"]}</div></div>',
                    unsafe_allow_html=True,
                )
                downloaded_files.append((file_path, title))
            else:
                total_failed += 1
                status_text.markdown(
                    f'<div class="result-item result-fail">'
                    f'<div class="r-title">{title}</div>'
                    f'<div class="r-sub">{t["failed"]}</div></div>',
                    unsafe_allow_html=True,
                )

        # Summary
        st.markdown("---")
        if total_failed == 0:
            st.success(f"{t['all_success']} {total_success} {t['items']}")
        else:
            st.warning(f"{t['success']} {total_success} · {t['failed']} {total_failed}")

        # Download buttons
        if downloaded_files:
            for file_path, title in downloaded_files:
                try:
                    with open(file_path, "rb") as f:
                        file_data = f.read()
                    file_name = os.path.basename(file_path)
                    mime = "audio/mpeg" if fmt == "mp3" else "video/mp4"
                    st.download_button(
                        label=f"↓  {file_name}",
                        data=file_data,
                        file_name=file_name,
                        mime=mime,
                        use_container_width=True,
                    )
                except Exception as e:
                    st.error(f"{t['cant_read']}: {e}")

# ── History ──
if history_clicked:
    st.markdown("---")
    history = load_history()
    if not history:
        st.info(t["no_history"])
    else:
        st.markdown(f'<div class="card"><div class="card-label">{t["recent"]}</div>', unsafe_allow_html=True)
        for h in reversed(history[-20:]):
            icon = "●" if h.get("status") == "สำเร็จ" else "○"
            color = GREEN_C if h.get("status") == "สำเร็จ" else TEXT3
            title_text = h.get("title", h.get("url", ""))
            if len(title_text) > 50:
                title_text = title_text[:50] + "…"
            st.markdown(
                f'<div class="hist-item">'
                f'<span style="color:{color};margin-right:0.5rem;">{icon}</span>'
                f'<span class="hist-title">{title_text}</span>'
                f'<span class="hist-meta">{h.get("format","").upper()} · {h.get("date","")}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
    if st.button(t["clear_history"], use_container_width=False):
        save_history([])
        st.rerun()

# ── Footer ──
st.markdown(
    '<div class="footer">yt-downloader · yt-dlp + streamlit</div>',
    unsafe_allow_html=True,
)
