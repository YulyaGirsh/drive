import http.server
import socketserver
import webbrowser
import os
import json
import urllib.parse
import urllib.request
from pathlib import Path

PORT = 3000

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Добавляем CORS заголовки для работы с Telegram
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
        except json.JSONDecodeError:
            self.send_error(500, "Invalid JSON format")

    def send_questions_for_ticket(self, ticket_number):
        """Отправляет вопросы для конкретного билета"""
        try:
            with open('data.json', 'r', encoding='utf-8') as f:
                all_questions = json.load(f)
            
            # Фильтруем вопросы по номеру билета
            ticket_questions = [q for q in all_questions if q.get('ticket_number') == ticket_number]
            
            # Добавляем информацию об изображениях
            for question in ticket_questions:
                question['image_path'] = self.find_image_for_question(ticket_number, question.get('question_number', 1))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.end_headers()
            self.wfile.write(json.dumps(ticket_questions, ensure_ascii=False).encode('utf-8'))
        except FileNotFoundError:
            self.send_error(404, "Questions file not found")
        except json.JSONDecodeError:
            self.send_error(500, "Invalid JSON format")

    def find_image_for_question(self, ticket_number, question_number):
        """Находит изображение для вопроса по схеме ticket{номер}_q{номер}_{рандом}"""
        images_dir = Path('images')
        if not images_dir.exists():
            return None
        
        # Ищем файлы по паттерну ticket{ticket_number}_q{question_number}_*
        pattern = f"ticket{ticket_number}_q{question_number}_"
        matching_files = list(images_dir.glob(f"{pattern}*.jpg"))
        
        if matching_files:
            # Возвращаем первый найденный файл
            return f"images/{matching_files[0].name}"
        
        return None

def start_server():
    # Переходим в директорию с файлами
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Сервер запущен на http://localhost:{PORT}")
        print(f"Откройте приложение в браузере: http://localhost:{PORT}")
        print("Для остановки нажмите Ctrl+C")
        
        # Автоматически открываем браузер
        webbrowser.open(f'http://localhost:{PORT}')
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")

if __name__ == "__main__":
    start_server()

