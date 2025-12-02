"""
Обработчик для работы с подписками
"""
from utils import read_request_data, send_json_response, send_error_response, get_current_timestamp
import database


class SubscriptionHandler:
    """Обработчик запросов к подпискам"""
    
    @staticmethod
    def check_paid_subscription(handler):
        """Проверяет оплаченную подписку пользователя"""
        try:
            data = read_request_data(handler.headers, handler.rfile)
            if not data:
                send_error_response(handler, 400, "Invalid request data")
                return
            
            user_id = data.get('user_id')
            if not user_id:
                send_error_response(handler, 400, "Missing user_id")
                return
            
            has_paid_subscription = SubscriptionHandler._check_user_paid_subscription(user_id)
            
            send_json_response(handler, {
                'success': True,
                'has_paid_subscription': has_paid_subscription
            })
        except Exception as e:
            print(f"Ошибка при проверке оплаченной подписки: {e}")
            send_error_response(handler, 500, str(e))
    
    @staticmethod
    def activate_subscription(user_id, amount, payment_method):
        """Активирует подписку для пользователя"""
        try:
            success = SubscriptionHandler._activate_user_subscription(user_id, amount, payment_method)
            
            if success:
                # Отправляем уведомление админу
                from .telegram_handler import TelegramHandler
                admin_message = f"""<b>НОВАЯ ОПЛАТА ПОДПИСКИ</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount} руб
<b>Способ оплаты:</b> {payment_method}
<b>Время:</b> {get_current_timestamp()}

Подписка активирована!"""
                
                TelegramHandler.send_notification(admin_message)
                print(f"Подписка активирована для пользователя {user_id}")
            
            return success
        except Exception as e:
            print(f"Ошибка при активации подписки: {e}")
            return False
    
    @staticmethod
    def _check_user_paid_subscription(user_id):
        """Проверяет, есть ли у пользователя оплаченная подписка"""
        try:
            return database.check_user_subscription(user_id)
        except Exception as e:
            print(f"Ошибка при проверке подписки пользователя: {e}")
            return False
    
    @staticmethod
    def _activate_user_subscription(user_id, amount, payment_method):
        """Активирует подписку для пользователя"""
        try:
            return database.activate_subscription(user_id, amount, payment_method)
        except Exception as e:
            print(f"Ошибка при активации подписки: {e}")
            return False

