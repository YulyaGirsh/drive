import http.server
import socketserver
import webbrowser
import os
import json
import urllib.parse
import urllib.request
from pathlib import Path

PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем правильные MIME-типы для изображений
        self.extensions_map.update({
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        })
    
    def end_headers(self):
        # Добавляем CORS заголовки для работы с Telegram
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Обработка API запросов
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            # Обычная обработка статических файлов
            super().do_GET()

    def do_POST(self):
        # Обработка POST запросов
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404, "Not found")

    def do_OPTIONS(self):
        # Обработка CORS preflight запросов
        self.send_response(200)
        self.end_headers()

    def handle_api_request(self):
        try:
            if self.path == '/api/questions':
                self.send_questions()
            elif self.path.startswith('/api/questions/ticket/'):
                ticket_number = int(self.path.split('/')[-1])
                self.send_questions_for_ticket(ticket_number)
            elif self.path == '/api/get-translation-data':
                self.send_translation_data()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def handle_api_post(self):
        try:
            if self.path == '/api/send-telegram':
                self.send_telegram_message()
            elif self.path == '/api/lawyer-order':
                self.handle_lawyer_order()
            elif self.path == '/api/psychologist-order':
                self.handle_psychologist_order()
            elif self.path == '/api/check-subscription':
                self.check_subscription()
            elif self.path == '/api/check-paid-subscription':
                self.check_paid_subscription()
            elif self.path == '/api/confirm-payment':
                self.confirm_payment()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def send_telegram_message(self):
        """Отправляет сообщение в Telegram"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Получены данные для отправки в Telegram: {data}")
            
            # Извлекаем параметры
            bot_token = data.get('bot_token')
            chat_id = data.get('chat_id')
            text = data.get('text')
            parse_mode = data.get('parse_mode', 'HTML')
            
            if not all([bot_token, chat_id, text]):
                print("Ошибка: отсутствуют обязательные параметры")
                self.send_error(400, "Missing required parameters")
                return
            
            # Формируем запрос к Telegram API
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            telegram_data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            print(f"Отправляем запрос в Telegram: {telegram_url}")
            
            # Отправляем запрос
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                print(f"Ответ от Telegram: {result_data}")
                
                if result_data.get('ok'):
                    print("✅ Сообщение успешно отправлено в Telegram")
                    # Отправляем успешный ответ клиенту
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True, 'message': 'Message sent successfully'}).encode('utf-8'))
                else:
                    print(f"❌ Ошибка Telegram API: {result_data}")
                    self.send_error(500, f"Telegram API error: {result_data.get('description', 'Unknown error')}")
                
        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')
            print(f"HTTP ошибка при отправке в Telegram: {e.code} - {error_text}")
            self.send_error(500, f"HTTP error: {e.code}")
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}")
            self.send_error(500, str(e))

    def handle_lawyer_order(self):
        """Обработка заказа автоюриста"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            order_data = json.loads(post_data.decode('utf-8'))
            
            print(f"Получен заказ автоюриста: {order_data}")
            
            # Валидация обязательных полей
            if not order_data.get('name') or not order_data.get('phone') or not order_data.get('situation'):
                self.send_error(400, "Missing required fields")
                return

            # Форматирование сообщения для админа
            telegram_info = order_data.get('telegramUser')
            if telegram_info:
                client_info = f"""• ID: {telegram_info['id']}
• Имя: {telegram_info['first_name']} {telegram_info.get('last_name', '')}
• Username: @{telegram_info.get('username', 'не указан')}
• Язык: {telegram_info.get('language_code', 'не указан')}"""
            else:
                client_info = f"""• Имя: {order_data['name']}
• Telegram: @{order_data.get('telegram', 'не указан')}"""
            
            order_message = f"""🆕 **ПОСТУПИЛ НОВЫЙ ЗАКАЗ**

⚖️ **Услуга:** {order_data['service']}

👤 **Клиент:**
{client_info}

📞 **Телефон:** {order_data['phone']}

📝 **Описание ситуации:**
{order_data['situation']}

⏰ **Время заказа:** {order_data['timestamp']}

💬 **Связаться с клиентом:** @{order_data.get('telegram', 'не указан')}"""

            # Отправка уведомления админу
            self.send_telegram_notification(order_message)
            
            # Логирование заказа
            print(f"📋 Новый заказ автоюриста получен:", {
                'client': f"{order_data['name']} (@{order_data.get('telegram', 'не указан')})",
                'service': order_data['service'],
                'timestamp': order_data['timestamp'],
                'telegramUser': telegram_info
            })

            # Отправляем ответ клиенту
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Order submitted successfully'}).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при обработке заказа автоюриста: {e}")
            self.send_error(500, str(e))

    def handle_psychologist_order(self):
        """Обработка заказа автопсихолога"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            order_data = json.loads(post_data.decode('utf-8'))
            
            print(f"Получен заказ автопсихолога: {order_data}")
            
            # Валидация обязательных полей
            if not order_data.get('name') or not order_data.get('phone') or not order_data.get('situation'):
                self.send_error(400, "Missing required fields")
                return

            # Форматирование сообщения для админа
            telegram_info = order_data.get('telegramUser')
            if telegram_info:
                client_info = f"""• ID: {telegram_info['id']}
• Имя: {telegram_info['first_name']} {telegram_info.get('last_name', '')}
• Username: @{telegram_info.get('username', 'не указан')}
• Язык: {telegram_info.get('language_code', 'не указан')}"""
            else:
                client_info = f"""• Имя: {order_data['name']}
• Telegram: @{order_data.get('telegram', 'не указан')}"""
            
            order_message = f"""🆕 **ПОСТУПИЛ НОВЫЙ ЗАКАЗ**

🧠 **Услуга:** {order_data['service']}

👤 **Клиент:**
{client_info}

📞 **Телефон:** {order_data['phone']}

📝 **Описание ситуации:**
{order_data['situation']}

⏰ **Время заказа:** {order_data['timestamp']}

💬 **Связаться с клиентом:** @{order_data.get('telegram', 'не указан')}"""

            # Отправка уведомления админу
            self.send_telegram_notification(order_message)
            
            # Логирование заказа
            print(f"📋 Новый заказ автопсихолога получен:", {
                'client': f"{order_data['name']} (@{order_data.get('telegram', 'не указан')})",
                'service': order_data['service'],
                'timestamp': order_data['timestamp'],
                'telegramUser': telegram_info
            })

            # Отправляем ответ клиенту
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'success': True, 'message': 'Order submitted successfully'}).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при обработке заказа автопсихолога: {e}")
            self.send_error(500, str(e))

    def send_telegram_notification(self, message):
        """Отправляет уведомление в Telegram"""
        try:
            # Конфигурация бота
            bot_token = "8263208579:AAHbgB-KSmyqZwMf7FtxBbUzjWNIugUtKu0"
            chat_id = 5292692434
            
            # Формируем запрос к Telegram API
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            telegram_data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'Markdown'
            }
            
            # Отправляем запрос
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                if result_data.get('ok'):
                    print('✅ Уведомление админу отправлено')
                else:
                    print(f'❌ Ошибка отправки уведомления: {result_data}')
                    # Fallback без Markdown
                    try:
                        telegram_data['parse_mode'] = None
                        telegram_data['text'] = message.replace('**', '').replace('*', '')
                        req = urllib.request.Request(
                            telegram_url,
                            data=json.dumps(telegram_data).encode('utf-8'),
                            headers={'Content-Type': 'application/json'}
                        )
                        with urllib.request.urlopen(req) as fallback_response:
                            fallback_result = json.loads(fallback_response.read().decode('utf-8'))
                            if fallback_result.get('ok'):
                                print('✅ Уведомление админу отправлено (без Markdown)')
                    except Exception as fallback_error:
                        print(f'❌ Ошибка отправки уведомления (fallback): {fallback_error}')
                
        except Exception as e:
            print(f'❌ Ошибка при отправке уведомления: {e}')

    def check_subscription(self):
        """Проверяет подписку пользователя на канал"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Проверяем подписку для пользователя: {data}")
            
            user_id = data.get('user_id')
            channel_username = data.get('channel_username', '+w4RmUNIUdKFlMDBi')
            
            if not user_id:
                self.send_error(400, "Missing user_id")
                return
            
            # Конфигурация бота
            bot_token = "8263208579:AAHbgB-KSmyqZwMf7FtxBbUzjWNIugUtKu0"
            
            # Проверяем подписку через Telegram API
            telegram_url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
            telegram_data = {
                'chat_id': f'@{channel_username}',
                'user_id': user_id
            }
            
            print(f"Отправляем запрос проверки подписки: {telegram_url}")
            
            # Отправляем запрос
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode('utf-8')
                    result_data = json.loads(result)
                    
                    print(f"Ответ от Telegram API: {result_data}")
                    
                    if result_data.get('ok'):
                        member_data = result_data.get('result', {})
                        status = member_data.get('status', 'left')
                        
                        # Пользователь подписан если статус не 'left'
                        is_subscribed = status != 'left'
                        
                        print(f"Статус подписки: {status}, Подписан: {is_subscribed}")
                        
                        # Отправляем ответ клиенту
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True, 
                            'is_subscribed': is_subscribed,
                            'status': status
                        }).encode('utf-8'))
                    else:
                        print(f"Ошибка Telegram API: {result_data}")
                        # Если бот не может проверить подписку, считаем что пользователь не подписан
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'success': True, 
                            'is_subscribed': False,
                            'status': 'unknown',
                            'error': result_data.get('description', 'Cannot check subscription')
                        }).encode('utf-8'))
                        
            except urllib.error.HTTPError as e:
                error_text = e.read().decode('utf-8')
                print(f"HTTP ошибка при проверке подписки: {e.code} - {error_text}")
                
                # Если ошибка 400, значит бот не может проверить подписку
                if e.code == 400:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'success': True, 
                        'is_subscribed': False,
                        'status': 'unknown',
                        'error': 'Bot cannot check subscription - not admin of channel'
                    }).encode('utf-8'))
                else:
                    self.send_error(500, f"HTTP error: {e.code}")
                
        except Exception as e:
            print(f"Ошибка при проверке подписки: {e}")
            self.send_error(500, str(e))

    def send_questions(self):
        """Отправляет все вопросы из data.json"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(questions, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Questions file not found")
        except json.JSONDecodeError:
            self.send_error(500, "Invalid JSON format")

    def send_questions_for_ticket(self, ticket_number):
        """Отправляет вопросы для конкретного билета"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                all_questions = json.load(f)
            
            # Фильтруем вопросы по номеру билета
            ticket_questions = [q for q in all_questions if q.get('ticket_number') == ticket_number]
            
            # Добавляем информацию об изображениях
            for question in ticket_questions:
                question['image_path'] = self.find_image_for_question(ticket_number, question.get('question_number', 1))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(ticket_questions, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Questions file not found")
        except json.JSONDecodeError:
            self.send_error(500, "Invalid JSON format")

    def find_image_for_question(self, ticket_number, question_number):
        """Находит изображение для вопроса по схеме ticket{номер}_q{номер}_{рандом}"""
        images_dir = Path('images')
        if not images_dir.exists():
            return None
        
        # Ищем файлы по паттерну ticket{ticket_number}_q{question_number}_*
        pattern = f"ticket{ticket_number}_q{question_number}_"
        matching_files = list(images_dir.glob(f"{pattern}*.jpg"))
        
        if matching_files:
            # Возвращаем первый найденный файл
            return f"images/{matching_files[0].name}"
        
        return None

    def send_translation_data(self):
        """Отправляет данные о трансляции из файла translation_data.json"""
        try:
            with open('translation_data.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            # Если файл не найден, возвращаем пустой объект
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps({}, ensure_ascii=False).encode('utf-8'))
        except json.JSONDecodeError:
            self.send_error(500, "Invalid JSON format in translation data")

    def check_paid_subscription(self):
        """Проверяет оплаченную подписку пользователя"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Проверяем оплаченную подписку для пользователя: {data}")
            
            user_id = data.get('user_id')
            
            if not user_id:
                self.send_error(400, "Missing user_id")
                return
            
            # Проверяем в файле подписок
            has_paid_subscription = self.check_user_paid_subscription(user_id)
            
            print(f"Результат проверки оплаченной подписки: {has_paid_subscription}")
            
            # Отправляем ответ клиенту
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True, 
                'has_paid_subscription': has_paid_subscription
            }).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при проверке оплаченной подписки: {e}")
            self.send_error(500, str(e))

    def confirm_payment(self):
        """Подтверждает оплату и активирует подписку"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Подтверждаем оплату: {data}")
            
            user_id = data.get('user_id')
            amount = data.get('amount', 10)
            payment_method = data.get('payment_method', 'tbank')
            
            if not user_id:
                self.send_error(400, "Missing user_id")
                return
            
            # Активируем подписку
            success = self.activate_user_subscription(user_id, amount, payment_method)
            
            if success:
                # Отправляем уведомление админу
                admin_message = f"""💰 <b>НОВАЯ ОПЛАТА ПОДПИСКИ</b>

👤 <b>Пользователь ID:</b> {user_id}
💰 <b>Сумма:</b> {amount}₽
🏦 <b>Способ оплаты:</b> {payment_method}
🕐 <b>Время:</b> {self.get_current_timestamp()}

✅ Подписка активирована!"""
                
                self.send_telegram_notification(admin_message)
                
                print(f"✅ Подписка активирована для пользователя {user_id}")
                
                # Отправляем успешный ответ клиенту
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'success': True, 
                    'message': 'Subscription activated successfully'
                }).encode('utf-8'))
            else:
                self.send_error(500, "Failed to activate subscription")
                
        except Exception as e:
            print(f"Ошибка при подтверждении оплаты: {e}")
            self.send_error(500, str(e))

    def check_user_paid_subscription(self, user_id):
        """Проверяет, есть ли у пользователя оплаченная подписка"""
        try:
            # Читаем файл с подписками
            try:
                with open('paid_subscriptions.json', 'r', encoding='utf-8') as f:
                    subscriptions = json.load(f)
            except FileNotFoundError:
                # Если файла нет, создаем пустой
                subscriptions = {}
            
            # Проверяем, есть ли пользователь в списке
            return str(user_id) in subscriptions
            
        except Exception as e:
            print(f"Ошибка при проверке подписки пользователя: {e}")
            return False

    def activate_user_subscription(self, user_id, amount, payment_method):
        """Активирует подписку для пользователя"""
        try:
            # Читаем существующие подписки
            try:
                with open('paid_subscriptions.json', 'r', encoding='utf-8') as f:
                    subscriptions = json.load(f)
            except FileNotFoundError:
                subscriptions = {}
            
            # Добавляем пользователя с подпиской
            subscriptions[str(user_id)] = {
                'activated_at': self.get_current_timestamp(),
                'amount': amount,
                'payment_method': payment_method,
                'status': 'active'
            }
            
            # Сохраняем обновленные подписки
            with open('paid_subscriptions.json', 'w', encoding='utf-8') as f:
                json.dump(subscriptions, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Ошибка при активации подписки: {e}")
            return False

    def get_current_timestamp(self):
        """Возвращает текущее время в формате строки"""
        from datetime import datetime
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def start_server():
    # Переходим в директорию с файлами
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Сервер запущен на http://localhost:{PORT}")
        print(f"Откройте приложение в браузере: http://localhost:{PORT}")
        print("Для остановки нажмите Ctrl+C")
        
        # Автоматически открываем браузер
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")

if __name__ == "__main__":
    start_server()

