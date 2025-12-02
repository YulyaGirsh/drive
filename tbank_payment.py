"""
Модуль для работы с платежами Т-банк
"""
import json
import hashlib
import hmac
import time
import urllib.request
import urllib.parse
from tbank_config import *

class TbankPayment:
    def __init__(self):
        self.merchant_id = TBANK_MERCHANT_ID
        self.api_key = TBANK_API_KEY
        self.secret_key = TBANK_SECRET_KEY
        self.api_url = TBANK_API_URL
        self.webhook_url = TBANK_WEBHOOK_URL
    
    def init_payment(self, amount, user_id, description=None):
        """
        Инициирует платеж через API /v2/Init для T-Pay
        """
        try:
            order_id = f"easydrive_{user_id}_{int(time.time())}"
            
            # Формируем данные для инициализации платежа T-Pay
            init_data = {
                "TerminalKey": TBANK_TERMINAL_KEY,
                "Amount": amount * 100,  # Сумма в копейках
                "OrderId": order_id,
                "Description": description or PAYMENT_DESCRIPTION,
                "CustomerKey": str(user_id),
                "Recurrent": "Y",  # Сохраняем карту для будущих платежей
                "PayType": "O",  # Одностадийная оплата
                "Language": "ru",
                "NotificationURL": self.webhook_url,
                "SuccessURL": f"{TBANK_SUCCESS_URL}?user_id={user_id}",
                "FailURL": f"{TBANK_FAIL_URL}?user_id={user_id}",
                "DATA": {
                    "OperationInitiatorType": "0",
                    "Source": "tpay"  # Указываем источник T-Pay
                },
                "Receipt": {
                    "Items": [
                        {
                            "Name": description or "Подписка EasyDrive",
                            "Price": amount * 100,
                            "Quantity": 1,
                            "Amount": amount * 100,
                            "PaymentMethod": "full_payment",
                            "PaymentObject": "service",
                            "Tax": "none"
                        }
                    ],
                    "FfdVersion": "1.05",
                    "Taxation": "osn",
                    "Payments": {
                        "Electronic": amount * 100
                    }
                }
            }
            
            # Создаем токен для подписи
            token = self._create_init_token(init_data)
            init_data["Token"] = token
            
            print(f"Инициируем платеж: {init_data}")
            
            # Отправляем запрос в Т-банк
            return self._send_init_request(init_data)
            
        except Exception as e:
            print(f"Ошибка при инициализации платежа: {e}")
            return None
    
    def init_tpay_payment(self, amount, user_id, description=None):
        """
        Инициирует платеж через T-Pay (упрощенный метод)
        """
        try:
            order_id = f"easydrive_{user_id}_{int(time.time())}"
            
            # Упрощенные данные для T-Pay
            init_data = {
                "TerminalKey": TBANK_TERMINAL_KEY,
                "Amount": amount * 100,  # Сумма в копейках
                "OrderId": order_id,
                "Description": description or PAYMENT_DESCRIPTION,
                "CustomerKey": str(user_id),
                "Language": "ru",
                "NotificationURL": self.webhook_url,
                "SuccessURL": f"{TBANK_SUCCESS_URL}?user_id={user_id}",
                "FailURL": f"{TBANK_FAIL_URL}?user_id={user_id}"
            }
            
            # Создаем токен для подписи (упрощенный)
            token = self._create_simple_token(init_data)
            init_data["Token"] = token
            
            print(f"Инициируем T-Pay платеж: {init_data}")
            
            # Отправляем запрос в Т-банк
            return self._send_init_request(init_data)
            
        except Exception as e:
            print(f"Ошибка при инициализации T-Pay платежа: {e}")
            return None
    
    def _create_simple_token(self, data):
        """
        Создает токен согласно официальной документации Т-банка v2 API
        
        Алгоритм:
        1. Берем ТОЛЬКО корневые поля (исключаем Token и вложенные объекты: DATA, Receipt)
        2. Добавляем Password (секретный ключ) как параметр
        3. Сортируем по ключу в алфавитном порядке
        4. Конкатенируем ТОЛЬКО значения в строку
        5. Вычисляем SHA-256
        """
        # Исключаем поле Token и вложенные объекты
        excluded_keys = {'Token', 'DATA', 'Receipt'}  # Игнорируем вложенные объекты
        token_data = {k: v for k, v in data.items() 
                      if k not in excluded_keys 
                      and not isinstance(v, dict)  # Игнорируем вложенные объекты
                      and not isinstance(v, list)   # Игнорируем массивы
                      and v is not None}
        
        # Добавляем Password как параметр (ВАЖНО!)
        token_data['Password'] = self.secret_key
        
        # Сортируем ключи в алфавитном порядке
        sorted_keys = sorted(token_data.keys())
        
        # Конкатенируем ТОЛЬКО значения параметров (не ключи!) в алфавитном порядке
        token_string = ""
        for key in sorted_keys:
            value = token_data[key]
            if value is not None:
                token_string += str(value)
        
        print(f"DEBUG: Параметры для токена: {token_data}")
        print(f"DEBUG: Строка для токена: {token_string[:200]}...")
        
        # Создаем SHA-256 хеш
        token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
        
        print(f"DEBUG: Сгенерированный токен: {token}")
        return token
    
    def create_payment(self, amount, user_id, description=None):
        """
        Создает платеж в Т-банк (старый метод для совместимости)
        """
        try:
            # Формируем данные платежа
            payment_data = {
                "merchant_id": self.merchant_id,
                "amount": amount * 100,  # Сумма в копейках
                "currency": PAYMENT_CURRENCY,
                "description": description or PAYMENT_DESCRIPTION,
                "order_id": f"easydrive_{user_id}_{int(time.time())}",
                "return_url": f"{TBANK_SUCCESS_URL}?user_id={user_id}",
                "fail_url": f"{TBANK_FAIL_URL}?user_id={user_id}",
                "webhook_url": self.webhook_url,
                "timestamp": int(time.time())
            }
            
            # Создаем подпись
            signature = self._create_signature(payment_data)
            payment_data["signature"] = signature
            
            print(f"Создаем платеж: {payment_data}")
            
            # Отправляем запрос в Т-банк
            return self._send_request(payment_data)
            
        except Exception as e:
            print(f"Ошибка при создании платежа: {e}")
            return None
    
    def create_card_payment(self, amount, user_id, card_data, description=None):
        """
        Создает платеж по карте
        """
        try:
            # Формируем данные платежа
            payment_data = {
                "merchant_id": self.merchant_id,
                "amount": amount * 100,  # Сумма в копейках
                "currency": PAYMENT_CURRENCY,
                "description": description or PAYMENT_DESCRIPTION,
                "order_id": f"easydrive_{user_id}_{int(time.time())}",
                "card_number": card_data["number"],
                "card_expiry": card_data["expiry"],
                "card_cvv": card_data["cvv"],
                "card_holder": card_data["holder"],
                "timestamp": int(time.time())
            }
            
            # Создаем подпись
            signature = self._create_signature(payment_data)
            payment_data["signature"] = signature
            
            print(f"Создаем платеж по карте: {payment_data}")
            
            # Отправляем запрос в Т-банк
            return self._send_request(payment_data)
            
        except Exception as e:
            print(f"Ошибка при создании платежа по карте: {e}")
            return None
    
    def verify_webhook(self, data, signature):
        """
        Проверяет подпись webhook от Т-банк
        """
        try:
            # Создаем подпись для проверки
            expected_signature = self._create_signature(data)
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            print(f"Ошибка при проверке webhook: {e}")
            return False
    
    def _create_signature(self, data):
        """
        Создает подпись для запроса
        """
        # Сортируем ключи и создаем строку для подписи
        sorted_keys = sorted(data.keys())
        signature_string = "&".join([f"{key}={data[key]}" for key in sorted_keys])
        signature_string += f"&secret_key={self.secret_key}"
        
        # Создаем HMAC-SHA256 подпись
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            signature_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _create_token(self, data, token_fields=None):
        """
        Универсальный метод создания токена для Т-банк API
        """
        if token_fields is None:
            # По умолчанию используем все поля кроме Token и вложенных объектов
            excluded_keys = {'Token', 'DATA', 'Receipt'}
            token_fields = [k for k in data.keys() 
                          if k not in excluded_keys 
                          and not isinstance(data[k], dict) 
                          and not isinstance(data[k], list)
                          and data[k] is not None]
        
        # Создаем строку для токена
        token_string = ""
        for field in token_fields:
            if field in data and data[field] is not None:
                if field == "DATA" and isinstance(data[field], dict):
                    # Для DATA объекта создаем строку из ключей и значений
                    data_str = ""
                    for key, value in sorted(data[field].items()):
                        data_str += f"{key}={value}"
                    token_string += data_str
                else:
                    token_string += str(data[field])
        
        # Добавляем секретный ключ
        token_string += self.secret_key
        
        # Создаем SHA-256 хеш
        token = hashlib.sha256(token_string.encode('utf-8')).hexdigest()
        
        return token
    
    def _create_init_token(self, data):
        """
        Создает токен для API /v2/Init
        """
        token_fields = [
            "TerminalKey", "Amount", "OrderId", "Description", 
            "CustomerKey", "Recurrent", "PayType", "Language",
            "NotificationURL", "SuccessURL", "FailURL", "DATA"
        ]
        return self._create_token(data, token_fields)
    
    def _send_tbank_api_request(self, url, data, response_fields=None):
        """
        Универсальный метод отправки запроса в Т-банк API
        """
        try:
            # Подготавливаем данные
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            # Создаем запрос
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/json'
                }
            )
            
            # Отправляем запрос
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                print(f"Ответ от Т-банк {url}: {result_data}")
                
                # Проверяем успешность ответа
                if result_data.get('Success'):
                    response_dict = {'success': True}
                    # Всегда добавляем стандартные поля
                    response_dict.update({
                        'payment_id': result_data.get('PaymentId'),
                        'order_id': result_data.get('OrderId') or data.get('OrderId'),
                        'status': result_data.get('Status'),
                        'amount': result_data.get('Amount') or data.get('Amount')
                    })
                    # Добавляем дополнительные поля, если указаны
                    if response_fields:
                        for field in response_fields:
                            # Преобразуем snake_case в PascalCase для API полей
                            api_field = ''.join(word.capitalize() for word in field.split('_'))
                            response_dict[field] = result_data.get(api_field) or result_data.get(field)
                    return response_dict
                else:
                    return {
                        'success': False,
                        'error': result_data.get('Message', 'Неизвестная ошибка'),
                        'details': result_data.get('Details', '')
                    }
                
        except urllib.error.HTTPError as e:
            error_response = e.read().decode('utf-8')
            print(f"HTTP ошибка при запросе к {url}: {e.code} - {error_response}")
            return {
                'success': False,
                'error': f'HTTP ошибка: {e.code}',
                'details': error_response
            }
        except Exception as e:
            print(f"Ошибка при запросе к {url}: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _send_init_request(self, data):
        """
        Отправляет запрос инициализации платежа в Т-банк API /v2/Init
        """
        url = "https://securepay.tinkoff.ru/v2/Init"
        result = self._send_tbank_api_request(url, data, ['PaymentURL'])
        if result.get('success'):
            # Добавляем специфичные поля для Init из ответа API
            result['payment_url'] = result.get('PaymentURL')
        return result
    
    def confirm_payment(self, payment_id, amount=None, ip_address=None):
        """
        Подтверждает списание платежа через API /v2/Confirm
        """
        try:
            # Формируем данные для подтверждения платежа
            confirm_data = {
                "TerminalKey": TBANK_TERMINAL_KEY,
                "PaymentId": payment_id,
                "IP": ip_address or "127.0.0.1"
            }
            
            # Добавляем сумму, если указана
            if amount:
                confirm_data["Amount"] = amount
            
            # Создаем токен для подписи
            token = self._create_confirm_token(confirm_data)
            confirm_data["Token"] = token
            
            print(f"Подтверждаем платеж: {confirm_data}")
            
            # Отправляем запрос в Т-банк
            return self._send_confirm_request(confirm_data)
            
        except Exception as e:
            print(f"Ошибка при подтверждении платежа: {e}")
            return None
    
    def _create_confirm_token(self, data):
        """
        Создает токен для API /v2/Confirm
        """
        token_fields = ["TerminalKey", "PaymentId", "IP", "Amount"]
        return self._create_token(data, token_fields)
    
    def _send_confirm_request(self, data):
        """
        Отправляет запрос подтверждения платежа в Т-банк API /v2/Confirm
        """
        url = "https://securepay.tinkoff.ru/v2/Confirm"
        return self._send_tbank_api_request(url, data)
    
    def finish_authorize(self, payment_id, ip_address=None, send_email=False, source="cards", 
                        card_data=None, encrypted_payment_data=None, amount=None, 
                        device_channel="02", route="ACQ", info_email=None, data_params=None):
        """
        Завершает авторизацию платежа через API /v2/FinishAuthorize
        """
        try:
            # Формируем данные для завершения авторизации
            finish_data = {
                "TerminalKey": TBANK_TERMINAL_KEY,
                "PaymentId": payment_id,
                "IP": ip_address or "127.0.0.1",
                "SendEmail": send_email,
                "Source": source,
                "deviceChannel": device_channel,
                "Route": route
            }
            
            # Добавляем сумму, если указана
            if amount:
                finish_data["Amount"] = amount
            
            # Добавляем email, если указан
            if info_email:
                finish_data["InfoEmail"] = info_email
            
            # Добавляем данные карты, если указаны
            if card_data:
                finish_data["CardData"] = card_data
            
            # Добавляем зашифрованные данные платежа, если указаны
            if encrypted_payment_data:
                finish_data["EncryptedPaymentData"] = encrypted_payment_data
            
            # Добавляем дополнительные параметры 3DS
            if data_params:
                finish_data["DATA"] = data_params
            
            # Создаем токен для подписи
            token = self._create_finish_authorize_token(finish_data)
            finish_data["Token"] = token
            
            print(f"Завершаем авторизацию платежа: {finish_data}")
            
            # Отправляем запрос в Т-банк
            return self._send_finish_authorize_request(finish_data)
            
        except Exception as e:
            print(f"Ошибка при завершении авторизации платежа: {e}")
            return None
    
    def _create_finish_authorize_token(self, data):
        """
        Создает токен для API /v2/FinishAuthorize
        """
        token_fields = [
            "TerminalKey", "PaymentId", "IP", "SendEmail", "Source", 
            "Amount", "deviceChannel", "Route", "InfoEmail"
        ]
        return self._create_token(data, token_fields)
    
    def _send_finish_authorize_request(self, data):
        """
        Отправляет запрос завершения авторизации в Т-банк API /v2/FinishAuthorize
        """
        url = "https://securepay.tinkoff.ru/v2/FinishAuthorize"
        return self._send_tbank_api_request(url, data, ['payment_id', 'order_id', 'status', 'amount', 'acs_url', 'pa_req', 'md'])
    
    def _send_request(self, data):
        """
        Отправляет запрос в Т-банк API
        """
        try:
            # Формируем URL
            url = f"{self.api_url}/create"
            
            # Подготавливаем данные
            json_data = json.dumps(data, ensure_ascii=False).encode('utf-8')
            
            # Создаем запрос
            req = urllib.request.Request(
                url,
                data=json_data,
                headers={
                    'Content-Type': 'application/json; charset=utf-8',
                    'Authorization': f'Bearer {self.api_key}',
                    'X-Merchant-ID': self.merchant_id
                }
            )
            
            # Отправляем запрос
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                print(f"Ответ от Т-банк: {result_data}")
                return result_data
                
        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')
            print(f"HTTP ошибка при запросе к Т-банк: {e.code} - {error_text}")
            return {"error": f"HTTP {e.code}: {error_text}"}
        except Exception as e:
            print(f"Ошибка при запросе к Т-банк: {e}")
            return {"error": str(e)}

# Функция для создания тестового платежа
def create_test_payment(amount, user_id):
    """
    Создает тестовый платеж для демонстрации
    """
    payment = TbankPayment()
    
    # Используем тестовые данные
    test_data = {
        "merchant_id": "test_merchant_123",
        "amount": amount * 100,
        "currency": "RUB",
        "description": "Тестовая оплата подписки",
        "order_id": f"test_easydrive_{user_id}_{int(time.time())}",
        "return_url": f"https://hochupravaeasy.ru/success?user_id={user_id}",
        "fail_url": f"https://hochupravaeasy.ru/fail?user_id={user_id}",
        "timestamp": int(time.time())
    }
    
    # Для тестирования возвращаем успешный ответ
    return {
        "success": True,
        "payment_id": f"test_payment_{user_id}_{int(time.time())}",
        "payment_url": f"https://hochupravaeasy.ru/success?user_id={user_id}",
        "status": "pending",
        "message": "Тестовый платеж создан успешно"
    }
