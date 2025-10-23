#!/usr/bin/env python3
"""
Сервер для обработки webhook'ов от Т-банка
Запускается отдельно от основного приложения
"""
import http.server
import socketserver
import json
import os
import requests
from urllib.parse import parse_qs
from tbank_payment import TbankPayment

PORT = 8001  # Другой порт, чтобы не конфликтовать с основным сервером

class WebhookHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/api/tbank-webhook':
            self.handle_tbank_webhook()
        else:
            self.send_error(404, "Not found")
    
    def handle_tbank_webhook(self):
        """Обрабатывает webhook от Т-банка"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Получен webhook от Т-банка: {data}")
            
            # Проверяем подпись (если есть)
            signature = self.headers.get('X-Tbank-Signature', '')
            if signature:
                payment = TbankPayment()
                if not payment.verify_webhook(data, signature):
                    print("Неверная подпись webhook")
                    self.send_error(400, "Invalid signature")
                    return
            
            # Обрабатываем статус платежа
            payment_status = data.get('status')
            order_id = data.get('order_id', '')
            amount = data.get('amount', 0)
            
            # Извлекаем user_id из order_id (формат: easydrive_{user_id}_{timestamp})
            if order_id.startswith('easydrive_'):
                try:
                    user_id = order_id.split('_')[1]
                except:
                    user_id = None
            else:
                user_id = None
            
            if payment_status == 'success' and user_id:
                # Отправляем уведомление в Telegram
                self.send_telegram_notification(user_id, amount)
                
                print(f"Платеж успешен для пользователя {user_id}")
                
                # Отправляем ответ Т-банку
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
            else:
                print(f"Платеж не успешен: {payment_status}")
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при обработке webhook: {e}")
            self.send_error(500, str(e))
    
    def send_telegram_notification(self, user_id, amount):
        """Отправляет уведомление в Telegram о успешной оплате"""
        try:
            # Загружаем конфигурацию
            from tbank_config import REAL_CONFIG
            import os
            
            bot_token = os.getenv('BOT_TOKEN')
            recipient_id = os.getenv('RECIPIENT_ID')
            
            if not bot_token or not recipient_id:
                print("Не настроены BOT_TOKEN или RECIPIENT_ID")
                return
            
            message_text = f"""💰 <b>Платеж успешно обработан!</b>

👤 <b>Пользователь ID:</b> {user_id}
💰 <b>Сумма:</b> {amount / 100}₽
🏦 <b>Способ оплаты:</b> Т-банк
⏰ <b>Время:</b> {os.popen('date').read().strip()}

✅ <b>Подписка активирована автоматически</b>"""

            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            response = requests.post(telegram_url, json={
                'chat_id': recipient_id,
                'text': message_text,
                'parse_mode': 'HTML'
            })
            
            if response.ok:
                print("Уведомление об оплате отправлено в Telegram")
            else:
                print(f"Ошибка отправки уведомления: {response.status_code}")
                
        except Exception as e:
            print(f"Ошибка отправки уведомления в Telegram: {e}")

if __name__ == "__main__":
    # Загружаем переменные окружения
    from pathlib import Path
    config_file = Path('config.env')
    if config_file.exists():
        with open(config_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    with socketserver.TCPServer(("", PORT), WebhookHandler) as httpd:
        print(f"🌐 Webhook сервер запущен на порту {PORT}")
        print(f"📡 Webhook URL: https://hochupravaeasy.ru/api/tbank-webhook")
        print("Для остановки нажмите Ctrl+C")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")
