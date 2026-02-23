# HTTPS on EC2 with Caddy (Option A)

HTTPS is provided by **Caddy** on the EC2 instance: it listens on **80** and **443**, gets a **Let's Encrypt** certificate automatically, and reverse-proxies to the app on **localhost:8080**.

## Current setup

- **Caddy** is installed and running as a systemd service on the instance.
- **Domain** is read from SSM: `/insightgym/DOMAIN` (currently set to `app.insightgym.com`).
- **Ports 80 and 443** are open on the EC2 security group.

## Use your own domain

1. **Set the domain in SSM** (replace with your real domain):
   ```bash
   aws ssm put-parameter --name /insightgym/DOMAIN --value "app.yourdomain.com" --type String --region me-south-1 --overwrite
   ```

2. **Point DNS to the server**  
   Create an **A record** for your domain (e.g. `app.yourdomain.com`) → **15.185.88.160** (the EC2 Elastic IP).

3. **Update Caddy config and restart** (on the instance via **SSH** or **Session Manager**):
   - Edit `/etc/caddy/Caddyfile`: change the server name (e.g. `app.insightgym.com`) to your domain and the `email` line if you like.
   - Restart Caddy:
     ```bash
     sudo systemctl restart caddy
     ```

4. **Wait for DNS**  
   After DNS propagates, Caddy will obtain/renew the Let's Encrypt certificate. If it fails at first, run `sudo systemctl restart caddy` again once DNS is correct.

## URLs

- **HTTPS:** `https://<your-domain>` (e.g. `https://app.insightgym.com`) once DNS points to 15.185.88.160 and Caddy has the cert.
- **HTTP (direct):** `http://15.185.88.160:8080` still works; Caddy does not serve the raw IP on 80/443.

## Re-run Caddy setup (new instance or reinstall)

The script is in the repo: `infra/aws/setup-caddy-https.sh`. It:

- Reads `/insightgym/DOMAIN` from SSM
- Installs Caddy, writes `/etc/caddy/Caddyfile`, and enables the systemd service

To run it on the instance (e.g. via SSM), base64-encode the script (with **Unix line endings**), then run:

```bash
echo "<base64>" | base64 -d | sudo bash
```

Or store the script in SSM and fetch+run it the same way as the app run script.

## Troubleshooting

- **Certificate errors:** Ensure the domain’s A record points to **15.185.88.160** and that ports **80** and **443** are allowed in the EC2 security group (Let's Encrypt uses port 80 for HTTP-01).
- **Caddy status:** On the instance run `sudo systemctl status caddy` and `sudo journalctl -u caddy -f`.
- **Config:** Caddyfile is at `/etc/caddy/Caddyfile`; edit and run `sudo systemctl restart caddy` to apply.
