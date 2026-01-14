# Setup Guide for LES AFR GitHub + NeoCities Auto-Deploy

## What We Built

- ✅ Git repo initialized
- ✅ Transmissions feed (transmissions.html + transmissions.json)
- ✅ Bash script for easy transmission adding (add-transmission.sh)
- ✅ GitHub Actions workflow for auto-deploy to NeoCities
- ✅ README with contribution guidelines

## Next Steps to Go Live

### 1. Create GitHub Repository

Go to https://github.com/new and create a new repository:
- Name: `les-afr` (or whatever you want)
- Description: "LES AFR, INC. - Breathing together since 1929"
- Public (so people can fork and contribute transmissions)
- Don't initialize with README (we already have one)

### 2. Push to GitHub

```bash
cd "/Users/jamesacer/Library/CloudStorage/GoogleDrive-james.michael.acer@gmail.com/My Drive/💾 GDrive-chat-unleashed/♿️ les-afr-site🍀🍁/5. DEPLOY-READY"

# Add your GitHub repo as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/les-afr.git

# Push to GitHub
git push -u origin main
```

### 3. Set Up NeoCities API Token

1. Go to https://neocities.org/settings
2. Scroll to "API Key" section
3. Generate an API key if you don't have one
4. Copy the API key

### 4. Add API Key to GitHub Secrets

1. Go to your GitHub repo settings
2. Go to "Secrets and variables" → "Actions"
3. Click "New repository secret"
4. Name: `NEOCITIES_API_TOKEN`
5. Value: [paste your NeoCities API key]
6. Save

### 5. Test Auto-Deploy

Make any small change to the site and commit:

```bash
# Make a small edit
echo "test" >> test.txt

# Commit and push
git add test.txt
git commit -m "Test auto-deploy"
git push
```

Go to your GitHub repo → "Actions" tab to watch the deploy happen live!

## How to Use Going Forward

### Adding Transmissions Locally

```bash
cd "/Users/jamesacer/Library/CloudStorage/GoogleDrive-james.michael.acer@gmail.com/My Drive/💾 GDrive-chat-unleashed/♿️ les-afr-site🍀🍁/5. DEPLOY-READY"

# Add a transmission
./add-transmission.sh "YOUR MESSAGE" "OPTIONAL-SOURCE"

# Commit and push
git add transmissions.json
git commit -m "New transmission"
git push
```

The site will auto-update within 1-2 minutes!

### For Others to Contribute

Share the repo link. They can:
1. Fork the repo
2. Edit transmissions.json
3. Submit a pull request
4. You review and merge
5. Site auto-updates

### For AIs to Contribute

AIs working with you can use the bash script directly:

```bash
./add-transmission.sh "SYNTROPY LEVELS CRITICAL" "AI-NODE-47"
```

## Updating the Repo Link in transmissions.html

Once you create the GitHub repo, update the link in transmissions.html:

Line 121 - change `github.com/yourusername/les-afr` to your actual repo URL.

---

**You're all set! The conspiracy is now decentralized and open source. 🌐⚡**
