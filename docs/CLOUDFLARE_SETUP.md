# Cloudflare Integration Guide: MyAtelier Pro

Cloudflare provides a powerful Web Application Firewall (WAF), DDoS protection, and SSL management.

## 1. DNS Configuration
- Point your `app` and `api` subdomains to your VPS IP.
- Ensure the "Proxy status" (Orange cloud) is **Enabled**.

## 2. SSL/TLS Settings
- Set SSL/TLS mode to **Full (strict)**.
- This requires your Nginx to have a valid certificate (which we already configured with Let's Encrypt).

## 3. WAF & Firewall Rules
- **Block common attacks**: Enable Cloudflare Managed Rules.
- **Bot Fight Mode**: Enable to block malicious scrapers.
- **Rate Limiting**: Add a rule to block IPs making > 200 requests per minute (as a backup to our internal rate limiter).

## 4. Origin Protection
To ensure traffic *only* comes through Cloudflare:
- Update your VPS firewall (`ufw` or `iptables`) to only allow connections on ports 80/443 from [Cloudflare IP ranges](https://www.cloudflare.com/ips/).

## 5. X-Forwarded-For Header
Cloudflare will send the real user IP in the `CF-Connecting-IP` header.
Our Nginx config is already set to handle `X-Forwarded-For`, but you might want to add this to Nginx:
```nginx
set_real_ip_from 103.21.244.0/22;
# ... add all cloudflare IPs ...
real_ip_header CF-Connecting-IP;
```
