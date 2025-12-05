# Скрипт для ожидания и повторной попытки обновления
# Использование: .\wait_and_update.ps1

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Ожидание обновления лимита Docker Hub" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Лимит Docker Hub обновляется каждые 6 часов" -ForegroundColor Yellow
Write-Host "Рекомендуется подождать 30-60 минут" -ForegroundColor Yellow
Write-Host ""
Write-Host "Скрипт будет проверять каждые 10 минут..." -ForegroundColor Cyan
Write-Host "Нажмите Ctrl+C для отмены" -ForegroundColor Gray
Write-Host ""

$waitMinutes = 60  # Ждем 60 минут
$checkInterval = 10  # Проверяем каждые 10 минут

$elapsed = 0
while ($elapsed -lt $waitMinutes) {
    Write-Host "[$([DateTime]::Now.ToString('HH:mm:ss'))] Ожидание... (прошло $elapsed минут из $waitMinutes)" -ForegroundColor Gray
    Start-Sleep -Seconds ($checkInterval * 60)
    $elapsed += $checkInterval
    
    Write-Host ""
    Write-Host "Попытка обновления..." -ForegroundColor Yellow
    & powershell -ExecutionPolicy Bypass -File update_server_postgres.ps1
    
    # Проверяем, успешно ли запустились контейнеры
    $SSH_HOST = "89.23.99.152"
    $SSH_USER = "root"
    $SSH_PASS = "dJN.wJ-YM*+J9b"
    $PROJECT_DIR = "/home/easydrive"
    
    if (Get-Command plink -ErrorAction SilentlyContinue) {
        $plinkArgs = @("-ssh", "-batch", "-hostkey", "ssh-ed25519 255 SHA256:cOyZJNP542WHc1jfUVx+EZcCm/WelAy7fL2iA4LIYgs", "-pw", $SSH_PASS, "${SSH_USER}@${SSH_HOST}", "cd $PROJECT_DIR && docker-compose ps 2>/dev/null | grep -q postgres && echo 'OK' || echo 'FAIL'")
        $result = & plink $plinkArgs
        
        if ($result -match "OK") {
            Write-Host ""
            Write-Host "=========================================" -ForegroundColor Green
            Write-Host "УСПЕХ! Контейнеры запущены!" -ForegroundColor Green
            Write-Host "=========================================" -ForegroundColor Green
            break
        }
    }
}

if ($elapsed -ge $waitMinutes) {
    Write-Host ""
    Write-Host "Время ожидания истекло. Попробуйте:" -ForegroundColor Yellow
    Write-Host "1. Зарегистрироваться в Docker Hub (бесплатно): https://hub.docker.com/" -ForegroundColor Cyan
    Write-Host "2. Или подождите еще немного и запустите: .\update_server_postgres.ps1" -ForegroundColor Cyan
}

