#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации nginx
"""
import subprocess
import re

def check_nginx_config():
    """Проверяем конфигурацию nginx"""
    try:
        # Получаем конфигурацию nginx
        result = subprocess.run(['nginx', '-T'], capture_output=True, text=True)
        
        if result.returncode == 0:
            config = result.stdout
            
            # Ищем proxy_pass
            proxy_matches = re.findall(r'proxy_pass\s+http://[^;]+', config)
            print("🔍 Найденные proxy_pass:")
            for match in proxy_matches:
                print(f"   {match}")
            
            # Ищем listen порты
            listen_matches = re.findall(r'listen\s+(\d+)', config)
            print(f"\n🔍 Найденные порты listen: {set(listen_matches)}")
            
            # Ищем server_name
            server_matches = re.findall(r'server_name\s+([^;]+)', config)
            print(f"🔍 Найденные server_name: {set(server_matches)}")
            
        else:
            print(f"❌ Ошибка получения конфигурации nginx: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_nginx_config()
