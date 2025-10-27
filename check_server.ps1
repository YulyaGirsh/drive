# PowerShell скрипт для проверки сервера
$hostname = "89.23.99.152"
$username = "root"
$password = "dJN.wJ-YM*+J9b"

Write-Host "🔌 Подключение к серверу $hostname..." -ForegroundColor Green

# Команды для выполнения
$commands = @(
    "cd /home/easydrive && pwd",
    "cd /home/easydrive && git status",
    "ps aux | grep 'python.*server.py' | grep -v grep",
    "cd /home/easydrive && grep -n 'def init_tbank_payment' server.py",
    "cd /home/easydrive && git log --oneline -3"
)

# Подключаемся через ssh
$cmds = $commands -join " && "

Write-Host "Выполняем команды на сервере..." -ForegroundColor Yellow
ssh "$username@$hostname" $cmds

