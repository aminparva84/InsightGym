# PowerShell script to create GitHub repository and push code
# Usage: .\create_github_repo.ps1

param(
    [string]$RepoName = "InsightGym",
    [string]$Username = "aminparva84",
    [string]$Description = "Raha Fitness - AI-powered fitness platform with Flask backend and React frontend",
    [string]$Token = ""
)

# Check if token is provided
if (-not $Token) {
    Write-Host "GitHub Personal Access Token is required."
    Write-Host "You can create one at: https://github.com/settings/tokens"
    Write-Host "Required scopes: repo"
    $Token = Read-Host "Enter your GitHub Personal Access Token"
}

$headers = @{
    Authorization = "token $Token"
    Accept = "application/vnd.github.v3+json"
}

# Create repository
$body = @{
    name = $RepoName
    description = $Description
    private = $false
    auto_init = $false
} | ConvertTo-Json

try {
    Write-Host "Creating repository $RepoName on GitHub..."
    $response = Invoke-RestMethod -Uri "https://api.github.com/user/repos" -Headers $headers -Method Post -Body $body -ContentType "application/json"
    
    Write-Host "Repository created successfully!"
    Write-Host "Repository URL: $($response.html_url)"
    
    # Add remote and push
    Write-Host "`nSetting up remote and pushing code..."
    
    # Remove existing remote if any
    git remote remove origin 2>$null
    
    # Add remote
    git remote add origin "https://$Username@github.com/$Username/$RepoName.git"
    
    # Push to main branch
    Write-Host "Pushing code to GitHub..."
    git push -u origin main
    
    Write-Host "`n✅ Success! Your repository is now on GitHub:"
    Write-Host $response.html_url
    
} catch {
    Write-Host "Error: $($_.Exception.Message)"
    if ($_.Exception.Response.StatusCode -eq 401) {
        Write-Host "Authentication failed. Please check your token."
    } elseif ($_.Exception.Response.StatusCode -eq 422) {
        Write-Host "Repository might already exist. Trying to push anyway..."
        git remote remove origin 2>$null
        git remote add origin "https://$Username@github.com/$Username/$RepoName.git"
        git push -u origin main
    }
}



