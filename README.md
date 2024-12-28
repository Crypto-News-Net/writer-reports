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

## Dependencies and Build Requirements

### Required Dependencies
The frontend requires specific versions of certain dependencies to build successfully:

```json
{
  "dependencies": {
    "ajv": "6.12.6",
    "ajv-keywords": "3.5.2"
  }
}
```

These dependencies are critical for the webpack build process and must be included in `package.json`. They resolve module resolution conflicts in the build chain:
- `ajv` version 6.12.6 provides the expected file structure at `lib/ajv.js`
- `ajv-keywords` version 3.5.2 is compatible with this ajv version

### GitHub Actions Build
The workflow uses a clean install approach to ensure consistent builds:
```yaml
- name: Install Dependencies
  working-directory: frontend
  run: |
    rm -rf node_modules package-lock.json
    npm install --legacy-peer-deps
```

### Known Issues
1. **Build Failures**: If you encounter module resolution errors mentioning `ajv`, ensure you have the exact versions specified above in your dependencies.
2. **Clean Installs**: Sometimes a clean install (`rm -rf node_modules package-lock.json` followed by `npm install`) can resolve dependency-related build issues.
