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

# ===== Minimal CSS with Kanit =====
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Kanit:wght@200;300;400;500;600&display=swap" rel="stylesheet">

<style>
    /* ── Global Font ── */
    *, html, body, [class*="st-"], .stMarkdown, .stTextArea textarea,
    .stSelectbox, .stRadio, .stButton button, input, select, textarea,
    div[data-testid="stExpander"] summary span,
    div[data-testid="stExpander"] div {
        font-family: 'Kanit', sans-serif !important;
    }

    /* ── Background ── */
    .stApp {
        background: #0a0a0a;
    }
    section[data-testid="stSidebar"] { display: none; }

    /* ── Container max-width for responsive ── */
    .block-container {
        max-width: 640px !important;
        padding: 2rem 1.2rem 3rem !important;
    }
    @media (max-width: 640px) {
        .block-container { padding: 1.2rem 0.8rem 2rem !important; }
    }

    /* ── Hero ── */
    .hero {
        text-align: center;
        padding: 2.5rem 0 1rem;
    }
    .hero-icon {
        font-size: 2.4rem;
        margin-bottom: 0.3rem;
        opacity: 0.9;
    }
    .hero h1 {
        font-family: 'Kanit', sans-serif !important;
        font-weight: 500;
        font-size: 1.75rem;
        color: #ffffff;
        letter-spacing: -0.02em;
        margin: 0;
    }
    .hero p {
        font-family: 'Kanit', sans-serif !important;
        font-weight: 300;
        color: #555;
        font-size: 0.9rem;
        margin-top: 0.3rem;
    }

    /* ── Cards ── */
    .card {
        background: #111111;
        border: 1px solid #1e1e1e;
        border-radius: 12px;
        padding: 1.2rem 1.4rem;
        margin-bottom: 0.8rem;
    }
    .card-label {
        font-family: 'Kanit', sans-serif !important;
        font-weight: 400;
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #444;
        margin-bottom: 0.5rem;
    }

    /* ── Status pill ── */
    .pill {
        display: inline-block;
        font-family: 'Kanit', sans-serif !important;
        font-size: 0.72rem;
        font-weight: 400;
        padding: 0.2rem 0.7rem;
        border-radius: 20px;
        margin-bottom: 0.6rem;
    }
    .pill-ok {
        background: rgba(16, 185, 129, 0.12);
        color: #10b981;
        border: 1px solid rgba(16, 185, 129, 0.2);
    }
    .pill-warn {
        background: rgba(245, 158, 11, 0.12);
        color: #f59e0b;
        border: 1px solid rgba(245, 158, 11, 0.2);
    }

    /* ── Inputs ── */
    .stTextArea textarea {
        background: #0e0e0e !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 10px !important;
        color: #e0e0e0 !important;
        font-size: 0.88rem !important;
        transition: border-color 0.2s ease;
    }
    .stTextArea textarea:focus {
        border-color: #333 !important;
        box-shadow: none !important;
    }
    .stTextArea label { display: none !important; }

    /* ── Select / Radio ── */
    .stSelectbox > div > div,
    .stRadio > div {
        background: transparent !important;
    }
    .stSelectbox [data-baseweb="select"] > div {
        background: #0e0e0e !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 8px !important;
    }

    /* ── Buttons ── */
    .stButton > button {
        font-family: 'Kanit', sans-serif !important;
        font-weight: 400;
        border-radius: 8px;
        border: 1px solid #1e1e1e;
        background: #111 !important;
        color: #ccc !important;
        transition: all 0.2s ease;
        font-size: 0.88rem;
    }
    .stButton > button:hover {
        background: #1a1a1a !important;
        border-color: #333 !important;
        color: #fff !important;
    }
    .stButton > button[kind="primary"],
    button[data-testid="stBaseButton-primary"] {
        background: #fff !important;
        color: #000 !important;
        border: none !important;
        font-weight: 500 !important;
    }
    button[data-testid="stBaseButton-primary"]:hover {
        background: #e0e0e0 !important;
    }

    /* ── Download button ── */
    .stDownloadButton > button {
        background: #111 !important;
        color: #10b981 !important;
        border: 1px solid rgba(16, 185, 129, 0.25) !important;
        border-radius: 8px !important;
        font-weight: 400 !important;
        font-family: 'Kanit', sans-serif !important;
    }
    .stDownloadButton > button:hover {
        background: rgba(16, 185, 129, 0.08) !important;
        border-color: #10b981 !important;
    }

    /* ── Expander ── */
    div[data-testid="stExpander"] {
        background: #111;
        border: 1px solid #1e1e1e;
        border-radius: 10px;
    }
    div[data-testid="stExpander"] summary {
        font-size: 0.85rem;
        color: #888;
    }

    /* ── Progress bar ── */
    .stProgress > div > div {
        background: #1e1e1e !important;
        border-radius: 4px;
    }
    .stProgress > div > div > div {
        background: #fff !important;
        border-radius: 4px;
    }

    /* ── Alerts ── */
    .stAlert, div[data-testid="stAlert"] {
        background: #111 !important;
        border: 1px solid #1e1e1e !important;
        border-radius: 10px !important;
        font-size: 0.85rem;
    }

    /* ── Divider ── */
    hr { border-color: #1a1a1a !important; }

    /* ── Results ── */
    .result-item {
        font-family: 'Kanit', sans-serif !important;
        background: #111;
        border: 1px solid #1e1e1e;
        border-radius: 10px;
        padding: 0.8rem 1rem;
        margin: 0.4rem 0;
        font-size: 0.85rem;
    }
    .result-ok { border-left: 3px solid #10b981; }
    .result-fail { border-left: 3px solid #ef4444; }
    .result-item .r-title { color: #ccc; font-weight: 400; }
    .result-item .r-sub { color: #555; font-size: 0.75rem; margin-top: 0.15rem; }

    /* ── History ── */
    .hist-item {
        font-family: 'Kanit', sans-serif !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 0.55rem 0;
        border-bottom: 1px solid #141414;
        font-size: 0.82rem;
    }
    .hist-item:last-child { border-bottom: none; }
    .hist-title { color: #aaa; flex: 1; }
    .hist-meta { color: #444; font-size: 0.72rem; text-align: right; white-space: nowrap; margin-left: 0.8rem; }

    /* ── Footer ── */
    .footer {
        text-align: center;
        color: #333;
        font-size: 0.7rem;
        padding: 2rem 0 1rem;
        letter-spacing: 0.03em;
    }

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, header { visibility: hidden; }
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

# ── Hero ──
st.markdown("""
<div class="hero">
    <div class="hero-icon">⬇</div>
    <h1>yt-downloader</h1>
    <p>วาง URL · เลือกรูปแบบ · ดาวน์โหลด</p>
</div>
""", unsafe_allow_html=True)

# ── Status ──
ytdlp_ok = check_yt_dlp()
ffmpeg_ok = check_ffmpeg()
if ytdlp_ok and ffmpeg_ok:
    ver = get_yt_dlp_version()
    st.markdown(f'<span class="pill pill-ok">พร้อมใช้งาน · yt-dlp {ver}</span>', unsafe_allow_html=True)
else:
    issues = []
    if not ytdlp_ok:
        issues.append("yt-dlp")
    if not ffmpeg_ok:
        issues.append("ffmpeg")
    st.markdown(f'<span class="pill pill-warn">ไม่พบ {" · ".join(issues)}</span>', unsafe_allow_html=True)

# ── URL Input Card ──
st.markdown('<div class="card"><div class="card-label">URL</div>', unsafe_allow_html=True)
url_input = st.text_area(
    "url_input",
    height=90,
    placeholder="วาง URL ที่นี่  ·  หลายลิงก์ได้ (บรรทัดละ 1)",
    label_visibility="collapsed",
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Settings Card ──
st.markdown('<div class="card"><div class="card-label">ตั้งค่า</div>', unsafe_allow_html=True)
col1, col2 = st.columns(2)
with col1:
    fmt = st.radio("รูปแบบ", ["mp3", "mp4"], horizontal=True, label_visibility="collapsed")
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
st.markdown('</div>', unsafe_allow_html=True)

# ── Action Buttons ──
col_b1, col_b2, col_b3 = st.columns([1, 2, 1])
with col_b1:
    fetch_clicked = st.button("ดึงชื่อ", use_container_width=True)
with col_b2:
    download_clicked = st.button("ดาวน์โหลด", type="primary", use_container_width=True)
with col_b3:
    history_clicked = st.button("ประวัติ", use_container_width=True)

# ── Parse URLs ──
urls = [u.strip() for u in url_input.strip().splitlines() if u.strip()] if url_input else []

# ── Fetch Titles ──
if fetch_clicked:
    if not urls:
        st.warning("กรุณาใส่ URL ก่อน")
    else:
        with st.spinner("กำลังดึงชื่อ..."):
            titles = fetch_titles(urls)
        if titles:
            st.markdown('<div class="card"><div class="card-label">รายการ</div>', unsafe_allow_html=True)
            for i, t in enumerate(titles, 1):
                st.markdown(
                    f'<div style="color:#aaa;font-size:0.85rem;padding:0.2rem 0;">'
                    f'<span style="color:#555">{i}.</span> {t}</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)

# ── Download ──
if download_clicked:
    if not urls:
        st.warning("กรุณาใส่ URL ก่อน")
    else:
        st.markdown("---")
        st.markdown(
            f'<div style="color:#888;font-size:0.82rem;margin-bottom:0.8rem;">'
            f'{fmt.upper()} · {len(urls)} รายการ · เสียง {audio_q}'
            f'{"" if fmt == "mp3" else f" · วิดีโอ {video_q}"}'
            f'</div>',
            unsafe_allow_html=True,
        )

        total_success = 0
        total_failed = 0
        downloaded_files = []

        for idx, url in enumerate(urls, 1):
            st.markdown(
                f'<div style="color:#555;font-size:0.8rem;margin-top:0.5rem;">'
                f'[{idx}/{len(urls)}] {url[:70]}{"..." if len(url) > 70 else ""}</div>',
                unsafe_allow_html=True,
            )

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
                status_text.markdown(
                    f'<div class="result-item result-ok">'
                    f'<div class="r-title">{title}</div>'
                    f'<div class="r-sub">ดาวน์โหลดสำเร็จ</div></div>',
                    unsafe_allow_html=True,
                )
                downloaded_files.append((file_path, title))
            else:
                total_failed += 1
                status_text.markdown(
                    f'<div class="result-item result-fail">'
                    f'<div class="r-title">{title}</div>'
                    f'<div class="r-sub">ล้มเหลว</div></div>',
                    unsafe_allow_html=True,
                )

        # Summary
        st.markdown("---")
        if total_failed == 0:
            st.success(f"สำเร็จทั้งหมด {total_success} รายการ")
        else:
            st.warning(f"สำเร็จ {total_success} · ล้มเหลว {total_failed}")

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
                    st.error(f"อ่านไฟล์ไม่ได้: {e}")

# ── History ──
if history_clicked:
    st.markdown("---")
    history = load_history()
    if not history:
        st.info("ยังไม่มีประวัติ")
    else:
        st.markdown('<div class="card"><div class="card-label">ประวัติล่าสุด</div>', unsafe_allow_html=True)
        for h in reversed(history[-20:]):
            icon = "●" if h.get("status") == "สำเร็จ" else "○"
            color = "#10b981" if h.get("status") == "สำเร็จ" else "#555"
            title_text = h.get("title", h.get("url", ""))
            if len(title_text) > 55:
                title_text = title_text[:55] + "…"
            st.markdown(
                f'<div class="hist-item">'
                f'<span style="color:{color};margin-right:0.5rem;">{icon}</span>'
                f'<span class="hist-title">{title_text}</span>'
                f'<span class="hist-meta">{h.get("format","").upper()} · {h.get("date","")}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )
        st.markdown('</div>', unsafe_allow_html=True)
    if st.button("ล้างประวัติ", use_container_width=False):
        save_history([])
        st.rerun()

# ── Footer ──
st.markdown(
    '<div class="footer">yt-downloader · yt-dlp + streamlit</div>',
    unsafe_allow_html=True,
)
