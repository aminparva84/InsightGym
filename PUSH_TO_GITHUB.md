# Push to GitHub - Quick Guide

## Repository Name: InsightGym
## GitHub Username: aminparva84

## Option 1: Create Repository via GitHub Website (Easiest)

1. **Go to GitHub and create the repository:**
   - Visit: https://github.com/new
   - Repository name: `InsightGym`
   - Description: "Raha Fitness - AI-powered fitness platform with Flask backend and React frontend"
   - Choose **Public** or **Private**
   - **DO NOT** check "Initialize this repository with a README"
   - Click "Create repository"

2. **Push your code:**
   ```powershell
   git remote add origin https://github.com/aminparva84/InsightGym.git
   git push -u origin main
   ```

## Option 2: Use PowerShell Script (Automated)

1. **Get a GitHub Personal Access Token:**
   - Go to: https://github.com/settings/tokens
   - Click "Generate new token (classic)"
   - Select scope: `repo` (full control of private repositories)
   - Copy the token

2. **Run the script:**
   ```powershell
   .\create_github_repo.ps1
   ```
   - Enter your token when prompted
   - The script will create the repo and push your code automatically

## Option 3: Use GitHub CLI (if installed)

```powershell
gh repo create InsightGym --public --source=. --remote=origin --push
```

## Current Status

✅ Local Git repository initialized
✅ All files committed
✅ Remote configured: `https://github.com/aminparva84/InsightGym.git`

**Next step:** Create the repository on GitHub (Option 1) and then run:
```powershell
git push -u origin main
```

## Authentication

If you're prompted for credentials:
- **Username:** aminparva84
- **Password:** Use a Personal Access Token (not your GitHub password)
  - Create one at: https://github.com/settings/tokens
  - Required scope: `repo`



