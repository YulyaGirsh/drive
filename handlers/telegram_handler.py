"""
Обработчик для работы с Telegram API
"""
import json
import urllib.request
import urllib.error
from config import BOT_TOKEN, ADMIN_CHAT_ID
from utils import read_request_data, send_json_response, send_error_response


class TelegramHandler:
    """Обработчик запросов к Telegram API"""
    
    @staticmethod
    def send_message(handler, data):
        """Отправляет сообщение в Telegram"""
        try:
            bot_token = data.get('bot_token')
            chat_id = data.get('chat_id')
            text = data.get('text')
            parse_mode = data.get('parse_mode', 'HTML')
            
            if not all([bot_token, chat_id, text]):
                send_error_response(handler, 400, "Missing required parameters")
                return
            
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            telegram_data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data, ensure_ascii=False).encode('utf-8'),
                headers={'Content-Type': 'application/json; charset=utf-8'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                if result_data.get('ok'):
                    send_json_response(handler, {'success': True, 'message': 'Message sent successfully'})
                else:
                    error_msg = result_data.get('description', 'Unknown error')
                    send_error_response(handler, 500, f"Telegram API error: {error_msg}")
                    
        except urllib.error.HTTPError as e:
            error_text = e.read().decode('utf-8')
            print(f"HTTP ошибка при отправке в Telegram: {e.code} - {error_text}")
            send_error_response(handler, 500, f"HTTP error: {e.code}")
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}")
            send_error_response(handler, 500, str(e))
    
    @staticmethod
    def send_notification(message):
        """Отправляет уведомление админу в Telegram"""
        try:
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            telegram_data = {
                'chat_id': ADMIN_CHAT_ID,
                'text': message,
                'parse_mode': 'HTML'
            }
            
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
                    # Fallback без HTML
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
                                print('Уведомление админу отправлено (без HTML)')
                    except Exception as fallback_error:
                        print(f'Ошибка отправки уведомления (fallback): {fallback_error}')
                        
        except Exception as e:
            print(f'Ошибка при отправке уведомления: {e}')
    
    @staticmethod
    def check_channel_subscription(handler, user_id, channel):
        """Проверяет подписку пользователя на канал"""
        try:
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
            full_url = f"{telegram_url}?chat_id=@{channel}&user_id={user_id}"
            
            with urllib.request.urlopen(full_url) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                if result_data.get('ok'):
                    member_data = result_data.get('result', {})
                    status = member_data.get('status', 'left')
                    is_subscribed = status not in ['left', 'kicked']
                    
                    return {
                        'subscribed': is_subscribed,
                        'status': status,
                        'channel': channel
                    }
                else:
                    return {
                        'subscribed': False,
                        'status': 'unknown',
                        'channel': channel,
                        'error': result_data.get('description', 'Cannot check subscription')
                    }
        except urllib.error.HTTPError as e:
            if e.code == 400:
                return {
                    'subscribed': False,
                    'status': 'unknown',
                    'channel': channel,
                    'error': 'Bot cannot check subscription - not admin of channel'
                }
            else:
                return {
                    'subscribed': False,
                    'status': 'unknown',
                    'channel': channel,
                    'error': f'HTTP error: {e.code}'
                }
        except Exception as e:
            print(f"Ошибка при проверке подписки: {e}")
            return {
                'subscribed': False,
                'error': str(e)
            }

