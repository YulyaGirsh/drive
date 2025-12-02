#!/usr/bin/env python3
"""
Скрипт для тестирования проверки подписки на канал
Использование: python test_subscription.py <user_id> [channel]
"""
import sys
import json
import urllib.request
import urllib.error
from config import BOT_TOKEN

def test_subscription(user_id, channel='avtoshkolavtelefone'):
    """Тестирует проверку подписки на канал"""
    print(f"\n{'='*60}")
    print(f"🧪 ТЕСТ ПРОВЕРКИ ПОДПИСКИ")
    print(f"{'='*60}")
    print(f"👤 User ID: {user_id}")
    print(f"📺 Канал: @{channel}")
    print(f"🤖 Bot Token: {BOT_TOKEN[:20]}...")
    print(f"{'='*60}\n")
    
    try:
        telegram_url = f"https://api.telegram.org/bot{BOT_TOKEN}/getChatMember"
        full_url = f"{telegram_url}?chat_id=@{channel}&user_id={user_id}"
        
        print(f"📡 Отправляем запрос:")
        print(f"   {full_url}\n")
        
        with urllib.request.urlopen(full_url, timeout=10) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"📥 Ответ от Telegram API:")
            print(json.dumps(result_data, indent=2, ensure_ascii=False))
            print()
            
            if result_data.get('ok'):
                member_data = result_data.get('result', {})
                status = member_data.get('status', 'left')
                is_subscribed = status not in ['left', 'kicked']
                
                print(f"{'='*60}")
                print(f"📊 РЕЗУЛЬТАТ:")
                print(f"   Статус: {status}")
                print(f"   Подписан: {'✅ ДА' if is_subscribed else '❌ НЕТ'}")
                print(f"{'='*60}\n")
                
                if is_subscribed:
                    print("✅ Пользователь подписан на канал!")
                    return True
                else:
                    print("❌ Пользователь НЕ подписан на канал")
                    print(f"   Статус: {status}")
                    return False
            else:
                error_msg = result_data.get('description', 'Unknown error')
                print(f"{'='*60}")
                print(f"❌ ОШИБКА:")
                print(f"   {error_msg}")
                print(f"{'='*60}\n")
                
                if 'not found' in error_msg.lower() or 'chat not found' in error_msg.lower():
                    print("⚠️  Канал не найден. Проверьте имя канала.")
                elif 'not enough rights' in error_msg.lower() or 'not admin' in error_msg.lower():
                    print("⚠️  Бот не является администратором канала!")
                    print("   Решение: Добавьте бота как администратора канала @{}".format(channel))
                elif 'user not found' in error_msg.lower():
                    print("⚠️  Пользователь не найден. Проверьте user_id.")
                
                return False
                
    except urllib.error.HTTPError as e:
        try:
            error_text = e.read().decode('utf-8')
            error_data = json.loads(error_text)
            print(f"❌ HTTP Ошибка {e.code}:")
            print(json.dumps(error_data, indent=2, ensure_ascii=False))
        except:
            print(f"❌ HTTP Ошибка {e.code}: {str(e)}")
        
        print()
        if e.code == 400:
            print("⚠️  Ошибка 400 обычно означает:")
            print("   - Бот не является администратором канала")
            print("   - Канал не существует")
            print("   - Неправильное имя канала")
        elif e.code == 403:
            print("⚠️  Ошибка 403: Бот не имеет доступа к каналу")
        elif e.code == 404:
            print("⚠️  Ошибка 404: Канал или пользователь не найден")
        
        return False
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint(user_id, channel='avtoshkolavtelefone', server_url='http://localhost:8000'):
    """Тестирует API endpoint проверки подписки"""
    print(f"\n{'='*60}")
    print(f"🧪 ТЕСТ API ENDPOINT")
    print(f"{'='*60}")
    print(f"🌐 Server URL: {server_url}")
    print(f"👤 User ID: {user_id}")
    print(f"📺 Канал: @{channel}")
    print(f"{'='*60}\n")
    
    try:
        request_data = {
            'user_id': user_id,
            'channel': channel
        }
        
        print(f"📤 Отправляем POST запрос на {server_url}/api/check-channel-subscription")
        print(f"📋 Данные: {json.dumps(request_data, ensure_ascii=False)}\n")
        
        req = urllib.request.Request(
            f"{server_url}/api/check-channel-subscription",
            data=json.dumps(request_data).encode('utf-8'),
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            result_data = json.loads(result)
            
            print(f"📥 Ответ от сервера:")
            print(json.dumps(result_data, indent=2, ensure_ascii=False))
            print()
            
            subscribed = result_data.get('subscribed', False)
            print(f"{'='*60}")
            print(f"📊 РЕЗУЛЬТАТ:")
            print(f"   Подписан: {'✅ ДА' if subscribed else '❌ НЕТ'}")
            if result_data.get('status'):
                print(f"   Статус: {result_data.get('status')}")
            if result_data.get('error'):
                print(f"   Ошибка: {result_data.get('error')}")
            print(f"{'='*60}\n")
            
            return subscribed
            
    except urllib.error.HTTPError as e:
        error_text = e.read().decode('utf-8')
        print(f"❌ HTTP Ошибка {e.code}:")
        print(error_text)
        return False
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Использование:")
        print("  python test_subscription.py <user_id> [channel] [--api] [--server-url URL]")
        print()
        print("Примеры:")
        print("  python test_subscription.py 123456789")
        print("  python test_subscription.py 123456789 avtoshkolavtelefone")
        print("  python test_subscription.py 123456789 --api")
        print("  python test_subscription.py 123456789 --api --server-url http://localhost:8000")
        sys.exit(1)
    
    user_id = sys.argv[1]
    channel = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else 'avtoshkolavtelefone'
    
    use_api = '--api' in sys.argv
    server_url = 'http://localhost:8000'
    if '--server-url' in sys.argv:
        idx = sys.argv.index('--server-url')
        if idx + 1 < len(sys.argv):
            server_url = sys.argv[idx + 1]
    
    if use_api:
        success = test_api_endpoint(user_id, channel, server_url)
    else:
        success = test_subscription(user_id, channel)
    
    sys.exit(0 if success else 1)

