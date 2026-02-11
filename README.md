# 🎵 MP3/MP4 Downloader Web App

เว็บแอพดาวน์โหลดเพลง/วิดีโอ สร้างด้วย Streamlit + yt-dlp

## ✨ Features
- ดาวน์โหลด MP3 / MP4 จาก YouTube, TikTok, Facebook, Twitter ฯลฯ
- เลือกคุณภาพเสียง / วิดีโอ
- แสดง progress แบบ real-time
- ประวัติดาวน์โหลด
- Dark theme สวยงาม

---

## 🚀 Deploy ฟรี (3 วิธี)

### วิธีที่ 1: Streamlit Cloud (แนะนำ — ง่ายสุด)

1. **สร้าง GitHub repo** → push โฟลเดอร์ `web_app` ขึ้นไป
2. ไปที่ [share.streamlit.io](https://share.streamlit.io)
3. Sign in ด้วย GitHub
4. กด **"New app"** แล้วเลือก:
   - Repository: `your-username/your-repo`
   - Branch: `main`
   - Main file path: `app.py`
5. ในส่วน **Advanced settings** → เพิ่ม Packages:
   ```
   ffmpeg
   ```
6. กด **Deploy!** 🎉

> ⚠️ ข้อจำกัด: RAM 1GB, ไม่เหมาะกับไฟล์ใหญ่มาก

---

### วิธีที่ 2: Hugging Face Spaces (ฟรี)

1. ไปที่ [huggingface.co/spaces](https://huggingface.co/spaces)
2. สร้าง Space ใหม่ → เลือก **Streamlit**
3. Upload ไฟล์ทั้งหมดใน `web_app/`
4. เพิ่มไฟล์ `packages.txt` ที่มี:
   ```
   ffmpeg
   ```
5. รอ build เสร็จ → ใช้งานได้เลย!

---

### วิธีที่ 3: Render (ฟรี)

1. Push code ขึ้น GitHub
2. ไปที่ [render.com](https://render.com) → New Web Service
3. เชื่อม GitHub repo
4. ตั้งค่า:
   - **Build Command:** `pip install -r requirements.txt && apt-get update && apt-get install -y ffmpeg`
   - **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
5. Deploy!

> ⚠️ ข้อจำกัด: Free tier จะ sleep หลัง 15 นาที

---

## 💻 รันในเครื่อง (Local)

```bash
cd web_app
pip install -r requirements.txt
streamlit run app.py
```

เปิด browser ไปที่ `http://localhost:8501`

---

## 📁 โครงสร้างไฟล์

```
web_app/
├── app.py                  # Main Streamlit app
├── requirements.txt        # Python dependencies
├── packages.txt            # System packages (ffmpeg)
├── pyproject.toml           # Project metadata
├── apt_packages.txt        # For some platforms
└── .streamlit/
    └── config.toml         # Streamlit theme config
```

---

## ⚠️ ข้อควรระวัง

1. **แพลตฟอร์มฟรีมี Resource จำกัด** — RAM/CPU/Storage น้อย
2. **ไฟล์ดาวน์โหลดเป็น temporary** — ผู้ใช้ต้องกดปุ่มดาวน์โหลดไปเครื่องตัวเอง
3. **อาจถูก rate limit** จาก YouTube ถ้าใช้มากเกินไป
4. **ไม่ควรเปิดสาธารณะ** ถ้าเป็นเนื้อหาที่มีลิขสิทธิ์

---

## 📋 วิธี Push ขึ้น GitHub

```bash
# ติดตั้ง git ก่อน (ถ้ายังไม่มี)
cd web_app

git init
git add .
git commit -m "Initial commit - MP3/MP4 Downloader Web App"

# สร้าง repo ใหม่บน github.com แล้ว
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
git branch -M main
git push -u origin main
```

จากนั้นไปเชื่อมกับ Streamlit Cloud / Hugging Face / Render ตามวิธีที่เลือก
