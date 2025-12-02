"""
Вспомогательные утилиты
"""
import json
from pathlib import Path
from datetime import datetime


def get_current_timestamp():
    """Возвращает текущее время в формате строки"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def find_image_for_question(ticket_number, question_number):
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


def load_json_file(filepath, default=None):
    """Загружает JSON файл с обработкой ошибок"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return default if default is not None else {}
    except json.JSONDecodeError:
        return default if default is not None else {}


def save_json_file(filepath, data):
    """Сохраняет данные в JSON файл с обработкой ошибок"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка при сохранении файла {filepath}: {e}")
        return False


def read_request_data(headers, rfile):
    """Читает данные из POST запроса"""
    try:
        content_length = int(headers.get('Content-Length', 0))
        if content_length == 0:
            return None
        post_data = rfile.read(content_length)
        return json.loads(post_data.decode('utf-8'))
    except (ValueError, json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Ошибка при чтении данных запроса: {e}")
        return None


def send_json_response(handler, data, status_code=200):
    """Отправляет JSON ответ клиенту"""
    try:
        handler.send_response(status_code)
        handler.send_header('Content-Type', 'application/json; charset=utf-8')
        handler.send_header('Access-Control-Allow-Origin', '*')
        handler.end_headers()
        handler.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    except Exception as e:
        print(f"Ошибка при отправке JSON ответа: {e}")


def send_error_response(handler, status_code, message):
    """Отправляет ошибку клиенту"""
    try:
        handler.send_error(status_code, message)
    except Exception as e:
        print(f"Ошибка при отправке ошибки: {e}")

