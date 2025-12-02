# Simple deploy script for EasyDrive (PowerShell)
# Uses built-in Windows capabilities for SSH

param(
    [switch]$Auto = $false
)

# Server configuration
$SERVER_HOST = "89.23.99.152"
$SERVER_USER = "root"
$SERVER_PASSWORD = "dJN.wJ-YM*+J9b"
$SERVER_PATH = "/var/www/easydrive"

function Write-ColorOutput {
    param(
        [string]$Message,
        [string]$Color = "White"
    )
    Write-Host $Message -ForegroundColor $Color
}

function Run-Command {
    param(
        [string]$Command,
        [string]$WorkingDirectory = (Get-Location)
    )
    
    try {
        Write-ColorOutput "Executing: $Command" "Yellow"
        $result = Invoke-Expression $Command
        return $true, $result
    }
    catch {
        Write-ColorOutput "Error: $($_.Exception.Message)" "Red"
        return $false, $_.Exception.Message
    }
}

function Git-AddAndCommit {
    Write-ColorOutput "Adding changes to git..." "Cyan"
    
    # Add all files
    $success, $output = Run-Command "git add ."
    if (-not $success) {
        Write-ColorOutput "Error adding files: $output" "Red"
        return $false
    }
    
    # Create commit with current time
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "Auto-deploy: $timestamp"
    
    $success, $output = Run-Command "git commit -m `"$commitMessage`""
    if (-not $success -and $output -notlike "*nothing to commit*") {
        Write-ColorOutput "Error creating commit: $output" "Red"
        return $false
    }
    
    Write-ColorOutput "Changes added to git" "Green"
    return $true
}

function Git-Push {
    Write-ColorOutput "Pushing changes to git..." "Cyan"
    
    $success, $output = Run-Command "git push origin main"
    if (-not $success) {
        Write-ColorOutput "Error pushing: $output" "Red"
        return $false
    }
    
    Write-ColorOutput "Changes pushed to git" "Green"
    return $true
}

function Show-ManualInstructions {
    Write-ColorOutput "MANUAL SERVER UPDATE:" "Yellow"
    Write-ColorOutput "1. Connect to server:" "White"
    Write-ColorOutput "   ssh $SERVER_USER@$SERVER_HOST" "Gray"
    Write-ColorOutput "2. Go to project folder:" "White"
    Write-ColorOutput "   cd $SERVER_PATH" "Gray"
    Write-ColorOutput "3. Update code:" "White"
    Write-ColorOutput "   git pull origin main" "Gray"
    Write-ColorOutput "4. Reload nginx:" "White"
    Write-ColorOutput "   sudo systemctl reload nginx" "Gray"
    Write-ColorOutput "" "White"
    Write-ColorOutput "Password: $SERVER_PASSWORD" "Yellow"
}

function Main {
    Write-ColorOutput "Starting EasyDrive auto-deploy..." "Cyan"
    Write-ColorOutput "Time: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Gray"
    Write-ColorOutput ("-" * 50) "Gray"
    
    # Stage 1: Git operations
    if (-not (Git-AddAndCommit)) {
        Write-ColorOutput "No changes to commit or git error" "Yellow"
        return
    }
    
    if (-not (Git-Push)) {
        exit 1
    }
    
    # Stage 2: Manual instructions
    Write-ColorOutput ("-" * 50) "Gray"
    Write-ColorOutput "Git push completed successfully!" "Green"
    Write-ColorOutput "Please update server manually:" "Yellow"
    Write-ColorOutput "" "White"
    Show-ManualInstructions
}

# Run
Main
