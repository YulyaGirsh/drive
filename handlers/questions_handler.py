"""
Обработчик для работы с вопросами ПДД
"""
import json
from utils import load_json_file, send_json_response, send_error_response, find_image_for_question


class QuestionsHandler:
    """Обработчик запросов к вопросам"""
    
    @staticmethod
    def get_all_questions(handler):
        """Отправляет все вопросы из data.json"""
        try:
            questions = load_json_file('data.json', default=[])
            if not questions:
                send_error_response(handler, 404, "Questions file not found")
                return
            send_json_response(handler, questions)
        except Exception as e:
            print(f"Ошибка при загрузке вопросов: {e}")
            send_error_response(handler, 500, "Error loading questions")
    
    @staticmethod
    def get_ticket_questions(handler, ticket_number):
        """Отправляет вопросы для конкретного билета"""
        try:
            all_questions = load_json_file('data.json', default=[])
            if not all_questions:
                send_error_response(handler, 404, "Questions file not found")
                return
            
            # Фильтруем вопросы по номеру билета
            ticket_questions = [q for q in all_questions if q.get('ticket_number') == ticket_number]
            
            # Добавляем информацию об изображениях
            for question in ticket_questions:
                question['image_path'] = find_image_for_question(
                    ticket_number, 
                    question.get('question_number', 1)
                )
            
            send_json_response(handler, ticket_questions)
        except Exception as e:
            print(f"Ошибка при загрузке вопросов билета: {e}")
            send_error_response(handler, 500, "Error loading ticket questions")
    
    @staticmethod
    def get_translation_data(handler):
        """Отправляет данные о трансляции"""
        try:
            data = load_json_file('translation_data.json', default={})
            send_json_response(handler, data)
        except Exception as e:
            print(f"Ошибка при загрузке данных трансляции: {e}")
            send_error_response(handler, 500, "Error loading translation data")

