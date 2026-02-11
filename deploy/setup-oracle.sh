#!/bin/bash
# ============================================
# Oracle Cloud VPS - yt-downloader Setup Script
# รันครั้งเดียวบน Ubuntu 22.04+ (ARM/x86)
# ============================================

set -e

echo "========================================"
echo "  yt-downloader — Oracle Cloud Setup"
echo "========================================"

# 1. อัพเดท system
echo "[1/6] อัพเดท system..."
sudo apt update && sudo apt upgrade -y

# 2. ลง Python + ffmpeg + git
echo "[2/6] ลง dependencies..."
sudo apt install -y python3 python3-pip python3-venv ffmpeg git

# 3. Clone repo
echo "[3/6] Clone repository..."
cd /home/ubuntu
if [ -d "yt-downloader" ]; then
    cd yt-downloader
    git pull
else
    git clone https://github.com/intity01/yt-downloader.git
    cd yt-downloader
fi

# 4. สร้าง virtual environment
echo "[4/6] สร้าง virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# 5. สร้าง systemd service (ทำงาน 24/7 + auto-restart)
echo "[5/6] สร้าง systemd service..."
sudo tee /etc/systemd/system/yt-downloader.service > /dev/null <<EOF
[Unit]
Description=yt-downloader Streamlit App
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/yt-downloader
Environment="PATH=/home/ubuntu/yt-downloader/venv/bin:/usr/bin"
ExecStart=/home/ubuntu/yt-downloader/venv/bin/streamlit run app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --server.maxUploadSize 50 \
    --browser.gatherUsageStats false
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable yt-downloader
sudo systemctl start yt-downloader

# 6. เปิด firewall port
echo "[6/6] เปิด firewall..."
sudo iptables -I INPUT 6 -m state --state NEW -p tcp --dport 8501 -j ACCEPT
sudo netfilter-persistent save 2>/dev/null || true

echo ""
echo "========================================"
echo "  ✅ Setup เสร็จสิ้น!"
echo "========================================"
echo ""
echo "  เว็บ: http://$(curl -s ifconfig.me):8501"
echo ""
echo "  คำสั่งที่มีประโยชน์:"
echo "    ดู status:  sudo systemctl status yt-downloader"
echo "    ดู log:     sudo journalctl -u yt-downloader -f"
echo "    restart:    sudo systemctl restart yt-downloader"
echo "    อัพเดท:    cd /home/ubuntu/yt-downloader && git pull && sudo systemctl restart yt-downloader"
echo ""
echo "  ⚠️  อย่าลืมเปิด port 8501 ใน Oracle Cloud Console:"
echo "    Networking → Virtual Cloud Networks → Security List → Add Ingress Rule"
echo "    Source CIDR: 0.0.0.0/0  |  Destination Port: 8501  |  Protocol: TCP"
echo ""
