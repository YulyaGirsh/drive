# Скрипт для обновления проекта на сервере
$server = "89.23.99.152"
$user = "root"
$password = "dJN.wJ-YM*+J9b"
$commands = @(
    "cd /var/www/easydrive",
    "git pull origin main",
    "sudo systemctl reload nginx",
    "echo 'Server updated successfully!'"
)

Write-Host "🚀 Обновляем проект на сервере $server..." -ForegroundColor Green

# Создаем временный файл с командами
$tempFile = [System.IO.Path]::GetTempFileName()
$commands | Out-File -FilePath $tempFile -Encoding ASCII

try {
    # Выполняем команды через SSH
    Write-Host "📡 Подключаемся к серверу..." -ForegroundColor Yellow
    
    # Используем ssh с передачей команд через stdin
    $process = Start-Process -FilePath "ssh" -ArgumentList @(
        "-o", "StrictHostKeyChecking=no",
        "-o", "UserKnownHostsFile=/dev/null",
        "$user@$server"
    ) -RedirectStandardInput -RedirectStandardOutput -RedirectStandardError -NoNewWindow -Wait -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "✅ Сервер успешно обновлен!" -ForegroundColor Green
    } else {
        Write-Host "❌ Ошибка при обновлении сервера" -ForegroundColor Red
        Write-Host "Код ошибки: $($process.ExitCode)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Ошибка: $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # Удаляем временный файл
    if (Test-Path $tempFile) {
        Remove-Item $tempFile -Force
    }
}

Write-Host "📋 Ручное обновление сервера:" -ForegroundColor Cyan
Write-Host "1. ssh root@89.23.99.152" -ForegroundColor White
Write-Host "2. cd /var/www/easydrive" -ForegroundColor White
Write-Host "3. git pull origin main" -ForegroundColor White
Write-Host "4. sudo systemctl reload nginx" -ForegroundColor White
Write-Host "Пароль: $password" -ForegroundColor Yellow