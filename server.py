import http.server
import socketserver
import webbrowser
import os
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path
from tbank_payment import TbankPayment, create_test_payment

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
        elif self.path == '/favicon.ico':
            # Обработка favicon.ico
            self.send_response(200)
            self.send_header('Content-Type', 'image/x-icon')
            self.end_headers()
            self.wfile.write(b'')  # Пустой favicon
        else:
            # Обычная обработка статических файлов
            super().do_GET()
    
    def log_message(self, format, *args):
        """Логируем все запросы для отладки"""
        print(f"{args[0]} {args[1]}")

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
            elif self.path == '/api/tbank-create-payment':
                self.create_tbank_payment()
            elif self.path == '/api/tbank-init-payment':
                self.init_tbank_payment()
            elif self.path == '/api/tbank-confirm-payment':
                self.confirm_tbank_payment()
            elif self.path == '/api/tbank-finish-authorize':
                self.finish_tbank_authorize()
            elif self.path == '/api/tbank-webhook':
                self.handle_tbank_webhook()
            elif self.path == '/api/check-channel-subscription':
                self.check_channel_subscription()
            elif self.path == '/api/v2/heartbeat':
                self.handle_heartbeat()
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
                data=json.dumps(telegram_data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                print(f"Ответ от Telegram: {result_data}")
                
                if result_data.get('ok'):
                    print("Сообщение успешно отправлено в Telegram")
                    # Отправляем успешный ответ клиенту
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({'success': True, 'message': 'Message sent successfully'}).encode('utf-8'))
                else:
                    print(f"Ошибка Telegram API: {result_data}")
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

**Клиент:**
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

**Клиент:**
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
                'parse_mode': 'HTML'
            }
            
            # Отправляем запрос
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                if result_data.get('ok'):
                    print('Уведомление админу отправлено')
                else:
                    print(f'Ошибка отправки уведомления: {result_data}')
                    # Fallback без Markdown
                    try:
                        telegram_data['parse_mode'] = None
                        telegram_data['text'] = message.replace('**', '').replace('*', '')
                        req = urllib.request.Request(
                            telegram_url,
                            data=json.dumps(telegram_data, ensure_ascii=False).encode('utf-8'),
                            headers={'Content-Type': 'application/json; charset=utf-8'}
                        )
                        with urllib.request.urlopen(req) as fallback_response:
                            fallback_result = json.loads(fallback_response.read().decode('utf-8'))
                            if fallback_result.get('ok'):
                                print('Уведомление админу отправлено (без Markdown)')
                    except Exception as fallback_error:
                        print(f'Ошибка отправки уведомления (fallback): {fallback_error}')
                
        except Exception as e:
            print(f'Ошибка при отправке уведомления: {e}')

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
                data=json.dumps(telegram_data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
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
            self.send_header('Access-Control-Allow-Origin', '*')
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
            
            # Отправляем ответ клиенту
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            if success:
                # Отправляем уведомление админу
                admin_message = f"""<b>НОВАЯ ОПЛАТА ПОДПИСКИ</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount} руб
<b>Способ оплаты:</b> {payment_method}
<b>Время:</b> {self.get_current_timestamp()}

Подписка активирована!"""
                
                self.send_telegram_notification(admin_message)
                
                print(f"Подписка активирована для пользователя {user_id}")
                
                # Отправляем успешный ответ клиенту (заголовки уже отправлены ранее)
                self.wfile.write(json.dumps({
                    'success': True, 
                    'message': 'Subscription activated successfully'
                }).encode('utf-8'))
            else:
                self.wfile.write(json.dumps({
                    'success': False, 
                    'message': 'Failed to activate subscription'
                }).encode('utf-8'))
                
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

    def create_tbank_payment(self):
        """Создает платеж через Т-банк"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Создаем платеж Т-банк: {data}")
            
            user_id = data.get('user_id')
            amount = data.get('amount', 10)
            payment_method = data.get('payment_method', 'card')
            card_data = data.get('card_data', {})
            
            if not user_id:
                self.send_error(400, "Missing user_id")
                return
            
            # Создаем платеж через Т-банк
            print(f"Создаем платеж для пользователя {user_id} на сумму {amount}₽")
            
            try:
                payment = TbankPayment()
                result = payment.create_payment(amount, user_id)
                
                if result and result.get('success'):
                    print(f"Платеж создан успешно: {result}")
                    
                    # Отправляем ответ клиенту
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    
                    response_data = {
                        'success': True,
                        'payment_id': result.get('payment_id'),
                        'payment_url': result.get('payment_url'),
                        'message': 'Payment created successfully',
                        'amount': amount,
                        'user_id': user_id
                    }
                    
                    print(f"Отправляем ответ: {response_data}")
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                else:
                    print(f"Ошибка создания платежа: {result}")
                    self.send_error(500, f"Payment creation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Ошибка при создании платежа Т-банк: {e}")
                self.send_error(500, str(e))
                
        except Exception as e:
            print(f"Ошибка при создании платежа Т-банк: {e}")
            self.send_error(500, str(e))
    
    def init_tbank_payment(self):
        """
        Инициирует платеж через Т-банк API /v2/Init
        Получает данные от фронтенда, генерирует токен на бэкенде, отправляет в Т-банк
        """
        try:
            content_length = int(self.headers.get('Content-Length', 0))
            if content_length == 0:
                self.send_error(400, "Empty request body")
                return
                
            post_data = self.rfile.read(content_length)
            
            # Декодируем и логируем сырые данные
            raw_data = post_data.decode('utf-8')
            print(f"Получены сырые данные: {raw_data[:200]}")
            
            data = json.loads(raw_data)
            
            print(f"Получены данные от фронтенда: {data}")
            
            # Извлекаем параметры из данных фронтенда
            terminal_key = data.get('TerminalKey')
            amount = data.get('Amount')
            order_id = data.get('OrderId')
            description = data.get('Description')
            success_url = data.get('SuccessURL')
            fail_url = data.get('FailURL')
            language = data.get('Language', 'ru')
            customer_key = data.get('CustomerKey')
            
            if not all([terminal_key, amount, order_id]):
                self.send_error(400, "Missing required parameters: TerminalKey, Amount, OrderId")
                return
            
            # Генерируем токен на бэкенде (секрет здесь!)
            from tbank_payment import TbankPayment
            payment = TbankPayment()
            
            print(f"DEBUG: Secret Key = {payment.secret_key}")
            print(f"DEBUG: Terminal Key = {terminal_key}")
            
            # Формируем данные для запроса в Т-банк
            tbank_data = {
                'TerminalKey': terminal_key,
                'Amount': amount,
                'OrderId': order_id,
                'Description': description,
                'SuccessURL': success_url,
                'FailURL': fail_url,
                'Language': language,
                'CustomerKey': customer_key,
                'Receipt': {
                    'Email': f'user_{customer_key}@example.com',
                    'Items': [
                        {
                            'Name': 'Подписка на видеоуроки EasyDrive',
                            'Price': amount,
                            'Quantity': 1,
                            'Amount': amount,
                            'Tax': 'none',
                            'Ean13': ''
                        }
                    ],
                    'Taxation': 'usn_income',
                    'FfdVersion': '1.05'
                }
            }
            
            # Генерируем токен
            token = payment._create_simple_token(tbank_data)
            tbank_data['Token'] = token
            
            print(f"DEBUG: Генерация токена для данных: {tbank_data}")
            print(f"DEBUG: Сгенерированный токен: {token}")
            print(f"Отправляем запрос в Т-банк: {tbank_data}")
            
            # Отправляем в Т-банк
            import urllib.request
            import urllib.parse
            
            url = 'https://securepay.tinkoff.ru/v2/Init'
            req = urllib.request.Request(
                url,
                data=json.dumps(tbank_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f"Ответ от Т-банка: {result}")
                
                # Отправляем ответ клиенту
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                self.wfile.write(json.dumps(result).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при инициализации платежа Т-банк: {e}")
            import traceback
            traceback.print_exc()
            self.send_error(500, str(e))
    
    def confirm_tbank_payment(self):
        """
        Подтверждает списание платежа через Т-банк API /v2/Confirm
        """
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            payment_id = data.get('payment_id')
            amount = data.get('amount')
            ip_address = data.get('ip_address')
            
            if not payment_id:
                self.send_error(400, "Missing payment_id")
                return
            
            # Подтверждаем платеж через Т-банк
            print(f"Подтверждаем платеж {payment_id} на сумму {amount}₽")
            
            try:
                payment = TbankPayment()
                result = payment.confirm_payment(payment_id, amount, ip_address)
                
                if result and result.get('success'):
                    print(f"Платеж подтвержден успешно: {result}")
                    
                    # Отправляем ответ клиенту
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    
                    response_data = {
                        'success': True,
                        'payment_id': result.get('payment_id'),
                        'order_id': result.get('order_id'),
                        'status': result.get('status'),
                        'amount': result.get('amount'),
                        'message': 'Payment confirmed successfully'
                    }
                    
                    print(f"Отправляем ответ: {response_data}")
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                else:
                    print(f"Ошибка подтверждения платежа: {result}")
                    self.send_error(500, f"Payment confirmation failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Ошибка при подтверждении платежа Т-банк: {e}")
                self.send_error(500, str(e))
                
        except Exception as e:
            print(f"Ошибка при подтверждении платежа Т-банк: {e}")
            self.send_error(500, str(e))
    
    def finish_tbank_authorize(self):
        """
        Завершает авторизацию платежа через Т-банк API /v2/FinishAuthorize
        """
        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            payment_id = data.get('payment_id')
            ip_address = data.get('ip_address')
            send_email = data.get('send_email', False)
            source = data.get('source', 'cards')
            card_data = data.get('card_data')
            encrypted_payment_data = data.get('encrypted_payment_data')
            amount = data.get('amount')
            device_channel = data.get('device_channel', '02')
            route = data.get('route', 'ACQ')
            info_email = data.get('info_email')
            data_params = data.get('data_params')
            
            if not payment_id:
                self.send_error(400, "Missing payment_id")
                return
            
            # Завершаем авторизацию через Т-банк
            print(f"Завершаем авторизацию платежа {payment_id}")
            
            try:
                payment = TbankPayment()
                result = payment.finish_authorize(
                    payment_id=payment_id,
                    ip_address=ip_address,
                    send_email=send_email,
                    source=source,
                    card_data=card_data,
                    encrypted_payment_data=encrypted_payment_data,
                    amount=amount,
                    device_channel=device_channel,
                    route=route,
                    info_email=info_email,
                    data_params=data_params
                )
                
                if result and result.get('success'):
                    print(f"Авторизация завершена успешно: {result}")
                    
                    # Отправляем ответ клиенту
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
                    self.send_header('Access-Control-Allow-Headers', 'Content-Type')
                    self.end_headers()
                    
                    response_data = {
                        'success': True,
                        'payment_id': result.get('payment_id'),
                        'order_id': result.get('order_id'),
                        'status': result.get('status'),
                        'amount': result.get('amount'),
                        'acs_url': result.get('acs_url'),
                        'pa_req': result.get('pa_req'),
                        'md': result.get('md'),
                        'message': 'Authorization finished successfully'
                    }
                    
                    print(f"Отправляем ответ: {response_data}")
                    self.wfile.write(json.dumps(response_data).encode('utf-8'))
                else:
                    print(f"Ошибка завершения авторизации: {result}")
                    self.send_error(500, f"Authorization finish failed: {result.get('error', 'Unknown error')}")
                    
            except Exception as e:
                print(f"Ошибка при завершении авторизации Т-банк: {e}")
                self.send_error(500, str(e))
                
        except Exception as e:
            print(f"Ошибка при завершении авторизации Т-банк: {e}")
            self.send_error(500, str(e))

    def handle_tbank_webhook(self):
        """Обрабатывает webhook от Т-банк"""
        try:
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Получен webhook от Т-банк: {data}")
            
            # Проверяем подпись (если есть)
            signature = self.headers.get('X-Tbank-Signature', '')
            if signature:
                payment = TbankPayment()
                if not payment.verify_webhook(data, signature):
                    print("Неверная подпись webhook")
                    self.send_error(400, "Invalid signature")
                    return
            
            # Обрабатываем статус платежа
            payment_status = data.get('Status') or data.get('status')  # Т-банк использует 'Status'
            order_id = data.get('OrderId') or data.get('order_id', '')  # Т-банк использует 'OrderId'
            amount = data.get('Amount') or data.get('amount', 0)  # Т-банк использует 'Amount'
            payment_id = data.get('PaymentId') or data.get('payment_id')  # Т-банк использует 'PaymentId'
            
            # Добавляем отладочную информацию
            print(f"DEBUG: payment_status={payment_status}, order_id={order_id}, amount={amount}, payment_id={payment_id}")
            
            # Извлекаем user_id из order_id (формат: easydrive_{user_id}_{timestamp})
            if order_id.startswith('easydrive_'):
                try:
                    user_id = order_id.split('_')[1]
                except:
                    user_id = None
            else:
                user_id = None
            
            # Обрабатываем разные статусы платежа
            if payment_status == 'AUTHORIZED' and user_id:
                # Платеж авторизован, нужно подтвердить списание
                if payment_id:
                    print(f"Платеж {payment_id} авторизован, подтверждаем списание...")
                    
                    try:
                        payment = TbankPayment()
                        confirm_result = payment.confirm_payment(payment_id, amount)
                        
                        if confirm_result and confirm_result.get('success'):
                            print(f"Платеж {payment_id} успешно подтвержден")
                            
                            # Активируем подписку
                            success = self.activate_user_subscription(user_id, amount / 100, 'tbank')
                            
                            if success:
                                print(f"Подписка активирована для пользователя {user_id}")
                                
                                # Отправляем уведомление админу
                                admin_message = f"""<b>НОВАЯ ОПЛАТА ПОДПИСКИ (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount / 100} руб
<b>Способ оплаты:</b> Т-банк (T-Pay)
<b>Время:</b> {self.get_current_timestamp()}
<b>Статус:</b> Подтверждено

Подписка активирована!"""
                            else:
                                admin_message = f"""<b>ОШИБКА АКТИВАЦИИ ПОДПИСКИ (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount / 100} руб
<b>Способ оплаты:</b> Т-банк (T-Pay)
<b>Время:</b> {self.get_current_timestamp()}
<b>Статус:</b> Платеж подтвержден, но ошибка активации подписки"""
                        else:
                            print(f"Ошибка подтверждения платежа {payment_id}: {confirm_result}")
                            admin_message = f"""<b>ОШИБКА ПОДТВЕРЖДЕНИЯ ПЛАТЕЖА (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Payment ID:</b> {payment_id}
<b>Сумма:</b> {amount / 100} руб
<b>Время:</b> {self.get_current_timestamp()}
<b>Статус:</b> Ошибка подтверждения

{confirm_result.get('error', 'Неизвестная ошибка')}"""
                    except Exception as e:
                        print(f"Ошибка при подтверждении платежа: {e}")
                        admin_message = f"""<b>ОШИБКА ПОДТВЕРЖДЕНИЯ ПЛАТЕЖА (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Payment ID:</b> {payment_id}
<b>Сумма:</b> {amount / 100} руб
<b>Время:</b> {self.get_current_timestamp()}
<b>Статус:</b> Исключение при подтверждении

{str(e)}"""
                    
                    # Отправляем уведомление админу
                    self.send_telegram_notification(admin_message)
                    
            elif payment_status in ['CONFIRMED', 'success'] and user_id:
                # Платеж успешен (одностадийный)
                success = self.activate_user_subscription(user_id, amount / 100, 'tbank')
                
                if success:
                    print(f"Подписка активирована для пользователя {user_id}")
                    
                    # Отправляем уведомление админу
                    admin_message = f"""<b>НОВАЯ ОПЛАТА ПОДПИСКИ (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount / 100} руб
<b>Способ оплаты:</b> Т-банк
<b>Время:</b> {self.get_current_timestamp()}
<b>Статус:</b> Успешно

Подписка активирована!"""
                    
                    self.send_telegram_notification(admin_message)
                else:
                    print(f"Ошибка активации подписки для пользователя {user_id}")
            
            # Отправляем ответ Т-банк
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'status': 'ok'}).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при обработке webhook Т-банк: {e}")
            self.send_error(500, str(e))

    def handle_heartbeat(self):
        """Обрабатывает heartbeat запросы"""
        try:
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'status': 'ok',
                'timestamp': self.get_current_timestamp(),
                'server': 'EasyDrive'
            }).encode('utf-8'))
        except Exception as e:
            print(f"Ошибка при обработке heartbeat: {e}")
            self.send_error(500, str(e))

    def check_channel_subscription(self):
        """Проверяет подписку пользователя на канал (новая версия для работы с разными каналами)"""
        try:
            print(f"\n{'='*60}")
            print(f"🔍 ПРОВЕРКА ПОДПИСКИ НА КАНАЛ")
            print(f"{'='*60}")
            
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # ДЕБАГ: Проверяем, что мы получили
            print(f"🔍 Content-Length header: {content_length}")
            print(f"🔍 Фактическая длина post_data: {len(post_data)}")
            print(f"🔍 Первые 50 байт в hex: {post_data[:50].hex()}")
            
            # Декодируем данные
            try:
                raw_data = post_data.decode('utf-8')
            except Exception as e:
                print(f"❌ Ошибка декодирования: {e}")
                raw_data = str(post_data)
            
            print(f"📥 Получены сырые данные: {raw_data[:200]}")
            print(f"📊 Длина данных: {len(raw_data)}")
            print(f"📋 Байты данных (repr): {post_data[:100]}")
            print(f"📋 Байты данных (hex): {post_data.hex()[:100]}")
            print(f"📋 Байты данных (raw): {post_data[:100]}")
            
            # Пытаемся распарсить JSON
            try:
                data = json.loads(raw_data)
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                print(f"📝 Попытка исправления...")
                # Пробуем исправить двойной escape
                try:
                    fixed_data = raw_data.replace('\\\\', '\\')
                    data = json.loads(fixed_data)
                    print(f"✅ Успешно исправлено и распарсено")
                except:
                    print(f"❌ Не удалось исправить JSON")
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'subscribed': False,
                        'error': f'Invalid JSON: {str(e)}'
                    }).encode('utf-8'))
                    return
            
            print(f"✅ Парсинг JSON успешен: {data}")
            print(f"👤 User ID: {data.get('user_id')}")
            print(f"📺 Channel: {data.get('channel')}")
            print(f"{'='*60}\n")
            
            user_id = data.get('user_id')
            channel = data.get('channel')  # 'test_girsh' или другой канал
            
            if not user_id:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'subscribed': False,
                    'error': 'Missing user_id'
                }).encode('utf-8'))
                return
            
            if not channel:
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({
                    'subscribed': False,
                    'error': 'Missing channel'
                }).encode('utf-8'))
                return
            
            # Конфигурация бота
            bot_token = "8263208579:AAHbgB-KSmyqZwMf7FtxBbUzjWNIugUtKu0"
            
            # Проверяем подписку через Telegram API
            telegram_url = f"https://api.telegram.org/bot{bot_token}/getChatMember"
            telegram_data = {
                'chat_id': f'@{channel}',
                'user_id': user_id
            }
            
            print(f"Отправляем запрос проверки подписки на @{channel}: {telegram_url}")
            print(f"Данные запроса: {telegram_data}")
            
            # Отправляем запрос
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            try:
                with urllib.request.urlopen(req) as response:
                    result = response.read().decode('utf-8')
                    result_data = json.loads(result)
                    
                    print(f"Ответ от Telegram API: {result_data}")
                    
                    if result_data.get('ok'):
                        member_data = result_data.get('result', {})
                        status = member_data.get('status', 'left')
                        
                        # Пользователь подписан если статус не 'left' и не 'kicked'
                        is_subscribed = status not in ['left', 'kicked']
                        
                        print(f"📊 Статус подписки на @{channel}: {status}")
                        print(f"✅ Подписан: {is_subscribed}")
                        
                        # Отправляем ответ клиенту
                        response_data = {
                            'subscribed': is_subscribed,
                            'status': status,
                            'channel': channel
                        }
                        
                        print(f"📤 Отправляем ответ клиенту: {response_data}\n")
                        
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(response_data).encode('utf-8'))
                    else:
                        print(f"Ошибка Telegram API: {result_data}")
                        # Если бот не может проверить подписку, считаем что пользователь не подписан
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps({
                            'subscribed': False,
                            'status': 'unknown',
                            'channel': channel,
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
                        'subscribed': False,
                        'status': 'unknown',
                        'channel': channel,
                        'error': 'Bot cannot check subscription - not admin of channel'
                    }).encode('utf-8'))
                else:
                    self.send_response(200)
                    self.send_header('Content-Type', 'application/json')
                    self.end_headers()
                    self.wfile.write(json.dumps({
                        'subscribed': False,
                        'status': 'unknown',
                        'channel': channel,
                        'error': f'HTTP error: {e.code}'
                    }).encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при проверке подписки на канал: {e}")
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'subscribed': False,
                'error': str(e)
            }).encode('utf-8'))

def start_server():
    # Переходим в директорию с файлами
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    class ReuseAddrTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    with ReuseAddrTCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
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

