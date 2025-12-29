# Git Repository Setup Instructions

## ✅ Local Repository Created

Your local Git repository has been initialized and all files have been committed.

## 📤 Push to Remote Repository

To push your code to GitHub, follow these steps:

### Option 1: Using GitHub Website (Recommended)

1. **Create a new repository on GitHub:**
   - Go to https://github.com/new
   - Repository name: `InsightGym` or `raha-fitness`
   - Description: "Raha Fitness - AI-powered fitness platform with Flask backend and React frontend"
   - Choose **Public** or **Private**
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
   - Click "Create repository"

2. **Connect and push:**
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/InsightGym.git
   git push -u origin main
   ```

### Option 2: Using GitHub CLI (if installed)

```bash
gh repo create InsightGym --public --source=. --remote=origin --push
```

### Option 3: Using SSH (if you have SSH keys set up)

```bash
git remote add origin git@github.com:YOUR_USERNAME/InsightGym.git
git push -u origin main
```

## 📝 What's Included

- ✅ Flask backend with SQLAlchemy models
- ✅ React frontend with i18n support (Farsi/English)
- ✅ AI Coach agent with RAG system
- ✅ Workout plan generator (6-month periodization)
- ✅ Comprehensive registration system
- ✅ Vector database integration
- ✅ All documentation files

## ⚠️ Important Notes

- The `venv/` folder is excluded via `.gitignore`
- Database files (`*.db`, `*.sqlite`) are excluded
- Environment files (`.env`) are excluded
- `node_modules/` is excluded

## 🔐 Environment Variables

Before deploying, make sure to set up your `.env` file with:
- `DATABASE_URL`
- `JWT_SECRET_KEY`
- Vector database credentials (if using Pinecone/Supabase)

## 📚 Next Steps

After pushing to GitHub:
1. Set up CI/CD (optional)
2. Configure environment variables in your hosting platform
3. Deploy backend to a service like Heroku, Railway, or AWS
4. Deploy frontend to Vercel, Netlify, or similar



