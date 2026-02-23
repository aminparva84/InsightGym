#!/bin/bash
# Install Caddy on EC2 and configure HTTPS with Let's Encrypt.
# Requires: SSM parameter /insightgym/DOMAIN set to your domain (e.g. app.yourdomain.com)
# DNS: A record for that domain must point to this instance's public IP.
set -e
REGION=$(curl -s http://169.254.169.254/latest/meta-data/placement/region)
DOMAIN=$(aws ssm get-parameter --name /insightgym/DOMAIN --query Parameter.Value --output text --region "$REGION" 2>/dev/null || true)
if [ -z "$DOMAIN" ]; then
  echo "ERROR: Set SSM parameter /insightgym/DOMAIN to your domain (e.g. app.yourdomain.com) and ensure DNS A record points to this server."
  exit 1
fi
# Install Caddy (binary, Amazon Linux 2 / RHEL-like)
CADDY_VERSION="2.7.6"
curl -sL -o /tmp/caddy.tar.gz "https://github.com/caddyserver/caddy/releases/download/v${CADDY_VERSION}/caddy_${CADDY_VERSION}_linux_amd64.tar.gz"
tar -xzf /tmp/caddy.tar.gz -C /tmp
sudo mv /tmp/caddy /usr/local/bin/caddy
sudo chmod +x /usr/local/bin/caddy
sudo setcap 'cap_net_bind_service=+ep' /usr/local/bin/caddy
rm -f /tmp/caddy.tar.gz
# Caddyfile: HTTPS with automatic Let's Encrypt, proxy to app
sudo mkdir -p /etc/caddy
sudo tee /etc/caddy/Caddyfile > /dev/null << CADDYEOF
{
  email admin@${DOMAIN}
}
${DOMAIN} {
  reverse_proxy 127.0.0.1:8080
}
CADDYEOF
# Optional: redirect HTTP (port 80) to HTTPS - Caddy does this by default for the same block
# systemd unit
sudo tee /etc/systemd/system/caddy.service > /dev/null << 'SVCEOF'
[Unit]
Description=Caddy
Documentation=https://caddyserver.com/docs/
After=network.target

[Service]
User=root
ExecStart=/usr/local/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile
Restart=on-failure
LimitNOFILE=1048576

[Install]
WantedBy=multi-user.target
SVCEOF
sudo systemctl daemon-reload
sudo systemctl enable caddy
sudo systemctl restart caddy
echo "Caddy installed and started. HTTPS should be available at https://${DOMAIN}"
echo "If DNS is not yet pointing here, certificate may fail; fix DNS and run: sudo systemctl restart caddy"
