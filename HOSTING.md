# Hosting Guide - Digital Footprint Tracker

This guide will help you deploy the Digital Footprint Tracker to various hosting platforms.

## Quick Summary of Options

| Platform | Free Tier | Setup Time | Recommended |
|----------|-----------|-----------|------------|
| **Railway** | $5/month free credits | 5 mins | ⭐ Best for free |
| **Render** | Free (1 month trial) | 5 mins | ✓ Good alternative |
| **Heroku** | ❌ Paid only ($7+/month) | 10 mins | Simple but costly |
| **PythonAnywhere** | Free tier available | 10 mins | Good for testing |
| **Replit** | Free with limits | 5 mins | Easiest for beginners |
| **DigitalOcean** | $4/month (after free trial) | 20 mins | Best long-term |

---

## 🚀 Option 1: Railway (Recommended - FREE)

Railway offers the best free alternative with $5/month free credits.

### Step 1: Create Railway Account
1. Go to https://railway.app
2. Click "Deploy Now" or sign up
3. Sign in with GitHub (recommended)

### Step 2: Deploy Project
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login to Railway
railway login

# Initialize project
railway init

# Link your GitHub repo or select this folder
# Railway will auto-detect Flask

# Deploy
railway up
```

Or **Deploy via GitHub:**
1. Push code to GitHub (already done ✓)
2. Go to https://railway.app
3. Click "New Project" → "Deploy from GitHub"
4. Select your `Digital-Footprint-Tracker` repo
5. Railway auto-detects Flask and deploys

### Step 3: Set Environment Variables
In Railway Dashboard:
1. Go to project → Variables
2. Add:
   ```
   FLASK_ENV=production
   SECRET_KEY=use-a-strong-random-key-here
   FLASK_APP=app.py
   ```

3. Railway automatically sets `PORT` env variable

### Step 4: Access Your App
Railways provides a unique URL like:
```
https://your-project-xyz.railway.app
```

Visit it in your browser!

---

## 🎯 Option 2: Render (Alternative - FREE)

Render offers a free tier perfect for hobby projects.

### Deploy via GitHub
1. Go to https://render.com
2. Sign up (use GitHub)
3. Click "New +" → "Web Service"
4. Select your GitHub repo
5. Configure:
   - **Name**: digital-footprint-tracker
   - **Environment**: Python 3.11
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Plan**: Free (note: spins down after 15 mins of inactivity)

6. Add environment variables in dashboard:
   ```
   FLASK_ENV=production
   SECRET_KEY=your-secret-key
   ```

7. Deploy!

---

## 💜 Option 3: Heroku (Paid - $7+/month)

If you prefer Heroku (now paid only):

### Prerequisites
```bash
# Install Heroku CLI
# Windows: Download from https://devcenter.heroku.com/articles/heroku-cli
# macOS: brew tap heroku/brew && brew install heroku
# Linux: curl https://cli-assets.heroku.com/install.sh | sh

heroku login
```

### Deploy
```bash
# Create Heroku app
heroku create your-app-name-unique

# Set environment variables
heroku config:set FLASK_ENV=production
heroku config:set SECRET_KEY=your-random-secret-key

# Deploy from git
git push heroku main

# View logs
heroku logs --tail
```

---

## 🐳 Option 4: Docker Deployment

If you have Docker installed:

```bash
# Build Docker image
docker build -t digital-footprint-tracker .

# Run locally
docker run -p 5000:5000 digital-footprint-tracker

# Test at http://localhost:5000
```

### Deploy Docker to:
- **DigitalOcean App Platform** (easiest for Docker)
- **AWS ECS**
- **Google Cloud Run**
- **Azure Container Instances**

---

## 🖥️ Option 5: Self-Hosted (VPS)

Best for long-term, cheap hosting.

### Using DigitalOcean ($4-6/month)

1. **Create Droplet:**
   - Go to https://www.digitalocean.com
   - Create new Droplet (Ubuntu 22.04)
   - Choose $4-6/month plan
   - Select your region

2. **SSH into server:**
   ```bash
   ssh root@your_droplet_ip
   ```

3. **Setup environment:**
   ```bash
   apt update && apt upgrade -y
   apt install python3 python3-pip python3-venv git nginx ufw -y
   
   # Clone repo
   cd /home
   git clone https://github.com/RugvedVaity/Digital-Footprint-Tracker.git
   cd Digital-Footprint-Tracker
   
   # Create virtual environment
   python3 -m venv venv
   source venv/bin/activate
   
   # Install dependencies
   pip install -r requirements.txt
   ```

4. **Setup Nginx:**
   ```bash
   # Create nginx config
   sudo nano /etc/nginx/sites-available/digital-footprint
   ```
   
   Paste:
   ```nginx
   server {
       listen 80;
       server_name your_domain.com;

       location / {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

5. **Enable and restart:**
   ```bash
   sudo ln -s /etc/nginx/sites-available/digital-footprint /etc/nginx/sites-enabled/
   sudo nginx -t
   sudo systemctl restart nginx
   ```

6. **Run Flask with Gunicorn:**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

7. **Setup SSL with Let's Encrypt:**
   ```bash
   sudo apt install certbot python3-certbot-nginx -y
   sudo certbot --nginx -d your_domain.com
   ```

---

## ⚙️ Environment Variables for Production

Create a `.env` file with these variables:

```env
# Flask
FLASK_ENV=production
SECRET_KEY=your-super-secure-random-key
FLASK_APP=app.py

# Database (SQLite by default, no setup needed)
DATABASE_URL=sqlite:///digital_footprint.db

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-specific-password

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

### Generate a Strong Secret Key
```bash
python3
>>> import secrets
>>> secrets.token_hex(32)
'your-generated-secret-key-here'
```

---

## 📋 Pre-Deployment Checklist

- [ ] Code pushed to GitHub
- [ ] `requirements.txt` up to date
- [ ] `Procfile` or `docker-compose.yml` ready
- [ ] Environment variables configured
- [ ] `.env` file created with production settings
- [ ] Database migrations ready
- [ ] Secret key is strong and unique
- [ ] DEBUG=False for production
- [ ] HTTPS enabled (most platforms do this automatically)

---

## 🔧 Deployment Troubleshooting

### Port Issues
- Make sure app listens on the PORT environment variable
- Check `app.py` - change:
  ```python
  if __name__ == '__main__':
      port = os.getenv('PORT', 5000)
      app.run(host='0.0.0.0', port=int(port), debug=False)
  ```

### Database Issues
- SQLite works out of box
- For PostgreSQL, install: `pip install psycopg2-binary`

### Static Files Not Loading
- Run: `flask collect-static` (if using Flask-Assets)
- Or ensure `static/` directory is in root

### Module Import Errors
- Verify: `pip list` shows all dependencies
- Try: `pip install -r requirements.txt --force-reinstall`

---

## 📊 Monitoring & Logs

### Railway
```bash
railway logs
```

### Render
- Dashboard → Logs tab

### Heroku
```bash
heroku logs --tail
```

### DigitalOcean (SSH)
```bash
tail -f /var/log/syslog
# Or for your app:
journalctl -u your-app -f
```

---

## 🎯 Recommended Path

**For fastest deployment (5 minutes):**
1. Use **Railway** (free $5/month credits)
2. Connect GitHub repo
3. Set 3 environment variables
4. Done! ✓

**For free tier (limited but free):**
1. Use **Render**
2. Deploy from GitHub
3. Set environment variables
4. Done! ✓

**For long-term (cheapest):**
1. Use **DigitalOcean VPS** ($4/month)
2. Takes 20 mins to setup
3. Full control and speed

---

## 🆘 Need Help?

If deployment fails:
1. Check logs (each platform has a logs viewer)
2. Verify environment variables are set
3. Test locally: `python app.py`
4. Check `requirements.txt` is correct
5. Ensure Procfile exists and is formatted correctly

---

## ✨ After Deployment

1. **Test your app** - visit the public URL
2. **Register a test user** - test authentication
3. **Run a scan** - test core functionality
4. **Configure email** (optional) - for notifications
5. **Monitor logs** - watch for errors
6. **Set up DNS** (optional) - use custom domain

Would you like help with any specific platform?
