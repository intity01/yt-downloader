# 🚀 Deploy yt-downloader บน Oracle Cloud Free Tier

## ข้อดีของ Oracle Cloud Free Tier
- **ฟรีตลอดชีพ** — ARM VM 4 OCPU / 24 GB RAM / 200 GB Storage
- **IP ไม่ถูกบล็อก** เหมือน Streamlit Cloud
- **Cookies support** — อัปโหลด cookies.txt ผ่านเว็บได้เลย

---

## ขั้นตอน

### 1. สมัคร Oracle Cloud
1. ไปที่ [cloud.oracle.com](https://cloud.oracle.com)
2. สมัครบัญชี (ต้องใช้บัตรเครดิต/เดบิตสำหรับ verify แต่ไม่คิดเงิน)
3. เลือก Home Region ใกล้สุด (เช่น Singapore)

### 2. สร้าง VM
1. ไปที่ **Compute → Instances → Create Instance**
2. เลือก Image: **Ubuntu 22.04** (หรือ 24.04)
3. เลือก Shape: **VM.Standard.A1.Flex** (ARM, ฟรี สูงสุด 4 OCPU / 24 GB)
4. ตั้ง OCPU: 1, RAM: 6 GB (พอสำหรับ yt-downloader)
5. ดาวน์โหลด SSH key (.pem) เก็บไว้

### 3. เปิด Port 8501
1. **Networking → Virtual Cloud Networks → คลิก VCN ของเรา**
2. **Security Lists → Default Security List → Add Ingress Rule**
   - Source CIDR: `0.0.0.0/0`
   - Destination Port: `8501`
   - Protocol: TCP

### 4. SSH เข้า VM แล้วรัน Setup
```bash
# SSH เข้า VM
ssh -i ~/your-key.pem ubuntu@<PUBLIC_IP>

# ดาวน์โหลดและรันสคริปต์
curl -fsSL https://raw.githubusercontent.com/intity01/yt-downloader/main/deploy/setup-oracle.sh | bash
```

### 5. เข้าเว็บ
```
http://<PUBLIC_IP>:8501
```

---

## คำสั่งที่มีประโยชน์

```bash
# ดูสถานะ
sudo systemctl status yt-downloader

# ดู log realtime
sudo journalctl -u yt-downloader -f

# restart
sudo systemctl restart yt-downloader

# อัปเดทเวอร์ชันใหม่
cd /home/ubuntu/yt-downloader
git pull
sudo systemctl restart yt-downloader

# อัปเดท yt-dlp
source venv/bin/activate
pip install -U yt-dlp
sudo systemctl restart yt-downloader
```

---

## Cookies (สำหรับวิดีโอที่ต้องล็อกอิน)

1. ติดตั้ง extension **Get cookies.txt LOCALLY** ใน Chrome/Firefox
2. ไปที่ YouTube แล้ว export cookies.txt
3. อัปโหลดไฟล์ผ่านเว็บ yt-downloader (กดปุ่ม 🍪 Upload Cookies)

---

## Domain Name (Optional)
ถ้าอยากใช้ domain แทน IP:
1. ซื้อ domain (เช่น จาก Cloudflare หรือ Namecheap)
2. ชี้ A record ไปที่ Public IP ของ VM
3. ใช้ **Caddy** เป็น reverse proxy + HTTPS อัตโนมัติ:
```bash
sudo apt install -y caddy
echo "yourdomain.com { reverse_proxy localhost:8501 }" | sudo tee /etc/caddy/Caddyfile
sudo systemctl restart caddy
```
