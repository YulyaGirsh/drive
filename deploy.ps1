# Автоматический скрипт деплоя для EasyDrive приложения (PowerShell)
# Автоматически пушит изменения в git и обновляет код на сервере

param(
    [switch]$Auto = $false
)

# Конфигурация сервера
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
        Write-ColorOutput "Выполняем: $Command" "Yellow"
        $result = Invoke-Expression $Command
        return $true, $result
    }
    catch {
        Write-ColorOutput "Ошибка: $($_.Exception.Message)" "Red"
        return $false, $_.Exception.Message
    }
}

function Git-AddAndCommit {
    Write-ColorOutput "📝 Добавляем изменения в git..." "Cyan"
    
    # Добавляем все файлы
    $success, $output = Run-Command "git add ."
    if (-not $success) {
        Write-ColorOutput "❌ Ошибка при добавлении файлов: $output" "Red"
        return $false
    }
    
    # Создаем коммит с текущим временем
    $timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
    $commitMessage = "Auto-deploy: $timestamp"
    
    $success, $output = Run-Command "git commit -m `"$commitMessage`""
    if (-not $success -and $output -notlike "*nothing to commit*") {
        Write-ColorOutput "❌ Ошибка при создании коммита: $output" "Red"
        return $false
    }
    
    Write-ColorOutput "✅ Изменения добавлены в git" "Green"
    return $true
}

function Git-Push {
    Write-ColorOutput "🚀 Отправляем изменения в git..." "Cyan"
    
    $success, $output = Run-Command "git push origin main"
    if (-not $success) {
        Write-ColorOutput "❌ Ошибка при push: $output" "Red"
        return $false
    }
    
    Write-ColorOutput "✅ Изменения отправлены в git" "Green"
    return $true
}

function Update-Server {
    Write-ColorOutput "🔄 Обновляем код на сервере..." "Cyan"
    
    # Команды для выполнения на сервере
    $commands = @(
        "cd $SERVER_PATH",
        "git pull origin main",
        "sudo systemctl reload nginx",
        "echo 'Deploy completed successfully'"
    )
    
    $sshCommand = "sshpass -p '$SERVER_PASSWORD' ssh -o StrictHostKeyChecking=no $SERVER_USER@$SERVER_HOST '$($commands -join ';')'"
    
    $success, $output = Run-Command $sshCommand
    if (-not $success) {
        Write-ColorOutput "❌ Ошибка при обновлении сервера: $output" "Red"
        return $false
    }
    
    Write-ColorOutput "✅ Сервер успешно обновлен" "Green"
    Write-ColorOutput "📋 Вывод сервера: $output" "Gray"
    return $true
}

function Check-Sshpass {
    $success, $output = Run-Command "where.exe sshpass"
    if (-not $success) {
        Write-ColorOutput "❌ sshpass не найден. Устанавливаем через WSL или Git Bash..." "Red"
        Write-ColorOutput "Установите sshpass в WSL: sudo apt-get install sshpass" "Yellow"
        return $false
    }
    return $true
}

function Start-AutoDeploy {
    Write-ColorOutput "👀 Запуск автоматического мониторинга изменений..." "Cyan"
    Write-ColorOutput "📁 Отслеживаемые файлы: .html, .css, .js, .py" "Gray"
    Write-ColorOutput "🔄 Деплой будет запускаться автоматически при изменениях" "Gray"
    Write-ColorOutput "⏹️  Для остановки нажмите Ctrl+C" "Gray"
    Write-ColorOutput ("-" * 60) "Gray"
    
    # Простой мониторинг файлов
    $watcher = New-Object System.IO.FileSystemWatcher
    $watcher.Path = Get-Location
    $watcher.Filter = "*.*"
    $watcher.IncludeSubdirectories = $true
    $watcher.EnableRaisingEvents = $true
    
    $lastDeploy = 0
    $deployDelay = 5
    
    $action = {
        $path = $Event.SourceEventArgs.FullPath
        $changeType = $Event.SourceEventArgs.ChangeType
        $currentTime = Get-Date -Format "HH:mm:ss"
        
        # Игнорируем служебные файлы
        if ($path -match '\.(pyc|pyo|pyd|log|tmp|swp|DS_Store)$' -or 
            $path -match '\.git|__pycache__|node_modules|\.vscode|\.idea') {
            return
        }
        
        $now = [DateTime]::Now.Ticks / 10000000
        if ($now - $lastDeploy -lt $deployDelay) {
            return
        }
        
        Write-ColorOutput "`n📁 Изменен файл: $path" "Yellow"
        Write-ColorOutput "⏰ Время: $currentTime" "Gray"
        
        $script:lastDeploy = $now
        
        # Запускаем деплой
        Write-ColorOutput "🚀 Запуск автоматического деплоя..." "Cyan"
        & $PSCommandPath
    }
    
    Register-ObjectEvent -InputObject $watcher -EventName "Changed" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Created" -Action $action
    Register-ObjectEvent -InputObject $watcher -EventName "Modified" -Action $action
    
    try {
        while ($true) {
            Start-Sleep -Seconds 1
        }
    }
    finally {
        $watcher.Dispose()
        Get-EventSubscriber | Unregister-Event
    }
}

# Основная функция
function Main {
    Write-ColorOutput "🚀 Запуск автоматического деплоя EasyDrive..." "Cyan"
    Write-ColorOutput "⏰ Время: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Gray"
    Write-ColorOutput ("-" * 50) "Gray"
    
    if ($Auto) {
        Start-AutoDeploy
        return
    }
    
    # Проверяем sshpass
    if (-not (Check-Sshpass)) {
        Write-ColorOutput "Установите sshpass для продолжения работы" "Red"
        exit 1
    }
    
    # Этап 1: Git операции
    if (-not (Git-AddAndCommit)) {
        Write-ColorOutput "⚠️ Нет изменений для коммита или ошибка git" "Yellow"
        return
    }
    
    if (-not (Git-Push)) {
        exit 1
    }
    
    # Этап 2: Обновление сервера
    if (-not (Update-Server)) {
        exit 1
    }
    
    Write-ColorOutput ("-" * 50) "Gray"
    Write-ColorOutput "🎉 Деплой завершен успешно!" "Green"
    Write-ColorOutput "⏰ Время завершения: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" "Gray"
}

# Запуск
Main
