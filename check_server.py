#!/usr/bin/env python3
"""
Проверка статуса проекта на сервере
"""
import paramiko
import getpass

def check_server_status():
    host = '89.23.99.152'
    username = 'root'
    password = 'dJN.wJ-YM*+J9b'
    
    try:
        print("🔌 Подключение к серверу...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, username=username, password=password, timeout=10)
        
        print("✅ Подключено!\n")
        
        # 1. Проверка git status
        print("="*60)
        print("📁 GIT STATUS")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command('cd /home/easydrive && git status')
        print(stdout.read().decode('utf-8'))
        
        # 2. Проверка процесса server.py
        print("\n" + "="*60)
        print("🖥️  ПРОЦЕСС SERVER.PY")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python.*server.py" | grep -v grep')
        output = stdout.read().decode('utf-8')
        if output:
            print(output)
        else:
            print("❌ Сервер НЕ запущен!")
        
        # 3. Проверка наличия обработчика
        print("\n" + "="*60)
        print("🔍 ПРОВЕРКА ОБРАБОТЧИКА")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command('cd /home/easydrive && grep -n "def init_tbank_payment" server.py')
        output = stdout.read().decode('utf-8')
        if output:
            print("✅ Обработчик найден в server.py:")
            print(output)
        else:
            print("❌ Обработчик init_tbank_payment НЕ найден!")
        
        # 4. Проверка последнего коммита
        print("\n" + "="*60)
        print("📝 ПОСЛЕДНИЕ КОММИТЫ")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command('cd /home/easydrive && git log --oneline -5')
        print(stdout.read().decode('utf-8'))
        
        # 5. Проверка логов
        print("\n" + "="*60)
        print("📋 ПОСЛЕДНИЕ ЛОГИ СЕРВЕРА")
        print("="*60)
        stdin, stdout, stderr = ssh.exec_command('cd /home/easydrive && tail -20 server.log')
        print(stdout.read().decode('utf-8'))
        
        ssh.close()
        print("\n✅ Проверка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_server_status()

