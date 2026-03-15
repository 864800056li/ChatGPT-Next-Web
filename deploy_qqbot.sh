#!/bin/bash
# QQ Bot Server Deployment Script
set -e

echo "🚀 Starting QQ Bot Server deployment..."

# Update system
echo "📦 Updating system packages..."
apt-get update -qq

# Install Python and dependencies
echo "🐍 Installing Python and dependencies..."
apt-get install -y -qq python3 python3-pip curl ufw
pip3 install -q flask requests

# Create application directory
mkdir -p /opt/qqbot
cd /opt/qqbot

# Create the Flask server
cat > server.py << 'PYTHON_EOF'
from flask import Flask, request, jsonify
import hashlib
import hmac
import logging

app = Flask(__name__)

# Configuration
TOKEN = "esoooNzsiEmwc3cx2z5wSau7f9kyL48S"
APPID = "1903480327"

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route("/", methods=["GET"])
def index():
    return "QQ Bot Server is running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json()
        logger.info(f"Received request: {data}")
        
        # Handle QQ verification (op=13)
        if data.get("op") == 13:
            d = data.get("d", {})
            plain_token = d.get("plain_token")
            event_ts = d.get("event_ts")
            
            if plain_token and event_ts:
                msg = f"{event_ts}{plain_token}".encode()
                signature = hmac.new(TOKEN.encode(), msg, hashlib.sha256).hexdigest()
                logger.info(f"Verification successful for token: {plain_token}")
                return jsonify({
                    "plain_token": plain_token,
                    "signature": signature
                })
        
        # Handle messages (op=0)
        if data.get("op") == 0:
            msg_type = data.get("t")
            logger.info(f"Received message type: {msg_type}")
            # TODO: Forward to OpenClaw
            return jsonify({"code": 0})
        
        return jsonify({"code": 0})
    
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        return jsonify({"code": 0})

if __name__ == "__main__":
    print("🚀 QQ Bot Server starting on http://0.0.0.0:8080")
    print(f"📍 Webhook URL: http://111.231.18.54:8080/webhook")
    app.run(host="0.0.0.0", port=8080, debug=False)
PYTHON_EOF

# Create systemd service
cat > /etc/systemd/system/qqbot.service << 'SERVICE_EOF'
[Unit]
Description=QQ Bot Server
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/qqbot
ExecStart=/usr/bin/python3 /opt/qqbot/server.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF

# Configure firewall
echo "🔥 Configuring firewall..."
ufw allow 8080/tcp
ufw allow 22/tcp
ufw --force enable

# Start service
echo "🔄 Starting service..."
systemctl daemon-reload
systemctl enable qqbot
systemctl stop qqbot 2>/dev/null || true
systemctl start qqbot

# Wait for service to start
sleep 3

# Check status
if systemctl is-active --quiet qqbot; then
    echo ""
    echo "✅ QQ Bot Server deployed successfully!"
    echo ""
    echo "📍 Webhook URL: http://111.231.18.54:8080/webhook"
    echo ""
    echo "📝 Next steps:"
    echo "   1. Go to https://q.qq.com"
    echo "   2. Navigate to 开发 → 回调配置"
    echo "   3. Enter webhook URL: http://111.231.18.54:8080/webhook"
    echo ""
    echo "🔍 Check logs: journalctl -u qqbot -f"
else
    echo "❌ Service failed to start"
    echo "Check logs: journalctl -u qqbot -n 50"
    exit 1
fi
