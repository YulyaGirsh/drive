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
    
    def create_payment(self, amount, user_id, description=None):
        """
        Создает платеж в Т-банк
        """
        try:
            # Формируем данные платежа
            payment_data = {
                "merchant_id": self.merchant_id,
                "amount": amount * 100,  # Сумма в копейках
                "currency": PAYMENT_CURRENCY,
                "description": description or PAYMENT_DESCRIPTION,
                "order_id": f"easydrive_{user_id}_{int(time.time())}",
                "return_url": f"https://hochupravaeasy.ru/success?user_id={user_id}",
                "fail_url": f"https://hochupravaeasy.ru/fail?user_id={user_id}",
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
