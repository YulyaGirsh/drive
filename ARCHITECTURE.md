# 🏗️ Архитектура системы оплаты EasyDrive

## 📊 Поток данных

```
┌─────────────┐
│   Браузер   │ 
│ videos.html │
└──────┬──────┘
       │ POST /api/tbank-init-payment
       ▼
┌─────────────┐
│  server.py  │ ──► Генерирует токен
└──────┬──────┘      (SHA-256 + сортировка)
       │ POST https://rest-api-test.tinkoff.ru/v2/Init
       ▼
┌─────────────┐
│  Т-Банк API │ ──► Проверяет токен
└──────┬──────┘      Отправляет ответ
       │
       ▼
┌─────────────┐
│  Браузер    │ ──► Сохраняет подписку
└─────────────┘      в localStorage
```

## 🔑 Ключевые файлы

| Файл | Роль | Содержание |
|------|------|------------|
| `videos.html` | Фронтенд | UI + отправка данных в бэкенд (БЕЗ секретов!) |
| `server.py` | Бэкенд | Принимает запросы, генерирует токен, отправляет в Т-банк |
| `tbank_payment.py` | Модуль | Класс TbankPayment + генерация токена |
| `tbank_config.py` | Конфигурация | Загрузка переменных из config.env |
| `config.env` | Секреты | TerminalKey, SecretKey (НЕ в Git!) |

## 🔐 Где хранятся секреты?

- ❌ **НЕ в `videos.html`** - туда попадают только публичные ключи
- ✅ **В `config.env`** - только на сервере
- ✅ **В `server.py`** - при генерации токена

## 🎯 Текущая конфигурация

### Тестовый терминал (в config.env):
```
TBANK_TERMINAL_KEY=1761136519162DEMO
TBANK_SECRET_KEY=TY#iAnEUV*3CS&BI
ТЕСТОВЫЙ ХОСТ: https://rest-api-test.tinkoff.ru/v2
```

### Запрос от фронтенда (videos.html):
```javascript
const data = {
    TerminalKey: '1761136519162DEMO',
    Amount: 1000,
    OrderId: 'easydrive_123_1699...',
    Description: 'Подписка на видеоуроки EasyDrive',
    SuccessURL: 'https://hochupravaeasy.ru/success',
    FailURL: 'https://hochupravaeasy.ru/fail',
    Language: 'ru',
    CustomerKey: '123'
}
```

### На бэкенде (server.py):
```python
# Генерируем токен (с секретом!)
token = payment._create_simple_token(tbank_data)

# Добавляем токен к данным
tbank_data['Token'] = token

# Отправляем в Т-банк
urlopen('https://rest-api-test.tinkoff.ru/v2/Init', data)
```

## ✅ Чеклист безопасности

- [x] SecretKey НЕ в браузере
- [x] Генерация токена только на бэкенде
- [x] Все запросы идут через /api/tbank-init-payment
- [x] Конфиг не в Git (.gitignore)
- [x] Используем тестовый хост

## 🧪 Как протестировать

1. Откройте: https://hochupravaeasy.ru/videos.html
2. Нажмите 3-й видеоурок
3. Введите карту: `4000 0000 0000 0119` (Срок: `12/30`, Код: `111`)
4. Проверьте логи в консоли

## 📝 Алгоритм генерации токена:

```python
def _create_simple_token(data):
    # 1. Убираем Token и вложенные объекты
    token_data = {k: v for k, v in data.items() 
                  if k != 'Token' and not isinstance(v, dict)}
    
    # 2. Сортируем по ключу
    sorted_keys = sorted(token_data.keys())
    
    # 3. Конкатенируем значения
    token_string = ''.join(str(token_data[key]) for key in sorted_keys)
    
    # 4. Добавляем секрет
    token_string += SECRET_KEY
    
    # 5. SHA-256
    return hashlib.sha256(token_string.encode()).hexdigest()
```
