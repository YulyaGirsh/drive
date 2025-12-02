"""
Обработчик для работы с заказами (автоюрист, автопсихолог)
"""
from utils import read_request_data, send_json_response, send_error_response
from handlers.telegram_handler import TelegramHandler


class OrdersHandler:
    """Обработчик запросов к заказам"""
    
    @staticmethod
    def _format_client_info(order_data):
        """Форматирует информацию о клиенте"""
        telegram_info = order_data.get('telegramUser')
        if telegram_info:
            return f"""• ID: {telegram_info['id']}
• Имя: {telegram_info['first_name']} {telegram_info.get('last_name', '')}
• Username: @{telegram_info.get('username', 'не указан')}
• Язык: {telegram_info.get('language_code', 'не указан')}"""
        else:
            return f"""• Имя: {order_data['name']}
• Telegram: @{order_data.get('telegram', 'не указан')}"""
    
    @staticmethod
    def _validate_order_data(order_data):
        """Валидирует данные заказа"""
        if not order_data.get('name') or not order_data.get('phone') or not order_data.get('situation'):
            return False
        return True
    
    @staticmethod
    def _process_order(handler, service_emoji, service_name):
        """Универсальный метод обработки заказа"""
        try:
            order_data = read_request_data(handler.headers, handler.rfile)
            if not order_data:
                send_error_response(handler, 400, "Invalid request data")
                return
            
            # Валидация обязательных полей
            if not OrdersHandler._validate_order_data(order_data):
                send_error_response(handler, 400, "Missing required fields")
                return
            
            # Форматирование сообщения для админа
            client_info = OrdersHandler._format_client_info(order_data)
            order_message = f"""🆕 **ПОСТУПИЛ НОВЫЙ ЗАКАЗ**

{service_emoji} **Услуга:** {order_data['service']}

**Клиент:**
{client_info}

📞 **Телефон:** {order_data['phone']}

📝 **Описание ситуации:**
{order_data['situation']}

⏰ **Время заказа:** {order_data['timestamp']}

💬 **Связаться с клиентом:** @{order_data.get('telegram', 'не указан')}"""
            
            # Отправка уведомления админу
            TelegramHandler.send_notification(order_message)
            
            # Логирование заказа
            print(f"📋 Новый заказ {service_name} получен:", {
                'client': f"{order_data['name']} (@{order_data.get('telegram', 'не указан')})",
                'service': order_data['service'],
                'timestamp': order_data['timestamp'],
                'telegramUser': order_data.get('telegramUser')
            })
            
            send_json_response(handler, {'success': True, 'message': 'Order submitted successfully'})
        except Exception as e:
            print(f"Ошибка при обработке заказа {service_name}: {e}")
            send_error_response(handler, 500, str(e))
    
    @staticmethod
    def handle_lawyer_order(handler):
        """Обработка заказа автоюриста"""
        OrdersHandler._process_order(handler, '⚖️', 'автоюриста')
    
    @staticmethod
    def handle_psychologist_order(handler):
        """Обработка заказа автопсихолога"""
        OrdersHandler._process_order(handler, '🧠', 'автопсихолога')

