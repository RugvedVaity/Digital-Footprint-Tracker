# Deploying to Vercel

This guide will help you deploy the Digital Footprint Tracker to Vercel using Serverless Functions.

## Why Vercel?

✅ **Fast** - Global CDN with edge functions  
✅ **Free** - Generous free tier  
✅ **Easy** - GitHub integration with auto-deploys  
✅ **Scalable** - Serverless architecture  
✅ **Custom Domain** - Easy custom domain setup  

---

## 📋 Prerequisites

- Vercel account (free: https://vercel.com)
- GitHub account with your code pushed
- Python 3.11+ (for local testing)

---

## 🚀 Step 1: Prepare Your GitHub Repository

Your code is already on GitHub ✓

Verify push the latest changes:
```bash
cd "Digital Footprint Scanner"
git status
git push origin main
```

---

## 🔧 Step 2: Configure Vercel

The project includes:
- ✅ `vercel.json` - Configuration file
- ✅ `api/index.py` - Serverless entry point
- ✅ `api/health.py` - Health check endpoint
- ✅ `requirements.txt` - Dependencies

---

## 📦 Step 3: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard (Easiest - 2 minutes)

1. **Go to:** https://vercel.com/dashboard
2. **Click:** "Add New..." → "Project"
3. **Import Git Repository:**
   - Search for `Digital-Footprint-Tracker`
   - Click Import
4. **Configure Project:**
   - **Framework Preset:** `Flask` (should auto-detect)
   - **Root Directory:** `./` (leave as is)
   - **Build Command:** `pip install -r requirements.txt`
   - **Output Directory:** `.vercel/output`
5. **Environment Variables:** Add these:
   ```
   FLASK_ENV=production
   SECRET_KEY=<generate-secure-key>
   DATABASE_URL=sqlite:///tmp/digital_footprint.db
   ```
6. **Click:** "Deploy"
7. **Wait:** 2-3 minutes for Vercel to build and deploy

### Option B: Deploy via Vercel CLI (Advanced - 5 minutes)

```bash
# Install Vercel CLI
npm install -g vercel

# Login to Vercel
vercel login

# Deploy from project directory
cd "Digital Footprint Scanner"
vercel

# Follow prompts:
# - Link to existing project: No
# - Project name: digital-footprint-tracker
# - Directory: ./
# - Override settings: No

# To set environment variables:
vercel env add FLASK_ENV production
vercel env add SECRET_KEY <your-secret-key>
vercel env add DATABASE_URL sqlite:///tmp/digital_footprint.db

# Redeploy with env vars
vercel --prod
```

---

## 🔐 Step 4: Set Environment Variables

After deployment, go to **Project Settings:**

1. In Vercel Dashboard → Your Project → Settings
2. Go to **Environment Variables**
3. Add these variables:

| Key | Value |
|-----|-------|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | Generate with: `python -c "import secrets; print(secrets.token_hex(32))"` |
| `DATABASE_URL` | `sqlite:///tmp/digital_footprint.db` |
| `FLASK_APP` | `app:app` |

### Generate Secure Secret Key

```bash
python3
>>> import secrets
>>> secrets.token_hex(32)
# Copy the output and use it
```

---

## ✅ Step 5: Test Your Deployment

Once deployed, Vercel gives you a URL like:
```
https://digital-footprint-tracker-xyz.vercel.app
```

### Test endpoints:

```bash
# Health check
curl https://your-vercel-url/api/health

# Home page
curl https://your-vercel-url/

# API check
curl -X POST https://your-vercel-url/api/check \
  -H "Content-Type: application/json" \
  -d '{"username": "testuser"}'
```

---

## 🔄 Step 6: Enable Auto-deployments

Vercel automatically redeploys when you push to GitHub:

```bash
# Make changes, commit, and push
git add .
git commit -m "Update feature"
git push origin main

# Vercel automatically deploys! ✓
# Check deployment status in Vercel Dashboard
```

---

## 🗄️ Database Considerations

### SQLite on Vercel (Current Setup)
- ✅ Works for hobby projects
- ✅ No additional setup needed
- ⚠️ Ephemeral storage (resets on redeployment)
- ⚠️ Not ideal for production with multiple instances

### PostgreSQL on Vercel (Recommended for Production)

If you want persistent database:

1. **Create PostgreSQL database:**
   - Use Supabase (free tier): https://supabase.com
   - Or Vercel Postgres: https://vercel.com/storage/postgres (invite only)
   - Or Railway Postgres (recommended)

2. **Update environment variable:**
   ```
   DATABASE_URL=postgresql://user:password@host:5432/database
   ```

3. **Install PostgreSQL driver:**
   ```bash
   pip install psycopg2-binary
   ```

4. **Update requirements.txt and redeploy**

---

## 📊 Monitoring & Logs

### View Logs in Vercel Dashboard

1. Go to your project
2. Click "Deployments"
3. Click on the latest deployment
4. Go to "Runtime Logs" tab
5. See real-time logs

### Local Testing (Before Deployment)

```bash
# Create .env file
echo "FLASK_ENV=production" > .env
echo "SECRET_KEY=$(python -c 'import secrets; print(secrets.token_hex(32))')" >> .env

# Test locally
python app.py

# Visit http://localhost:5000
```

---

## 🐛 Troubleshooting

### Issue: "Module not found" error
**Solution:**
```bash
# Update requirements.txt
pip install -r requirements.txt

# Commit and push
git add requirements.txt
git commit -m "Update dependencies"
git push origin main
```

### Issue: Database connection error
**Solution:**
- Use `/tmp/` directory for SQLite
- Or switch to PostgreSQL
- Check `DATABASE_URL` environment variable

### Issue: Static files not loading
**Solution:**
- Vercel serves static files automatically from `public/` directory
- Move static files if needed:
  ```bash
  mkdir -p public/static
  cp -r static/* public/static/
  ```

### Issue: 502 Bad Gateway
**Solution:**
1. Check build logs in Vercel Dashboard
2. Verify all dependencies in `requirements.txt`
3. Check for Python version conflicts
4. Redeploy: Click "Redeploy" in Vercel Dashboard

---

## 🚀 After Deployment

### 1. Test Your App
- Visit your Vercel URL
- Register a test account
- Run a username scan
- Check if everything works

### 2. Setup Custom Domain (Optional)
1. Go to Project Settings → Domains
2. Add your custom domain
3. Follow DNS setup instructions
4. Domain is live in ~5 minutes

### 3. Enable HTTPS (Automatic)
- Vercel automatically enables HTTPS
- Your app is secure by default ✓

### 4. Monitor Performance
- Vercel Analytics: Automatic performance tracking
- Go to Insights tab in Vercel Dashboard

---

## 📈 Vercel Pricing

| Feature | Free | Pro |
|---------|------|-----|
| **Deployments** | Unlimited | Unlimited |
| **Build time** | 100 hours/month | 400 hours/month |
| **Serverless Functions** | Up to 12 seconds | Up to 60 seconds |
| **Custom Domains** | ✓ | ✓ |
| **Automatic HTTPS** | ✓ | ✓ |
| **Cost** | Free | $20/month |

Perfect for hobby projects with free tier! 🎉

---

## 🔗 Useful Links

- **Vercel Dashboard:** https://vercel.com/dashboard
- **Project Settings:** https://vercel.com/dashboard/[project-name]/settings
- **Vercel Python Docs:** https://vercel.com/docs/functions/serverless-functions/runtimes/python
- **Flask on Vercel:** https://vercel.com/docs/frameworks/flask

---

## ✨ Next Steps

1. ✅ Push code to GitHub
2. ⬜ Go to Vercel Dashboard
3. ⬜ Import your GitHub repo
4. ⬜ Add environment variables
5. ⬜ Deploy (automatic)
6. ⬜ Test your live URL
7. ⬜ Share & celebrate! 🎉

---

## 💬 Need Help?

- **Vercel Support:** https://vercel.com/support
- **Discord Community:** https://discord.gg/vercel
- **GitHub Issues:** Post your issue in your repo

Good luck! 🚀
