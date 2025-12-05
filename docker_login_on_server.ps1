# Скрипт для авторизации в Docker Hub на сервере
# Использование: .\docker_login_on_server.ps1

$SSH_HOST = "89.23.99.152"
$SSH_USER = "root"
$SSH_PASS = "dJN.wJ-YM*+J9b"
$PROJECT_DIR = "/home/easydrive"

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Авторизация в Docker Hub на сервере" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "ВНИМАНИЕ: Для авторизации нужен аккаунт Docker Hub" -ForegroundColor Yellow
Write-Host "Если у вас нет аккаунта, создайте бесплатный на https://hub.docker.com/" -ForegroundColor Yellow
Write-Host ""

$dockerUser = Read-Host "Введите логин Docker Hub"
$dockerPass = Read-Host "Введите пароль Docker Hub" -AsSecureString
$dockerPassPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto([Runtime.InteropServices.Marshal]::SecureStringToBSTR($dockerPass))

Write-Host ""
Write-Host "Подключение к серверу..." -ForegroundColor Yellow

# Проверка наличия plink
if (-not (Get-Command plink -ErrorAction SilentlyContinue)) {
    Write-Host "ОШИБКА: plink не найден в PATH" -ForegroundColor Red
    exit 1
}

# Функция для выполнения команды на сервере
function Execute-Remote {
    param([string]$Command)
    $plinkArgs = @("-ssh", "-batch", "-hostkey", "ssh-ed25519 255 SHA256:cOyZJNP542WHc1jfUVx+EZcCm/WelAy7fL2iA4LIYgs", "-pw", $SSH_PASS, "${SSH_USER}@${SSH_HOST}", $Command)
    & plink $plinkArgs
}

# Авторизация в Docker Hub
Write-Host "Авторизация в Docker Hub..." -ForegroundColor Yellow
$loginCmd = "echo '$dockerPassPlain' | docker login -u '$dockerUser' --password-stdin"
$loginResult = Execute-Remote $loginCmd

if ($loginResult -match "Login Succeeded|WARNING") {
    Write-Host "[OK] Авторизация успешна!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Запуск контейнеров..." -ForegroundColor Yellow
    $upResult = Execute-Remote "cd $PROJECT_DIR && (docker-compose up -d || docker compose up -d)"
    Write-Host $upResult
    
    Write-Host ""
    Write-Host "Проверка статуса..." -ForegroundColor Yellow
    Start-Sleep -Seconds 5
    Execute-Remote "cd $PROJECT_DIR && (docker-compose ps || docker compose ps)"
} else {
    Write-Host "[ОШИБКА] Не удалось авторизоваться" -ForegroundColor Red
    Write-Host $loginResult
}

# Очистка переменной с паролем
$dockerPassPlain = $null
$dockerPass = $null

