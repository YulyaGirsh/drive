# Скрипт для обновления проекта на сервере с PostgreSQL
# Использование: .\update_server_postgres.ps1

$SSH_HOST = "89.23.99.152"
$SSH_USER = "root"
$SSH_PASS = "dJN.wJ-YM*+J9b"
$PROJECT_DIR = "/home/easydrive"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Обновление проекта на сервере (PostgreSQL)" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Сервер: ${SSH_USER}@${SSH_HOST}" -ForegroundColor Yellow
Write-Host ""

# Проверка наличия plink
if (-not (Get-Command plink -ErrorAction SilentlyContinue)) {
    Write-Host "ОШИБКА: plink не найден в PATH" -ForegroundColor Red
    Write-Host "Установите PuTTY: https://www.chiark.greenend.org.uk/~sgtatham/putty/" -ForegroundColor Yellow
    exit 1
}

# Функция для выполнения команды на сервере
function Execute-Remote {
    param([string]$Command)
    $plinkArgs = @("-ssh", "-batch", "-hostkey", "ssh-ed25519 255 SHA256:cOyZJNP542WHc1jfUVx+EZcCm/WelAy7fL2iA4LIYgs", "-pw", $SSH_PASS, "${SSH_USER}@${SSH_HOST}", $Command)
    & plink $plinkArgs
}

Write-Host "1. Подключение к серверу..." -ForegroundColor Yellow
try {
    Execute-Remote "echo 'OK'" | Out-Null
    Write-Host "[OK] Подключение установлено" -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: Не удалось подключиться к серверу" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "2. Обновление кода из репозитория..." -ForegroundColor Yellow
$gitOutput = Execute-Remote "cd $PROJECT_DIR && git pull origin main 2>&1"
Write-Host $gitOutput
if ($gitOutput -match "Already up to date|Fast-forward|Updating") {
    Write-Host "[OK] Код обновлен" -ForegroundColor Green
} else {
    Write-Host "[INFO] Проверка статуса git..." -ForegroundColor Yellow
    Execute-Remote "cd $PROJECT_DIR && git status"
}
Write-Host ""

Write-Host "3. Проверка наличия образа PostgreSQL..." -ForegroundColor Yellow
$imageCheck = Execute-Remote "docker images postgres:15-alpine --format '{{.Repository}}:{{.Tag}}'"
if ($imageCheck -match "postgres:15-alpine") {
    Write-Host "[OK] Образ PostgreSQL уже есть на сервере" -ForegroundColor Green
} else {
    Write-Host "[WARNING] Образ PostgreSQL не найден" -ForegroundColor Yellow
    Write-Host "Попытка скачать образ..." -ForegroundColor Yellow
    $pullResult = Execute-Remote "cd $PROJECT_DIR && docker pull postgres:15-alpine 2>&1"
    Write-Host $pullResult
    if ($pullResult -match "rate limit|pull rate limit") {
        Write-Host "" -ForegroundColor Red
        Write-Host "=========================================" -ForegroundColor Red
        Write-Host "ОШИБКА: Лимит Docker Hub исчерпан!" -ForegroundColor Red
        Write-Host "=========================================" -ForegroundColor Red
        Write-Host ""
        Write-Host "Решения:" -ForegroundColor Yellow
        Write-Host "1. Авторизуйтесь в Docker Hub на сервере:" -ForegroundColor Cyan
        Write-Host "   ssh ${SSH_USER}@${SSH_HOST}" -ForegroundColor White
        Write-Host "   docker login" -ForegroundColor White
        Write-Host "   cd $PROJECT_DIR && docker-compose up -d" -ForegroundColor White
        Write-Host ""
        Write-Host "2. Подождите 30-60 минут и повторите:" -ForegroundColor Cyan
        Write-Host "   .\update_server_postgres.ps1" -ForegroundColor White
        Write-Host ""
        exit 1
    }
}
Write-Host ""

Write-Host "4. Остановка старых процессов..." -ForegroundColor Yellow
Execute-Remote "cd $PROJECT_DIR && pkill -f server.py 2>/dev/null || true; lsof -ti:8000 | xargs kill 2>/dev/null || true"
Write-Host "[OK] Старые процессы остановлены" -ForegroundColor Green
Write-Host ""

Write-Host "5. Остановка старых Docker контейнеров..." -ForegroundColor Yellow
Execute-Remote "cd $PROJECT_DIR && (docker-compose down 2>/dev/null || docker compose down 2>/dev/null || true)"
Write-Host "[OK] Docker контейнеры остановлены" -ForegroundColor Green
Write-Host ""

Write-Host "6. Сборка Docker образа приложения..." -ForegroundColor Yellow
$buildOutput = Execute-Remote "cd $PROJECT_DIR && (docker-compose build --no-cache easydrive-server 2>&1 || docker compose build --no-cache easydrive-server 2>&1)"
if ($buildOutput -match "Successfully built|DONE") {
    Write-Host "[OK] Образ приложения собран" -ForegroundColor Green
} else {
    Write-Host $buildOutput
}
Write-Host ""

Write-Host "7. Запуск Docker контейнеров..." -ForegroundColor Yellow
$upOutput = Execute-Remote "cd $PROJECT_DIR && (docker-compose up -d 2>&1 || docker compose up -d 2>&1)"
Write-Host $upOutput
if ($upOutput -match "Creating|Started|Up") {
    Write-Host "[OK] Контейнеры запущены" -ForegroundColor Green
} elseif ($upOutput -match "rate limit|pull rate limit") {
    Write-Host "" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host "ОШИБКА: Лимит Docker Hub при запуске!" -ForegroundColor Red
    Write-Host "=========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Решения:" -ForegroundColor Yellow
    Write-Host "1. Авторизуйтесь в Docker Hub:" -ForegroundColor Cyan
    Write-Host "   ssh ${SSH_USER}@${SSH_HOST}" -ForegroundColor White
    Write-Host "   docker login" -ForegroundColor White
    Write-Host "   cd $PROJECT_DIR && docker-compose up -d" -ForegroundColor White
    Write-Host ""
    Write-Host "2. Или подождите 30-60 минут" -ForegroundColor Cyan
    Write-Host ""
    exit 1
}
Write-Host ""

Write-Host "8. Ожидание запуска сервисов..." -ForegroundColor Yellow
Start-Sleep -Seconds 15

Write-Host "9. Проверка статуса контейнеров..." -ForegroundColor Yellow
$status = Execute-Remote "cd $PROJECT_DIR && (docker-compose ps || docker compose ps)"
Write-Host $status
Write-Host ""

Write-Host "10. Проверка логов PostgreSQL..." -ForegroundColor Yellow
$pgLogs = Execute-Remote "cd $PROJECT_DIR && (docker-compose logs --tail=10 postgres 2>/dev/null || docker compose logs --tail=10 postgres 2>/dev/null || echo 'PostgreSQL контейнер не запущен')"
Write-Host $pgLogs
Write-Host ""

Write-Host "11. Проверка работы сервера..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$result = Execute-Remote "curl -s http://localhost:8000/api/v2/heartbeat 2>/dev/null || echo 'WAIT'"
if ($result -match "success|ok|heartbeat") {
    Write-Host "[OK] Сервер работает!" -ForegroundColor Green
    Write-Host $result
} else {
    Write-Host "[INFO] Сервер еще запускается или есть проблемы..." -ForegroundColor Yellow
    Write-Host "Проверьте логи: ssh ${SSH_USER}@${SSH_HOST} 'cd $PROJECT_DIR && docker-compose logs -f'" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Обновление завершено!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Полезные команды:" -ForegroundColor Yellow
Write-Host "  ssh ${SSH_USER}@${SSH_HOST}" -ForegroundColor White
Write-Host "  cd $PROJECT_DIR" -ForegroundColor White
Write-Host "  docker-compose ps          - статус контейнеров" -ForegroundColor White
Write-Host "  docker-compose logs -f     - просмотр логов" -ForegroundColor White
Write-Host "  docker-compose restart     - перезапуск" -ForegroundColor White

