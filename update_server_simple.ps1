# Простой скрипт для обновления проекта на сервере
Write-Host "🚀 Обновляем проект EasyDrive на сервере..." -ForegroundColor Green
Write-Host ""
Write-Host "📋 Выполните следующие команды вручную:" -ForegroundColor Yellow
Write-Host ""
Write-Host "1. Подключитесь к серверу:" -ForegroundColor Cyan
Write-Host "   ssh root@89.23.99.152" -ForegroundColor White
Write-Host ""
Write-Host "2. Введите пароль:" -ForegroundColor Cyan
Write-Host "   dJN.wJ-YM*+J9b" -ForegroundColor Yellow
Write-Host ""
Write-Host "3. Перейдите в папку проекта:" -ForegroundColor Cyan
Write-Host "   cd /var/www/easydrive" -ForegroundColor White
Write-Host ""
Write-Host "4. Обновите код из GitHub:" -ForegroundColor Cyan
Write-Host "   git pull origin main" -ForegroundColor White
Write-Host ""
Write-Host "5. Перезагрузите nginx:" -ForegroundColor Cyan
Write-Host "   sudo systemctl reload nginx" -ForegroundColor White
Write-Host ""
Write-Host "6. Проверьте статус:" -ForegroundColor Cyan
Write-Host "   sudo systemctl status nginx" -ForegroundColor White
Write-Host ""
Write-Host "✅ После выполнения всех команд проект будет обновлен!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Проверьте работу сайта по адресу:" -ForegroundColor Blue
Write-Host "   http://89.23.99.152" -ForegroundColor White
