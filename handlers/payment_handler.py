"""
Обработчик для работы с платежами Т-Банк
"""
import json
import urllib.request
from tbank_payment import TbankPayment
from utils import read_request_data, send_json_response, send_error_response, get_current_timestamp
from .telegram_handler import TelegramHandler
from .subscription_handler import SubscriptionHandler


class PaymentHandler:
    """Обработчик запросов к платежам"""
    
    @staticmethod
    def init_tbank_payment(handler):
        """Инициирует платеж через Т-банк API /v2/Init"""
        try:
            data = read_request_data(handler.headers, handler.rfile)
            if not data:
                send_error_response(handler, 400, "Empty request body")
                return
            
            terminal_key = data.get('TerminalKey')
            amount = data.get('Amount')
            order_id = data.get('OrderId')
            description = data.get('Description')
            success_url = data.get('SuccessURL')
            fail_url = data.get('FailURL')
            language = data.get('Language', 'ru')
            customer_key = data.get('CustomerKey')
            
            if not all([terminal_key, amount, order_id]):
                send_error_response(handler, 400, "Missing required parameters: TerminalKey, Amount, OrderId")
                return
            
            payment = TbankPayment()
            
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
                    'Items': [{
                        'Name': 'Подписка на видеоуроки EasyDrive',
                        'Price': amount,
                        'Quantity': 1,
                        'Amount': amount,
                        'Tax': 'none',
                        'Ean13': ''
                    }],
                    'Taxation': 'usn_income',
                    'FfdVersion': '1.05'
                }
            }
            
            # Генерируем токен
            token = payment._create_simple_token(tbank_data)
            tbank_data['Token'] = token
            
            # Отправляем в Т-банк
            url = 'https://securepay.tinkoff.ru/v2/Init'
            req = urllib.request.Request(
                url,
                data=json.dumps(tbank_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=10) as response:
                result = json.loads(response.read().decode('utf-8'))
                send_json_response(handler, result)
                
        except Exception as e:
            print(f"Ошибка при инициализации платежа Т-банк: {e}")
            import traceback
            traceback.print_exc()
            send_error_response(handler, 500, str(e))
    
    @staticmethod
    def handle_webhook(handler):
        """Обрабатывает webhook от Т-банк"""
        try:
            data = read_request_data(handler.headers, handler.rfile)
            if not data:
                send_error_response(handler, 400, "Invalid request data")
                return
            
            # Проверяем подпись (если есть)
            signature = handler.headers.get('X-Tbank-Signature', '')
            if signature:
                payment = TbankPayment()
                if not payment.verify_webhook(data, signature):
                    send_error_response(handler, 400, "Invalid signature")
                    return
            
            # Обрабатываем статус платежа
            payment_status = data.get('Status') or data.get('status')
            order_id = data.get('OrderId') or data.get('order_id', '')
            amount = data.get('Amount') or data.get('amount', 0)
            payment_id = data.get('PaymentId') or data.get('payment_id')
            
            # Извлекаем user_id из order_id
            user_id = None
            if order_id.startswith('easydrive_'):
                try:
                    user_id = order_id.split('_')[1]
                except:
                    pass
            
            # Обрабатываем разные статусы платежа
            if payment_status == 'AUTHORIZED' and user_id and payment_id:
                payment = TbankPayment()
                confirm_result = payment.confirm_payment(payment_id, amount)
                
                if confirm_result and confirm_result.get('success'):
                    success = SubscriptionHandler.activate_subscription(
                        user_id, amount / 100, 'tbank'
                    )
                    admin_message = PaymentHandler._create_payment_notification(
                        user_id, amount / 100, 'tbank', 'Подтверждено', success
                    )
                    TelegramHandler.send_notification(admin_message)
            
            elif payment_status in ['CONFIRMED', 'success'] and user_id:
                success = SubscriptionHandler.activate_subscription(
                    user_id, amount / 100, 'tbank'
                )
                admin_message = PaymentHandler._create_payment_notification(
                    user_id, amount / 100, 'tbank', 'Успешно', success
                )
                TelegramHandler.send_notification(admin_message)
            
            send_json_response(handler, {'status': 'ok'})
                
        except Exception as e:
            print(f"Ошибка при обработке webhook Т-банк: {e}")
            send_error_response(handler, 500, str(e))
    
    @staticmethod
    def _create_payment_notification(user_id, amount, payment_method, status, success):
        """Создает сообщение для уведомления админа"""
        if success:
            return f"""<b>НОВАЯ ОПЛАТА ПОДПИСКИ (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount} руб
<b>Способ оплаты:</b> {payment_method}
<b>Время:</b> {get_current_timestamp()}
<b>Статус:</b> {status}

Подписка активирована!"""
        else:
            return f"""<b>ОШИБКА АКТИВАЦИИ ПОДПИСКИ (Т-БАНК)</b>

<b>Пользователь ID:</b> {user_id}
<b>Сумма:</b> {amount} руб
<b>Способ оплаты:</b> {payment_method}
<b>Время:</b> {get_current_timestamp()}
<b>Статус:</b> Платеж подтвержден, но ошибка активации подписки"""
    
    @staticmethod
    def confirm_payment(handler):
        """Подтверждает оплату и активирует подписку"""
        try:
            data = read_request_data(handler.headers, handler.rfile)
            if not data:
                send_error_response(handler, 400, "Invalid request data")
                return
            
            user_id = data.get('user_id')
            amount = data.get('amount', 10)
            payment_method = data.get('payment_method', 'tbank')
            
            if not user_id:
                send_error_response(handler, 400, "Missing user_id")
                return
            
            success = SubscriptionHandler.activate_subscription(user_id, amount, payment_method)
            
            if success:
                send_json_response(handler, {
                    'success': True,
                    'message': 'Subscription activated successfully'
                })
            else:
                send_json_response(handler, {
                    'success': False,
                    'message': 'Failed to activate subscription'
                })
        except Exception as e:
            print(f"Ошибка при подтверждении оплаты: {e}")
            send_error_response(handler, 500, str(e))

