# Writer Reports Deployment Guide

This application consists of two parts that need to be deployed separately:
1. A React frontend (deployed to GitHub Pages)
2. A Flask backend (deployed to Render.com)

## Backend Deployment (Render.com)

1. Create a new account on [Render.com](https://render.com) if you don't have one
2. Click "New +" and select "Web Service"
3. Connect your GitHub repository
4. Fill in the following details:
   - Name: writer-reports-api
   - Environment: Python
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   - Select the Free plan

The backend will be deployed to a URL like: `https://writer-reports-api.onrender.com`

## Frontend Deployment (GitHub Pages)

1. Create a new GitHub repository named 'writer-reports'
2. Update the `homepage` field in `frontend/package.json` with your GitHub username:
   ```json
   "homepage": "https://YOUR_GITHUB_USERNAME.github.io/writer-reports"
   ```
3. Initialize git and push to GitHub:
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin https://github.com/YOUR_USERNAME/writer-reports.git
   git push -u origin main
   ```
4. Deploy to GitHub Pages:
   ```bash
   cd frontend
   npm run deploy
   ```

The frontend will be deployed to: `https://YOUR_GITHUB_USERNAME.github.io/writer-reports`

## Local Development

1. Start the backend:
   ```bash
   python app.py
   ```

2. Start the frontend:
   ```bash
   cd frontend
   npm start
   ```

The app will use the local backend when running in development mode and the deployed backend when running in production.
