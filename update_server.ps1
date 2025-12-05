# Скрипт для автоматического обновления проекта на сервере (PowerShell)
# Использование: .\update_server.ps1

$ErrorActionPreference = "Stop"

$SSH_HOST = "89.23.99.152"
$SSH_USER = "root"
$SSH_PASS = "dJN.wJ-YM*+J9b"
$PROJECT_DIR = "/home/easydrive"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Обновление проекта на сервере" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Сервер: ${SSH_USER}@${SSH_HOST}" -ForegroundColor Yellow
Write-Host ""

# Проверка наличия ssh или plink
$sshCommand = $null
if (Get-Command ssh -ErrorAction SilentlyContinue) {
    $sshCommand = "ssh"
} elseif (Get-Command plink -ErrorAction SilentlyContinue) {
    $sshCommand = "plink"
} else {
    Write-Host "ОШИБКА: ssh или plink не найден в PATH" -ForegroundColor Red
    Write-Host "Установите OpenSSH или PuTTY" -ForegroundColor Yellow
    exit 1
}

# Функция для выполнения команды на сервере
function Execute-Remote {
    param([string]$Command)
    
    if ($sshCommand -eq "ssh") {
        # Используем sshpass через WSL или установленный sshpass
        $fullCommand = "echo '$SSH_PASS' | sshpass -p '$SSH_PASS' ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${SSH_USER}@${SSH_HOST} `"$Command`""
        Invoke-Expression $fullCommand
    } else {
        # Используем plink
        $plinkArgs = @("-ssh", "-batch", "-pw", $SSH_PASS, "${SSH_USER}@${SSH_HOST}", $Command)
        & plink $plinkArgs
    }
}

Write-Host "1. Подключение к серверу..." -ForegroundColor Yellow
try {
    Execute-Remote "echo 'Подключение успешно'" | Out-Null
    Write-Host "[OK] Подключение установлено" -ForegroundColor Green
} catch {
    Write-Host "ОШИБКА: Не удалось подключиться к серверу" -ForegroundColor Red
    exit 1
}
Write-Host ""

Write-Host "2. Обновление кода из репозитория..." -ForegroundColor Yellow
$gitCommand = @"
cd $PROJECT_DIR && \
if [ -d .git ]; then \
    if [ -n \"\$(git status --porcelain 2>/dev/null)\" ]; then \
        git stash; \
    fi; \
    git pull origin main; \
else \
    git init && \
    git remote add origin https://github.com/YulyaGirsh/drive.git 2>/dev/null || true && \
    git pull origin main; \
fi
"@
Execute-Remote $gitCommand
Write-Host "[OK] Код обновлен" -ForegroundColor Green
Write-Host ""

Write-Host "3. Остановка старых процессов..." -ForegroundColor Yellow
$stopCommand = @"
cd $PROJECT_DIR && \
OLD_PID=\$(lsof -t -i:8000 2>/dev/null || true) && \
if [ ! -z \"\$OLD_PID\" ]; then \
    kill \$OLD_PID 2>/dev/null || true; \
    sleep 2; \
fi && \
SERVER_PIDS=\$(ps aux | grep 'server.py' | grep -v grep | awk '{print \$2}' || true) && \
if [ ! -z \"\$SERVER_PIDS\" ]; then \
    echo \"\$SERVER_PIDS\" | xargs -r kill 2>/dev/null || true; \
    sleep 2; \
fi
"@
Execute-Remote $stopCommand
Write-Host "[OK] Старые процессы остановлены" -ForegroundColor Green
Write-Host ""

Write-Host "4. Остановка старых Docker контейнеров..." -ForegroundColor Yellow
$dockerDownCommand = @"
cd $PROJECT_DIR && \
if command -v docker-compose >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker-compose'; \
elif docker compose version >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker compose'; \
else \
    echo 'Docker Compose не найден'; \
    exit 1; \
fi && \
\$DOCKER_COMPOSE down 2>/dev/null || true
"@
Execute-Remote $dockerDownCommand
Write-Host "[OK] Docker контейнеры остановлены" -ForegroundColor Green
Write-Host ""

Write-Host "5. Сборка Docker образов..." -ForegroundColor Yellow
$dockerBuildCommand = @"
cd $PROJECT_DIR && \
if command -v docker-compose >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker-compose'; \
elif docker compose version >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker compose'; \
else \
    exit 1; \
fi && \
\$DOCKER_COMPOSE build --no-cache
"@
Execute-Remote $dockerBuildCommand
Write-Host "[OK] Образы собраны" -ForegroundColor Green
Write-Host ""

Write-Host "6. Запуск Docker контейнеров..." -ForegroundColor Yellow
$dockerUpCommand = @"
cd $PROJECT_DIR && \
if command -v docker-compose >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker-compose'; \
elif docker compose version >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker compose'; \
else \
    exit 1; \
fi && \
\$DOCKER_COMPOSE up -d
"@
Execute-Remote $dockerUpCommand
Write-Host "[OK] Контейнеры запущены" -ForegroundColor Green
Write-Host ""

Write-Host "7. Ожидание запуска сервисов..." -ForegroundColor Yellow
Start-Sleep -Seconds 10

Write-Host "8. Проверка статуса контейнеров..." -ForegroundColor Yellow
$statusCommand = @"
cd $PROJECT_DIR && \
if command -v docker-compose >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker-compose'; \
elif docker compose version >/dev/null 2>&1; then \
    DOCKER_COMPOSE='docker compose'; \
else \
    DOCKER_COMPOSE='docker compose'; \
fi && \
echo '=== Статус контейнеров ===' && \
\$DOCKER_COMPOSE ps && \
echo '' && \
echo '=== Последние логи (30 строк) ===' && \
\$DOCKER_COMPOSE logs --tail=30
"@
Execute-Remote $statusCommand
Write-Host ""

Write-Host "9. Проверка работы сервера..." -ForegroundColor Yellow
Start-Sleep -Seconds 5
$healthCheck = Execute-Remote "curl -s http://localhost:8000/api/v2/heartbeat >/dev/null 2>&1 && echo 'OK' || echo 'WAIT'"
if ($healthCheck -match "OK") {
    Write-Host "[OK] Сервер работает!" -ForegroundColor Green
    Execute-Remote "curl -s http://localhost:8000/api/v2/heartbeat"
} else {
    Write-Host "[INFO] Сервер еще запускается..." -ForegroundColor Yellow
    Write-Host "Проверьте логи на сервере: docker-compose logs -f" -ForegroundColor Cyan
}

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Обновление завершено!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Полезные команды для работы на сервере:" -ForegroundColor Yellow
Write-Host "  ssh ${SSH_USER}@${SSH_HOST}"
Write-Host "  cd $PROJECT_DIR"
Write-Host "  docker-compose ps          - статус контейнеров"
Write-Host "  docker-compose logs -f     - просмотр логов"
Write-Host "  docker-compose restart     - перезапуск"
Write-Host "  docker-compose down        - остановка"
