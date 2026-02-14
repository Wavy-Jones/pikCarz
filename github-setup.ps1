# ============================================
# pikCarz — GitHub Setup Script
# Powered by Cubeas | INFNT Solutions
# ============================================
# HOW TO RUN:
#   Right-click this file -> "Run with PowerShell"
#   OR open PowerShell in this folder and type:
#   .\github-setup.ps1
# ============================================

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  pikCarz -- GitHub Repository Setup" -ForegroundColor Cyan
Write-Host "  Powered by Cubeas | INFNT Solutions" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── Pre-filled details ────────────────────────
$githubUsername = "wavy-jones"
$repoName       = "pikcarz"
$repoVisibility = "public"
$remoteUrl      = "https://github.com/$githubUsername/$repoName.git"
$commitMessage  = "Initial commit - pikCarz frontend v1.0"

Write-Host "  GitHub User : $githubUsername" -ForegroundColor White
Write-Host "  Repo Name   : $repoName" -ForegroundColor White
Write-Host "  Visibility  : $repoVisibility" -ForegroundColor White
Write-Host "  Remote URL  : $remoteUrl" -ForegroundColor White
Write-Host ""

# ── Step 1: Git Init & First Commit ──────────
Write-Host "[1/4] Initialising git repository..." -ForegroundColor Green
git init
if ($LASTEXITCODE -ne 0) { Write-Host "ERROR: git init failed." -ForegroundColor Red; pause; exit }

Write-Host ""
Write-Host "[2/4] Staging all files..." -ForegroundColor Green
git add .

Write-Host ""
Write-Host "[3/4] Creating first commit..." -ForegroundColor Green
git commit -m $commitMessage
git branch -M main
git remote add origin $remoteUrl

# ── Step 2: Create repo on GitHub ────────────
Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host " ACTION REQUIRED: Create the GitHub repo " -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host " 1. This will open GitHub in your browser." -ForegroundColor White
Write-Host " 2. Fill in:" -ForegroundColor White
Write-Host "      Repository name : pikcarz" -ForegroundColor Yellow
Write-Host "      Visibility       : Public" -ForegroundColor Yellow
Write-Host "      (Do NOT tick 'Add a README file')" -ForegroundColor Red
Write-Host " 3. Click 'Create repository'" -ForegroundColor White
Write-Host " 4. Come back here and press Y" -ForegroundColor White
Write-Host ""

# Open GitHub new repo page in browser
Start-Process "https://github.com/new"

$ready = Read-Host "Done creating the repo on GitHub? (Y/N)"

if ($ready -eq "Y" -or $ready -eq "y") {
    Write-Host ""
    Write-Host "[4/4] Pushing to GitHub..." -ForegroundColor Green
    Write-Host "(If prompted for credentials, sign in with your GitHub account)" -ForegroundColor Yellow
    Write-Host ""
    git push -u origin main

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "========================================" -ForegroundColor Green
        Write-Host "  SUCCESS! pikCarz is now on GitHub!" -ForegroundColor Green
        Write-Host "========================================" -ForegroundColor Green
        Write-Host ""
        Write-Host "  Repo URL  : https://github.com/wavy-jones/pikcarz" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "  -- Enable GitHub Pages for a free live URL --" -ForegroundColor Cyan
        Write-Host "  1. Go to your repo on GitHub" -ForegroundColor White
        Write-Host "  2. Settings -> Pages" -ForegroundColor White
        Write-Host "  3. Source: Deploy from branch -> main -> / (root)" -ForegroundColor White
        Write-Host "  4. Save -> wait 1-2 mins" -ForegroundColor White
        Write-Host "  5. Live at: https://wavy-jones.github.io/pikcarz" -ForegroundColor Yellow
        Write-Host ""
        Start-Process "https://github.com/wavy-jones/pikcarz"
    } else {
        Write-Host ""
        Write-Host "Push failed. Try running manually:" -ForegroundColor Red
        Write-Host "  git push -u origin main" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "If you get an authentication error, run:" -ForegroundColor Yellow
        Write-Host "  git config --global credential.helper manager" -ForegroundColor Cyan
        Write-Host "Then try pushing again." -ForegroundColor Yellow
    }
} else {
    Write-Host ""
    Write-Host "Skipped. Run this when ready:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "Press any key to close..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
