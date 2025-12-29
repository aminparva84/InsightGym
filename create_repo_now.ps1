# Script to create GitHub repository using API
# This will create the repo and push the code

param(
    [string]$Token = $env:GITHUB_TOKEN
)

if (-not $Token) {
    Write-Host "GitHub Personal Access Token is required." -ForegroundColor Yellow
    Write-Host "You can create one at: https://github.com/settings/tokens" -ForegroundColor Cyan
    Write-Host "Required scopes: repo" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "You can either:" -ForegroundColor White
    Write-Host "1. Set environment variable: `$env:GITHUB_TOKEN = 'your-token'" -ForegroundColor Cyan
    Write-Host "2. Or run: .\create_repo_now.ps1 -Token 'your-token'" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}

$RepoName = "InsightGym"
$Username = "aminparva84"
$Description = "Raha Fitness - AI-powered fitness platform with Flask backend and React frontend"

$headers = @{
    Authorization = "Bearer $Token"
    Accept = "application/vnd.github.v3+json"
}

$body = @{
    name = $RepoName
    description = $Description
    private = $false
    auto_init = $false
} | ConvertTo-Json

try {
    Write-Host "Creating repository $RepoName on GitHub..." -ForegroundColor Yellow
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "✓ Repository created successfully!" -ForegroundColor Green
    Write-Host "Repository URL: $($response.html_url)" -ForegroundColor Cyan
    
    # Update remote URL to use token for authentication
    Write-Host "`nUpdating remote URL..." -ForegroundColor Yellow
    git remote remove origin 2>$null
    git remote add origin "https://$Token@github.com/$Username/$RepoName.git"
    
    # Push to main branch
    Write-Host "Pushing code to GitHub..." -ForegroundColor Yellow
    git push -u origin main
    
    # Update remote to remove token from URL (for security)
    git remote set-url origin "https://github.com/$Username/$RepoName.git"
    
    Write-Host "`n✅ SUCCESS! Your repository is now on GitHub!" -ForegroundColor Green
    Write-Host "Repository: $($response.html_url)" -ForegroundColor Cyan
    
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Authentication failed. Please check your token." -ForegroundColor Red
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        $errorResponse = $_.Exception.Response | ConvertFrom-Json
        if ($errorResponse.errors.message -like "*already exists*") {
            Write-Host "Repository already exists. Pushing code..." -ForegroundColor Yellow
            git remote remove origin 2>$null
            git remote add origin "https://$Token@github.com/$Username/$RepoName.git"
            git push -u origin main
            git remote set-url origin "https://github.com/$Username/$RepoName.git"
            Write-Host "✓ Code pushed successfully!" -ForegroundColor Green
        } else {
            Write-Host "Error details: $($errorResponse.message)" -ForegroundColor Red
        }
    }
}

