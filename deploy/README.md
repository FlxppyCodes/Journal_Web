# Deploying to the Hostinger KVM 4 VPS

## 1. Base setup (once)
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3.12-venv postgresql postgresql-contrib caddy ufw

# Firewall — SSH + HTTPS only
sudo ufw allow OpenSSH
sudo ufw allow 443
sudo ufw enable

# Create a non-root user to run the app
sudo adduser journal
```

## 2. Postgres
```bash
sudo -u postgres psql -c "CREATE USER journal_user WITH PASSWORD 'CHANGE_ME';"
sudo -u postgres psql -c "CREATE DATABASE journal_db OWNER journal_user;"
```

## 3. App
```bash
sudo -u journal -i
cd ~
git clone <your-repo-url> journaling-app   # or scp the files up
cd journaling-app
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env   # fill in DATABASE_URL, API_BEARER_TOKEN, OPENAI_API_KEY, TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
```

Table creation happens automatically on first run (`Base.metadata.create_all`), no manual SQL needed.

## 4. systemd
```bash
sudo cp deploy/api.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now api.service
sudo systemctl status api.service
```

## 5. Caddy reverse proxy + TLS
Add to `/etc/caddy/Caddyfile`:
```
api.yourdomain.com {
    reverse_proxy 127.0.0.1:8000
}
```
```bash
sudo systemctl reload caddy
```
Caddy handles Let's Encrypt cert issuance/renewal automatically — just make sure the subdomain's DNS A record points at the VPS IP first.

## 6. Verify
```bash
curl https://api.yourdomain.com/health
# {"status":"ok"}

curl -X POST https://api.yourdomain.com/daily/mood \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"entry_date":"2026-08-09","mood":"good"}'
```

## 7. Nightly backup cron (do this before you trust the app with real data)
```bash
crontab -e
# add:
0 3 * * * pg_dump journal_db | gzip > /home/journal/backups/journal_$(date +\%F).sql.gz
```
Then sync `/home/journal/backups` off-VPS on a schedule (rclone to Backblaze B2 is a solid free-tier option) — this is the step that protects you if the VPS ever gets wiped again.

## Not yet in this scaffold
- Telegram bot process + scheduler jobs (Phase 6 in the spec) — daily/weekly/monthly AI analysis and nudges.
- iOS app itself (Phase 2 onward).
- Alembic migrations (fine to skip for now since `create_all` handles a schema that isn't changing daily).
