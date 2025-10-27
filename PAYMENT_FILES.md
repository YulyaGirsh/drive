# Файлы для работы с оплатой и онлайн терминалом

## 🎯 Основные файлы

### 1. **videos.html** (главный файл фронтенда)
- **Расположение:** Корень проекта
- **Размер:** ~1980 строк
- **Основные функции:**

#### Ключевые функции оплаты:
- **`processCardPayment()`** (строка ~926)
  - Главная функция обработки оплаты картой
  - Отправляет запросы в Т-банк API
  - Логика активации подписки

- **`createTbankToken()`** (строка ~1109)
  - Генерация токена для Т-банк API
  - Использует SHA-256 хеширование
  - Строгий порядок полей: Amount → Description → FailURL → OrderId → SuccessURL → TerminalKey → SecretKey

- **`showCardPaymentModal()`** (строка ~616)
  - Отображение модального окна для ввода данных карты
  - Валидация данных

### 2. **tbank_payment.py** (Python backend)
- **Расположение:** Корень проекта
- **Размер:** ~638 строк
- **Назначение:** Backend обработка платежей через Python
- **Класс:** `TbankPayment`
- **Основной метод:** `init_payment(amount, user_id, description)`

### 3. **tbank_config.py** (конфигурация)
- **Расположение:** Корень проекта
- **Размер:** ~52 строки
- **Назначение:** Загрузка конфигурации из config.env

### 4. **config.env** (данные терминалов)
- **Расположение:** Корень проекта
- **Содержит:**
  - `TBANK_TERMINAL_KEY` — ключ терминала
  - `TBANK_SECRET_KEY` — секретный ключ
  - `TBANK_API_URL` — URL API
  - `TBANK_MERCHANT_ID` — ID мерчанта

## 🔧 Как работает оплата

1. **Пользователь нажимает на 3+ видеоурок** → `showPaymentModal()`
2. **Выбирает оплату картой** → `showCardPaymentModal()`
3. **Вводит данные карты** → `processCardPayment()`
4. **Генерируется токен** → `createTbankToken()`
5. **Отправляется запрос в Т-банк** → `https://securepay.tinkoff.ru/v2/Init`
6. **При успехе** → подписка сохраняется в `localStorage`

## 📝 Основные переменные в videos.html

```javascript
// Строки 242-246
const TBANK_TERMINAL_KEY = '1761136519162DEMO'; // Тестовый Terminal Key
const TBANK_SECRET_KEY = 'TY#iAnEUV*3CS&BI'; // Тестовый Secret Key
const TBANK_API_URL = 'https://securepay.tinkoff.ru/v2';
```

## 🎯 Где находятся данные:

- **Ключи терминала:** `videos.html` строки 242-245
- **Логика оплаты:** `videos.html` строки 926-1095
- **Генерация токена:** `videos.html` строки 1109-1189
- **Обработка форм:** `videos.html` строки 616-788
