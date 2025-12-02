"""
Маршрутизация API запросов
"""
from handlers.telegram_handler import TelegramHandler
from handlers.questions_handler import QuestionsHandler
from handlers.payment_handler import PaymentHandler
from handlers.subscription_handler import SubscriptionHandler
from handlers.orders_handler import OrdersHandler
from utils import read_request_data, send_json_response, send_error_response, get_current_timestamp


class Router:
    """Маршрутизатор для API запросов"""
    
    @staticmethod
    def handle_get_request(handler, path):
        """Обрабатывает GET запросы"""
        try:
            if path == '/api/questions':
                QuestionsHandler.get_all_questions(handler)
            elif path.startswith('/api/questions/ticket/'):
                try:
                    ticket_number = int(path.split('/')[-1])
                    QuestionsHandler.get_ticket_questions(handler, ticket_number)
                except ValueError:
                    send_error_response(handler, 400, "Invalid ticket number")
            elif path == '/api/get-translation-data':
                QuestionsHandler.get_translation_data(handler)
            else:
                send_error_response(handler, 404, "API endpoint not found")
        except Exception as e:
            print(f"Ошибка при обработке GET запроса: {e}")
            send_error_response(handler, 500, f"Server error: {str(e)}")
    
    @staticmethod
    def handle_post_request(handler, path):
        """Обрабатывает POST запросы"""
        try:
            # Логируем каждый POST запрос
            print(f"\n{'='*60}")
            print(f"📥 POST ЗАПРОС: {path}")
            print(f"📋 Headers: {dict(handler.headers)}")
            print(f"{'='*60}")
            
            if path == '/api/send-telegram':
                data = read_request_data(handler.headers, handler.rfile)
                if data:
                    TelegramHandler.send_message(handler, data)
                else:
                    send_error_response(handler, 400, "Invalid request data")
            
            elif path == '/api/lawyer-order':
                OrdersHandler.handle_lawyer_order(handler)
            
            elif path == '/api/psychologist-order':
                OrdersHandler.handle_psychologist_order(handler)
            
            elif path == '/api/check-subscription':
                # Старый метод проверки подписки (для совместимости)
                data = read_request_data(handler.headers, handler.rfile)
                if data:
                    user_id = data.get('user_id')
                    channel = data.get('channel_username', '+w4RmUNIUdKFlMDBi')
                    if user_id:
                        result = TelegramHandler.check_channel_subscription(handler, user_id, channel)
                        send_json_response(handler, {
                            'success': True,
                            'is_subscribed': result.get('subscribed', False),
                            'status': result.get('status', 'unknown')
                        })
                    else:
                        send_error_response(handler, 400, "Missing user_id")
                else:
                    send_error_response(handler, 400, "Invalid request data")
            
            elif path == '/api/check-paid-subscription':
                SubscriptionHandler.check_paid_subscription(handler)
            
            elif path == '/api/confirm-payment':
                PaymentHandler.confirm_payment(handler)
            
            elif path == '/api/tbank-init-payment':
                PaymentHandler.init_tbank_payment(handler)
            
            elif path == '/api/tbank-webhook':
                PaymentHandler.handle_webhook(handler)
            
            elif path == '/api/check-channel-subscription':
                data = read_request_data(handler.headers, handler.rfile)
                if not data:
                    send_error_response(handler, 400, "Invalid request data")
                    return
                
                user_id = data.get('user_id')
                channel = data.get('channel', 'avtoshkolavtelefone')  # Значение по умолчанию
                
                # Логируем запрос
                print(f"🔍 Проверка подписки: user_id={user_id}, channel={channel}")
                
                if not user_id:
                    print("⚠️ user_id отсутствует, возвращаем False")
                    send_json_response(handler, {
                        'subscribed': False,
                        'status': 'unknown',
                        'channel': channel,
                        'error': 'User ID not available'
                    })
                    return
                
                if not channel:
                    send_error_response(handler, 400, "Missing channel")
                    return
                
                result = TelegramHandler.check_channel_subscription(handler, user_id, channel)
                print(f"📊 Результат проверки подписки: {result}")
                send_json_response(handler, result)
            
            elif path == '/api/v2/heartbeat':
                send_json_response(handler, {
                    'status': 'ok',
                    'timestamp': get_current_timestamp(),
                    'server': 'EasyDrive'
                })
            
            else:
                send_error_response(handler, 404, "API endpoint not found")
                
        except Exception as e:
            print(f"Ошибка при обработке POST запроса: {e}")
            send_error_response(handler, 500, f"Server error: {str(e)}")

