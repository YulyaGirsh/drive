# Скрипт для обновления сервера
$server = "89.23.99.152"
$username = "root"
$password = "dJN.wJ-YM*+J9b"

# Создаем команды для выполнения на сервере
$commands = @"
cd /home/easydrive
pwd
git status
git pull origin main
echo "Update completed"
"@

# Выполняем команды через SSH
Write-Host "Подключаемся к серверу $server..."
ssh -o StrictHostKeyChecking=no $username@$server $commands
