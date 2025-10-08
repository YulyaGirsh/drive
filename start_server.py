#!/usr/bin/env python3
"""
Скрипт для запуска сервера на правильном порту
"""
import http.server
import socketserver
import os
import sys

# Порт для сервера (обычно 8000 для nginx proxy)
PORT = 8000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем CORS заголовки
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_GET(self):
        # Обработка API запросов
        if self.path.startswith('/api/'):
            self.handle_api_request()
        else:
            # Обычная обработка статических файлов
            super().do_GET()

    def do_POST(self):
        # Обработка POST запросов
        if self.path.startswith('/api/'):
            self.handle_api_post()
        else:
            self.send_error(404, "Not found")

    def do_OPTIONS(self):
        # Обработка CORS preflight запросов
        self.send_response(200)
        self.end_headers()

    def handle_api_request(self):
        try:
            if self.path == '/api/questions':
                self.send_questions()
            elif self.path.startswith('/api/questions/ticket/'):
                ticket_number = int(self.path.split('/')[-1])
                self.send_questions_for_ticket(ticket_number)
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def handle_api_post(self):
        try:
            if self.path == '/api/send-telegram':
                self.send_telegram_message()
            else:
                self.send_error(404, "API endpoint not found")
        except Exception as e:
            self.send_error(500, f"Server error: {str(e)}")

    def send_telegram_message(self):
        """Отправляет сообщение в Telegram"""
        try:
            import json
            import urllib.request
            
            # Читаем данные запроса
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            print(f"Получены данные для отправки в Telegram: {data}")
            
            # Извлекаем параметры
            bot_token = data.get('bot_token')
            chat_id = data.get('chat_id')
            text = data.get('text')
            parse_mode = data.get('parse_mode', 'HTML')
            
            if not all([bot_token, chat_id, text]):
                self.send_error(400, "Missing required parameters")
                return
            
            # Формируем запрос к Telegram API
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            telegram_data = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            # Отправляем запрос
            req = urllib.request.Request(
                telegram_url,
                data=json.dumps(telegram_data).encode('utf-8'),
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req) as response:
                result = response.read().decode('utf-8')
                result_data = json.loads(result)
                
                print(f"Ответ от Telegram: {result_data}")
                
                # Отправляем ответ клиенту
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(result.encode('utf-8'))
                
        except Exception as e:
            print(f"Ошибка при отправке в Telegram: {e}")
            self.send_error(500, str(e))

    def send_questions(self):
        """Отправляет все вопросы из data.json"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                questions = json.load(f)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(questions, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Questions file not found")
        except Exception as e:
            self.send_error(500, f"Error loading questions: {str(e)}")

    def send_questions_for_ticket(self, ticket_number):
        """Отправляет вопросы для конкретного билета"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                all_questions = json.load(f)
            
            # Фильтруем вопросы по номеру билета
            ticket_questions = [q for q in all_questions if q.get('ticket_number') == ticket_number]
            
            if not ticket_questions:
                self.send_error(404, f"Questions for ticket {ticket_number} not found")
                return
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(ticket_questions, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Questions file not found")
        except Exception as e:
            self.send_error(500, f"Error loading questions: {str(e)}")

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"🌐 Сервер запущен на порту {PORT}")
        print(f"📡 Доступен по адресу: http://localhost:{PORT}")
        print(f"🔗 Внешний адрес: https://hochupravaeasy.ru")
        print("Для остановки нажмите Ctrl+C")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n🛑 Сервер остановлен")
