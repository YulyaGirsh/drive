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
    def _send_telegram_message(bot_token, chat_id, text, parse_mode='HTML'):
        """
        Универсальный метод отправки сообщения в Telegram
        Возвращает (success: bool, result_data: dict)
        """
        try:
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
                return result_data.get('ok', False), result_data
                
        except urllib.error.HTTPError as e:
            try:
                error_text = e.read().decode('utf-8')
            except:
                error_text = str(e)
            print(f"HTTP ошибка при отправке в Telegram: {e.code} - {error_text}")
            return False, {'error': f'HTTP error: {e.code}', 'description': error_text}
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}")
            return False, {'error': str(e)}
    
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
            
            success, result_data = TelegramHandler._send_telegram_message(bot_token, chat_id, text, parse_mode)
            
            if success:
                send_json_response(handler, {'success': True, 'message': 'Message sent successfully'})
            else:
                error_msg = result_data.get('description', 'Unknown error')
                send_error_response(handler, 500, f"Telegram API error: {error_msg}")
                    
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}")
            send_error_response(handler, 500, str(e))
    
    @staticmethod
    def send_notification(message):
        """Отправляет уведомление админу в Telegram"""
        try:
            success, result_data = TelegramHandler._send_telegram_message(BOT_TOKEN, ADMIN_CHAT_ID, message, 'HTML')
            
            if success:
                print('Уведомление админу отправлено')
            else:
                print(f'Ошибка отправки уведомления: {result_data}')
                # Fallback без HTML
                try:
                    # Убираем HTML разметку и пробуем снова
                    plain_text = message.replace('**', '').replace('*', '').replace('<b>', '').replace('</b>', '')
                    success, fallback_result = TelegramHandler._send_telegram_message(BOT_TOKEN, ADMIN_CHAT_ID, plain_text, None)
                    if success:
                        print('Уведомление админу отправлено (без HTML)')
                except Exception as fallback_error:
                    print(f'Ошибка отправки уведомления (fallback): {fallback_error}')
                        
        except Exception as e:
            print(f'Ошибка при отправке уведомления: {e}')
    
    @staticmethod
    def check_channel_subscription(handler, user_id, channel):
        """Проверяет подписку пользователя на канал"""
        try:
            print(f"\n{'='*60}")
            print(f"🔍 ПРОВЕРКА ПОДПИСКИ НА КАНАЛ")
            print(f"{'='*60}")
            print(f"👤 User ID: {user_id}")
            print(f"📺 Канал: @{channel}")
            print(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
            print(f"{'='*60}")
            
            telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
            full_url = f"{telegram_url}?chat_id=@{channel}&user_id={user_id}"
            
            print(f"📡 Отправляем запрос к Telegram API...")
            print(f"   URL: {telegram_url}")
            print(f"   Параметры: chat_id=@{channel}, user_id={user_id}\n")
            
            with urllib.request.urlopen(full_url, timeout=10) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                print(f"📥 Ответ от Telegram API получен")
                print(f"   ok: {result_data.get('ok')}")
                
                if result_data.get('ok'):
                    member_data = result_data.get('result', {})
                    status = member_data.get('status', 'left')
                    is_subscribed = status not in ['left', 'kicked']
                    
                    print(f"\n✅ РЕЗУЛЬТАТ ПРОВЕРКИ:")
                    print(f"   Статус: {status}")
                    print(f"   Подписан: {'ДА ✅' if is_subscribed else 'НЕТ ❌'}")
                    print(f"{'='*60}\n")
                    
                    return {
                        'subscribed': is_subscribed,
                        'status': status,
                        'channel': channel
                    }
                else:
                    error_msg = result_data.get('description', 'Cannot check subscription')
                    error_code = result_data.get('error_code', 'unknown')
                    print(f"\n❌ ОШИБКА TELEGRAM API:")
                    print(f"   Код ошибки: {error_code}")
                    print(f"   Описание: {error_msg}")
                    print(f"{'='*60}\n")
                    
                    # Детальные сообщения об ошибках
                    if error_code == 400:
                        if 'chat not found' in error_msg.lower():
                            print("⚠️  КРИТИЧЕСКАЯ ОШИБКА: Канал не найден!")
                            print(f"   Проверьте, что канал @{channel} существует")
                        elif 'not enough rights' in error_msg.lower() or 'not admin' in error_msg.lower():
                            print("⚠️  КРИТИЧЕСКАЯ ОШИБКА: Бот не является администратором канала!")
                            print(f"   Решение: Добавьте бота как администратора канала @{channel}")
                            print("   В настройках канала → Администраторы → Добавить администратора")
                    elif error_code == 403:
                        print("⚠️  ОШИБКА: Бот не имеет доступа к каналу")
                    
                    return {
                        'subscribed': False,
                        'status': 'unknown',
                        'channel': channel,
                        'error': error_msg,
                        'error_code': error_code
                    }
        except urllib.error.HTTPError as e:
            try:
                error_text = e.read().decode('utf-8')
                error_data = json.loads(error_text)
                print(f"❌ HTTP ошибка {e.code}: {error_data}")
            except:
                error_text = str(e)
                print(f"❌ HTTP ошибка {e.code}: {error_text}")
            
            if e.code == 400:
                # Бот не может проверить подписку (не админ канала или канал не существует)
                # Это критическая ошибка - бот должен быть администратором канала!
                print(f"⚠️ ВНИМАНИЕ: Бот не может проверить подписку на канал @{channel}")
                print(f"⚠️ Убедитесь, что бот является администратором канала @{channel}")
                return {
                    'subscribed': False,
                    'status': 'unknown',
                    'channel': channel,
                    'error': 'Bot cannot check subscription - not admin of channel or channel not found'
                }
            elif e.code == 403:
                # Запрещено - бот заблокирован или нет прав
                print(f"⚠️ Ошибка 403: Бот не имеет доступа к каналу @{channel}")
                return {
                    'subscribed': False,
                    'status': 'unknown',
                    'channel': channel,
                    'error': 'Bot does not have access to channel'
                }
            else:
                return {
                    'subscribed': False,
                    'status': 'unknown',
                    'channel': channel,
                    'error': f'HTTP error: {e.code}'
                }
        except Exception as e:
            print(f"❌ Ошибка при проверке подписки: {e}")
            import traceback
            traceback.print_exc()
            return {
                'subscribed': False,
                'status': 'unknown',
                'channel': channel,
                'error': str(e)
            }

