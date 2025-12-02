"""
HTTP сервер для EasyDrive приложения
Использует модульную архитектуру с разделением на routes и handlers
"""
import http.server
import socketserver
import webbrowser
import os
from pathlib import Path
from routes import Router
from config import PORT


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    """HTTP обработчик запросов"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Добавляем правильные MIME-типы для изображений
        self.extensions_map.update({
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        })
    
    def end_headers(self):
        # Добавляем CORS заголовки для работы с Telegram
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()
    
    def do_GET(self):
        """Обработка GET запросов"""
        try:
            if self.path.startswith('/api/'):
                Router.handle_get_request(self, self.path)
            elif self.path == '/favicon.ico':
                # Обработка favicon.ico
                self.send_response(200)
                self.send_header('Content-Type', 'image/x-icon')
                self.end_headers()
                self.wfile.write(b'')  # Пустой favicon
            else:
                # Обычная обработка статических файлов
                super().do_GET()
        except Exception as e:
            print(f"Ошибка при обработке GET запроса: {e}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def log_message(self, format, *args):
        """Логируем все запросы для отладки"""
        print(f"{args[0]} {args[1]}")
    
    def do_POST(self):
        """Обработка POST запросов"""
        try:
            if self.path.startswith('/api/'):
                Router.handle_post_request(self, self.path)
            else:
                self.send_error(404, "Not found")
        except Exception as e:
            print(f"Ошибка при обработке POST запроса: {e}")
            self.send_error(500, f"Server error: {str(e)}")
    
    def do_OPTIONS(self):
        """Обработка CORS preflight запросов"""
        self.send_response(200)
        self.end_headers()


def start_server():
    """Запускает HTTP сервер"""
    # Переходим в директорию с файлами
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    class ReuseAddrTCPServer(socketserver.TCPServer):
        allow_reuse_address = True
    
    with ReuseAddrTCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Сервер запущен на http://0.0.0.0:{PORT}")
        print(f"Откройте приложение в браузере: http://localhost:{PORT}")
        print("Для остановки нажмите Ctrl+C")
        
        # Автоматически открываем браузер только если не в Docker
        if os.getenv('DOCKER_CONTAINER') != 'true':
            try:
                webbrowser.open(f'http://localhost:{PORT}')
            except Exception:
                pass  # Игнорируем ошибки открытия браузера
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nСервер остановлен")


if __name__ == "__main__":
    start_server()
