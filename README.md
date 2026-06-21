# RITS Services — Website (Python / Flask)

A professional dual-theme company website with all menu pages, a working
language switcher (English / Hindi), and a Portal with two logins:

| Portal | Method |
|---|---|
| Employee Login | LDAP (real `ldap3` if configured, demo fallback) |
| Customer Login | Google account (real OAuth if configured, demo fallback) |

## Quick start

```bash
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000

## Demo credentials (when no LDAP server is configured)

| Username | Password |
|---|---|
| admin | admin123 |
| employee | rits@2026 |

Customer login opens a simulated Google account chooser when no OAuth
credentials are configured — enter any email to sign in.

## Enable REAL LDAP (employee login)

```bash
pip install ldap3
export LDAP_SERVER="ldap://your-ldap-server:389"
export LDAP_BASE_DN="ou=users,dc=yourcompany,dc=com"
export LDAP_USER_ATTR="uid"        # or sAMAccountName for Active Directory
python app.py
```

## Enable REAL Google login (customer login)

1. Go to Google Cloud Console → APIs & Services → Credentials
2. Create an OAuth 2.0 Client ID (Web application)
3. Add authorized redirect URI: `http://127.0.0.1:5000/auth/google/callback`
4. Then:

```bash
pip install authlib requests
export GOOGLE_CLIENT_ID="xxxx.apps.googleusercontent.com"
export GOOGLE_CLIENT_SECRET="xxxx"
python app.py
```

## Features

- Dark / light theme toggle (saved in browser)
- Language switcher EN / हिन्दी (server-side, saved in session)
- Pages: Home, About Us, Services, Industries, Portfolio, Careers, Blog, Contact Us
- Working contact form (messages logged to `contact_messages.log`)
- Employee & Customer dashboards after login
- Fully responsive (desktop / tablet / mobile)

## Production notes

- Set a strong `SECRET_KEY` environment variable
- Run behind gunicorn + nginx:  `gunicorn -w 4 app:app`
- Replace the demo employee accounts before going live
