# 🚀 GitHub Profile Complete Setup Guide

This guide walks you through deploying your animated terminal profile following the exact 4 phases from your **Master Prompt** and **Setup Guide** PDFs.

---

## 📋 What is Already Built for You in this Folder

- 🖼️ **`dark.svg` & `light.svg`**: Terminal banners (1180×610) with Floyd-Steinberg dithered portrait, `profile.sh --live`, pulsing LIVE badge, handle pill, and `SYSTEM.INFO` panel.
- ⚙️ **`build_banner.py`**: The Python pipeline to regenerate banners anytime (e.g., if you place your own photo `photo.jpg` in this folder).
- 🐍 **`.github/workflows/snake.yml`**: The GitHub Actions workflow for the contribution snake using your exact color palette.
- 📄 **`README.md`**: The master profile README connecting all 4 phases.

---

## 🛠️ Step-by-Step Deployment Instructions

### Phase 0: The Profile Repository & Push

1. Go to [github.com/new](https://github.com/new).
2. Set **Repository name** to: `batman2400`
   - *GitHub will show a green banner: "✨ You found a secret! `batman2400/batman2400` is a special repository..."*
3. Set visibility to **Public** (required).
4. Do **NOT** check "Add a README file" (we will push our existing local repository with git).
5. Click **Create repository**.
6. In your terminal in this directory, run:
   ```powershell
   git remote add origin https://github.com/batman2400/batman2400.git
   git push -u origin main
   ```
   *(All files including `dark.svg`, `light.svg`, `.github/workflows/snake.yml`, and `README.md` will be pushed).*

---

### Phase 1: Banner Verification

The banner is embedded in `README.md` using a theme-aware `<picture>` tag:
- Automatically renders `dark.svg` on dark mode.
- Automatically renders `light.svg` on light mode.

**To test**: Toggle your GitHub appearance between Light and Dark in your GitHub settings (Avatar → Settings → Appearance) and verify both load.

> [!TIP]
> **Want to use your personal photo?**
> Simply save your head-and-shoulders picture as `photo.jpg` in this folder, run `python build_banner.py`, then `git commit -am "update portrait" && git push`.

---

### Phase 2: Stats Cards & Self-Hosting

The public instance of `github-readme-stats` is heavily shared and often hits `"API rate limit exceeded"`. Self-hosting gives you your own free, unlimited private instance:

1. **Create a GitHub Token**:
   - Go to [github.com/settings/tokens](https://github.com/settings/tokens) → **Tokens (classic)**.
   - Click **Generate new token (classic)**.
   - Note: `readme-stats` · Expiration: `No expiration`.
   - Scopes: Check the `repo` scope box.
   - Click **Generate token** and copy it immediately (it is only shown once).
2. **Fork and Deploy to Vercel**:
   - Fork [github.com/anuraghazra/github-readme-stats](https://github.com/anuraghazra/github-readme-stats).
   - Go to [vercel.com](https://vercel.com) → Sign up/in with GitHub (Hobby free plan).
   - Click **Add New...** → **Project** → Import your `github-readme-stats` fork.
   - Under **Environment Variables**, add:
     - Name: `PAT_1`
     - Value: `<your-copied-github-token>`
   - Click **Deploy** and wait ~2 minutes.
   - Copy your Vercel deployment URL (e.g. `your-instance.vercel.app`).
3. **Update README.md**:
   - In `README.md`, replace `github-readme-stats.vercel.app` with `your-instance.vercel.app`.

> [!NOTE]
> **Why `hide_rank=true`?**
> The letter grade is heavily weighted toward repository stars and followers, so newer accounts sit at "C" regardless of code volume or skill. Hiding it ensures an honest, focus-on-work profile presentation.

---

### Phase 3: Contribution Snake Action

The workflow file `.github/workflows/snake.yml` is already committed!

1. **Enable Actions Write Permissions**:
   - Go to your repository settings: `github.com/batman2400/batman2400/settings/actions`.
   - Scroll down to **Workflow permissions**.
   - Select **Read and write permissions**.
   - Click **Save**.
2. **Run the Workflow**:
   - Go to the **Actions** tab on your repository.
   - Click **Generate Snake Animation** on the left sidebar.
   - Click **Run workflow** → **Run workflow**.
   - The job will complete in ~1 minute and automatically push the SVGs to the `output` branch.
   - Once green, the snake animation will appear live in your profile!

---

### Phase 4: Social Badges

- Shields.io badges are styled with `for-the-badge` on background `#0A101F`.
- **The LinkedIn Rule**: Shields.io has a documented bug where the LinkedIn logo vanishes on custom colors. It is specifically set to brand blue `#0A66C2` to keep the icon visible.
- Update your handles/links for LinkedIn, Twitter, and Email in `README.md`.

---

## 🔍 Troubleshooting ("I changed it but nothing happened")

1. **CDN Caching**: GitHub caches raw SVGs aggressively. To check the live file, open:
   `https://raw.githubusercontent.com/batman2400/batman2400/main/dark.svg?v=999`
2. **Snake image broken**: The snake animation will only display *after* the GitHub Action runs green for the first time because the `output` branch is created by the action.
3. **Snake grid visibility**: The empty-cell color is set to `#2d3343` so it remains visible against GitHub's `#0d1117` background.
