# Настройка оплаты через Т-банк терминал

## 1. Настройка в Т-банке

### В личном кабинете Т-банка укажите:

**Webhook URL:**
```
https://hochupravaeasy.ru/api/tbank-webhook
```

**Success URL:**
```
https://hochupravaeasy.ru/success
```

**Fail URL:**
```
https://hochupravaeasy.ru/fail
```

## 2. Настройка на сервере

### Запуск webhook сервера:

```bash
# Перейти в директорию проекта
cd /home/easydrive

# Обновить код
git pull origin main

# Сделать скрипт исполняемым
chmod +x start_webhook.sh

# Запустить webhook сервер
./start_webhook.sh
```

### Обновление nginx конфигурации:

```bash
# Скопировать новую конфигурацию
sudo cp nginx_webhook_config.conf /etc/nginx/sites-available/easydrive

# Перезагрузить nginx
sudo systemctl reload nginx
```

## 3. Как работает система

### Процесс оплаты:

1. **Пользователь нажимает "💳 Оплатить 10₽"**
2. **Создается платеж через Т-банк API**
3. **Открывается страница оплаты Т-банка**
4. **Пользователь оплачивает через терминал**
5. **Т-банк отправляет webhook на сервер**
6. **Webhook сервер обрабатывает платеж**
7. **Отправляется уведомление в Telegram**
8. **Подписка активируется автоматически**

### Fallback (если API не работает):

1. **Показываются реквизиты для ручной оплаты**
2. **Пользователь оплачивает по реквизитам**
3. **Нажимает "Подтвердить оплату"**
4. **Отправляется уведомление в Telegram**
5. **Подписка активируется**

## 4. Мониторинг

### Проверка webhook сервера:

```bash
# Проверить статус
ps aux | grep webhook_server.py

# Посмотреть логи
tail -f webhook.log

# Проверить порт
netstat -tlnp | grep 8001
```

### Тестирование webhook:

```bash
curl -X POST https://hochupravaeasy.ru/api/tbank-webhook \
  -H "Content-Type: application/json" \
  -d '{"status": "success", "order_id": "test_123", "amount": 1000}'
```

## 5. Преимущества

- ✅ **Полная интеграция с Т-банк терминалом**
- ✅ **Автоматическая активация подписки**
- ✅ **Уведомления в Telegram**
- ✅ **Fallback на ручную оплату**
- ✅ **Не зависит от основного приложения**
