#!/bin/bash
# Fix QQ Bot Server - Run this on the server

echo "🔧 Fixing QQ Bot Server..."

# Check if service exists
if [ ! -f /etc/systemd/system/qqbot.service ]; then
    echo "❌ Service not found. Need to redeploy."
    
    # Install dependencies
    apt-get update
    apt-get install -y python3 python3-pip ufw
    pip3 install flask requests
    
    # Create directory and files
    mkdir -p /opt/qqbot
    cd /opt/qqbot
    
    cat > server.py << 'EOF'
from flask import Flask, request, jsonify
import hashlib, hmac

app = Flask(__name__)
TOKEN = "esoooNzsiEmwc3cx2z5wSau7f9kyL48S"

@app.route("/", methods=["GET"])
def index():
    return "QQ Bot Server Running!"

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.get_json()
    
    # Handle QQ verification
    if data.get("op") == 13:
        d = data.get("d", {})
        plain_token = d.get("plain_token")
        event_ts = d.get("event_ts")
        msg = f"{event_ts}{plain_token}".encode()
        signature = hmac.new(TOKEN.encode(), msg, hashlib.sha256).hexdigest()
        return jsonify({"plain_token": plain_token, "signature": signature})
    
    return jsonify({"code": 0})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
EOF
    
    # Create systemd service
    cat > /etc/systemd/system/qqbot.service << 'EOF'
[Unit]
Description=QQ Bot Server
After=network.target

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/qqbot/server.py
Restart=always

[Install]
WantedBy=multi-user.target
EOF
    
    # Configure firewall
    ufw allow 8080/tcp
    ufw allow 22/tcp
    ufw --force enable
    
    # Start service
    systemctl daemon-reload
    systemctl enable qqbot
fi

# Restart service
systemctl restart qqbot
sleep 2

# Check status
if systemctl is-active --quiet qqbot; then
    echo "✅ QQ Bot Server is running!"
    echo "📍 Webhook URL: http://111.231.18.54:8080/webhook"
    
    # Test local connection
    curl -s http://localhost:8080/ && echo ""
else
    echo "❌ Failed to start service"
    echo "Logs:"
    journalctl -u qqbot -n 20 --no-pager
fi
