#!/bin/bash

# Digital Footprint Tracker - Quick Deploy Script
# Helps with Railway deployment

echo "🚀 Digital Footprint Tracker - Quick Deploy"
echo "========================================"
echo ""
echo "This script will help you deploy to Railway (recommended)"
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

echo ""
echo "Step 1: Login to Railway"
railway login

echo ""
echo "Step 2: Initialize project"
railway init

echo ""
echo "Step 3: Set environment variables"
echo "Setting production environment..."
railway variables set FLASK_ENV=production
railway variables set SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
railway variables set FLASK_APP=app.py

echo ""
echo "Step 4: Deploy!"
railway up

echo ""
echo "✅ Deployment complete!"
echo "Your app will be available at the Railway URL provided above"
echo ""
echo "Next steps:"
echo "1. Visit your Railway URL"
echo "2. Register a new account"
echo "3. Test the application"
echo ""
echo "For more hosting options, see HOSTING.md"
