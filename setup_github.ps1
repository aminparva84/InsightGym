# Quick setup script for GitHub repository
# This will guide you through creating the repo and pushing code

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "GitHub Repository Setup for InsightGym" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if remote is already set
$remote = git remote get-url origin 2>$null
if ($remote) {
    Write-Host "✓ Remote already configured: $remote" -ForegroundColor Green
} else {
    Write-Host "Setting up remote..." -ForegroundColor Yellow
    git remote add origin https://github.com/aminparva84/InsightGym.git
    Write-Host "✓ Remote configured" -ForegroundColor Green
}

Write-Host ""
Write-Host "To complete the setup, you need to:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Create the repository on GitHub:" -ForegroundColor White
Write-Host "   - Go to: https://github.com/new" -ForegroundColor Cyan
Write-Host "   - Repository name: InsightGym" -ForegroundColor Cyan
Write-Host "   - Description: Raha Fitness - AI-powered fitness platform" -ForegroundColor Cyan
Write-Host "   - Choose Public or Private" -ForegroundColor Cyan
Write-Host "   - DO NOT initialize with README" -ForegroundColor Red
Write-Host "   - Click 'Create repository'" -ForegroundColor Cyan
Write-Host ""
Write-Host "2. After creating the repo, run this command:" -ForegroundColor White
Write-Host "   git push -u origin main" -ForegroundColor Green
Write-Host ""
Write-Host "OR use the automated script (requires GitHub token):" -ForegroundColor White
Write-Host "   .\create_github_repo.ps1" -ForegroundColor Green
Write-Host ""

$create = Read-Host "Do you want to create the repo now using GitHub API? (y/n)"
if ($create -eq 'y' -or $create -eq 'Y') {
    Write-Host ""
    Write-Host "You'll need a GitHub Personal Access Token." -ForegroundColor Yellow
    Write-Host "Get one at: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "Required scope: repo" -ForegroundColor Yellow
    Write-Host ""
    $token = Read-Host "Enter your GitHub Personal Access Token" -AsSecureString
    $tokenPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($token))
    
    $headers = @{
        Authorization = "token $tokenPlain"
        Accept = "application/vnd.github.v3+json"
    }
    
    $body = @{
        name = "InsightGym"
        description = "Raha Fitness - AI-powered fitness platform with Flask backend and React frontend"
        private = $false
    } | ConvertTo-Json
    
    try {
        Write-Host "Creating repository..." -ForegroundColor Yellow
        $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
        Write-Host "✓ Repository created successfully!" -ForegroundColor Green
        Write-Host "  URL: $($response.html_url)" -ForegroundColor Cyan
        
        Write-Host ""
        Write-Host "Pushing code..." -ForegroundColor Yellow
        git push -u origin main
        
        Write-Host ""
        Write-Host "✓✓✓ SUCCESS! Your code is now on GitHub! ✓✓✓" -ForegroundColor Green
        Write-Host "Repository: $($response.html_url)" -ForegroundColor Cyan
        
    } catch {
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        if ($_.Exception.Response.StatusCode -eq 422) {
            Write-Host "Repository might already exist. Trying to push..." -ForegroundColor Yellow
            git push -u origin main
        } elseif ($_.Exception.Response.StatusCode -eq 401) {
            Write-Host "Authentication failed. Please check your token." -ForegroundColor Red
        }
    }
} else {
    Write-Host ""
    Write-Host "When you're ready, create the repo on GitHub and run:" -ForegroundColor Yellow
    Write-Host "  git push -u origin main" -ForegroundColor Green
}



