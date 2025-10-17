import requests
import os
import time
import json
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def create_directories():
    """Создаем необходимые директории"""
    if not os.path.exists('data'):
        os.makedirs('data')
    if not os.path.exists('data/images'):
        os.makedirs('data/images')
    if not os.path.exists('data/images/tickets'):
        os.makedirs('data/images/tickets')

def get_file_extension(url):
    """Получаем расширение файла из URL"""
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        return path.split('.')[-1].lower()
    return 'jpg'

def download_image(url, filename):
    """Скачиваем изображение"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            f.write(response.content)
        
        print(f"✓ Изображение скачано: {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка скачивания {url}: {e}")
        return False

def parse_ticket(ticket_number):
    """Парсим данные конкретного билета"""
    url = f"https://examenpdd.com/bilet/{ticket_number}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        
        print(f"📋 Парсим билет {ticket_number}...")
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем контейнер с вопросами
        questions = []
        
        # Различные селекторы для поиска вопросов
        question_selectors = [
            '.question',
            '.question-item',
            '.ticket-question',
            '[class*="question"]',
            '.bilet-question'
        ]
        
        question_containers = []
        for selector in question_selectors:
            containers = soup.select(selector)
            if containers:
                question_containers = containers
                print(f"✓ Найдены вопросы с селектором: {selector}")
                break
        
        if not question_containers:
            # Если не нашли по селекторам, ищем по тексту
            print("⚠️  Вопросы не найдены по селекторам, ищем по тексту...")
            # Ищем элементы, содержащие текст "Вопрос"
            all_elements = soup.find_all(text=re.compile(r'Вопрос\s+\d+', re.IGNORECASE))
            for element in all_elements:
                parent = element.parent
                while parent and parent.name != 'body':
                    if parent.get('class') and any('question' in cls.lower() for cls in parent.get('class')):
                        question_containers.append(parent)
                        break
                    parent = parent.parent
        
        print(f"📊 Найдено контейнеров вопросов: {len(question_containers)}")
        
        # Парсим каждый вопрос
        for i, container in enumerate(question_containers[:20]):  # Максимум 20 вопросов
            question_data = parse_question(container, ticket_number, i + 1)
            if question_data:
                questions.append(question_data)
        
        # Если не нашли вопросы, создаем заглушки
        if not questions:
            print(f"⚠️  Вопросы для билета {ticket_number} не найдены, создаем заглушки")
            for i in range(20):
                questions.append({
                    "question_number": i + 1,
                    "text": f"Вопрос {i + 1} (Билет {ticket_number})",
                    "answers": ["Вариант А", "Вариант Б", "Вариант В", "Вариант Г"],
                    "correct_answer": 0,
                    "question_type": "multiple_choice",
                    "hint": "Подсказка недоступна",
                    "image": None,
                    "image_path": None
                })
        
        ticket_data = {
            "ticket_number": ticket_number,
            "total_questions": len(questions),
            "questions": questions,
            "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "source_url": url
        }
        
        return ticket_data
        
    except Exception as e:
        print(f"❌ Ошибка при парсинге билета {ticket_number}: {e}")
        return None

def parse_question(container, ticket_number, question_number):
    """Парсим отдельный вопрос"""
    try:
        question_data = {
            "question_number": question_number,
            "text": "",
            "answers": [],
            "correct_answer": 0,
            "question_type": "multiple_choice",
            "hint": "",
            "image": None,
            "image_path": None
        }
        
        # Ищем текст вопроса
        text_selectors = [
            '.question-text',
            '.question-title',
            '.question-content',
            'p',
            'div[class*="text"]'
        ]
        
        for selector in text_selectors:
            text_elem = container.select_one(selector)
            if text_elem and text_elem.get_text(strip=True):
                question_data["text"] = text_elem.get_text(strip=True)
                break
        
        if not question_data["text"]:
            # Если не нашли по селекторам, берем весь текст контейнера
            question_data["text"] = container.get_text(strip=True)[:200] + "..."
        
        # Ищем варианты ответов
        answer_selectors = [
            '.answer',
            '.option',
            '.choice',
            'li',
            'div[class*="answer"]',
            'label'
        ]
        
        answers = []
        for selector in answer_selectors:
            answer_elements = container.select(selector)
            for elem in answer_elements:
                text = elem.get_text(strip=True)
                if text and len(text) > 1 and text not in answers:
                    answers.append(text)
        
        # Если не нашли варианты, создаем заглушки
        if not answers:
            answers = ["Вариант А", "Вариант Б", "Вариант В", "Вариант Г"]
        
        question_data["answers"] = answers
        
        # Ищем правильный ответ (обычно выделен особым классом)
        correct_selectors = [
            '.correct',
            '.right',
            '.true',
            '.answer-correct',
            '[class*="correct"]'
        ]
        
        for selector in correct_selectors:
            correct_elem = container.select_one(selector)
            if correct_elem:
                correct_text = correct_elem.get_text(strip=True)
                for i, answer in enumerate(answers):
                    if correct_text in answer or answer in correct_text:
                        question_data["correct_answer"] = i
                        break
        
        # Ищем изображение
        img_elem = container.select_one('img')
        if img_elem:
            img_src = img_elem.get('src') or img_elem.get('data-src')
            if img_src:
                img_url = urljoin(f"https://examenpdd.com/bilet/{ticket_number}", img_src)
                question_data["image"] = img_url
                
                # Скачиваем изображение
                ext = get_file_extension(img_url)
                img_filename = f"data/images/tickets/ticket_{ticket_number:02d}_question_{question_number:02d}.{ext}"
                
                # Создаем папку для билета
                ticket_dir = f"data/images/tickets"
                if not os.path.exists(ticket_dir):
                    os.makedirs(ticket_dir)
                
                if download_image(img_url, img_filename):
                    question_data["image_path"] = img_filename
        
        # Ищем подсказку
        hint_selectors = [
            '.hint',
            '.explanation',
            '.tip',
            '.help',
            '[class*="hint"]',
            '[class*="explanation"]'
        ]
        
        for selector in hint_selectors:
            hint_elem = container.select_one(selector)
            if hint_elem:
                question_data["hint"] = hint_elem.get_text(strip=True)
                break
        
        if not question_data["hint"]:
            question_data["hint"] = "Подсказка недоступна"
        
        return question_data
        
    except Exception as e:
        print(f"❌ Ошибка при парсинге вопроса {question_number}: {e}")
        return None

def scrape_all_tickets():
    """Парсим все билеты"""
    create_directories()
    
    print("🚀 Начинаем полный парсинг данных с examenpdd.com")
    print("=" * 60)
    
    all_tickets = []
    successful_tickets = 0
    
    for ticket_num in range(1, 41):  # Билеты с 1 по 40
        print(f"\n{'='*20} БИЛЕТ {ticket_num} {'='*20}")
        
        ticket_data = parse_ticket(ticket_num)
        
        if ticket_data:
            all_tickets.append(ticket_data)
            successful_tickets += 1
            
            # Сохраняем данные билета в отдельный файл
            ticket_file = f"data/ticket_{ticket_num:02d}.json"
            with open(ticket_file, 'w', encoding='utf-8') as f:
                json.dump(ticket_data, f, ensure_ascii=False, indent=2)
            
            print(f"✅ Билет {ticket_num} сохранен в {ticket_file}")
        else:
            print(f"❌ Не удалось спарсить билет {ticket_num}")
        
        # Пауза между запросами
        time.sleep(2)
    
    # Сохраняем все данные в один файл
    all_data = {
        "total_tickets": len(all_tickets),
        "successful_tickets": successful_tickets,
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "source": "https://examenpdd.com/",
        "tickets": all_tickets
    }
    
    with open('data/all_tickets.json', 'w', encoding='utf-8') as f:
        json.dump(all_data, f, ensure_ascii=False, indent=2)
    
    print("\n" + "=" * 60)
    print(f"✅ Парсинг завершен!")
    print(f"📊 Обработано билетов: {successful_tickets}/40")
    print(f"📁 Данные сохранены в папке: data/")
    print(f"📄 Основной файл: data/all_tickets.json")
    print(f"📄 Отдельные билеты: data/ticket_XX.json")
    
    return all_data

def create_summary_report(data):
    """Создаем сводный отчет"""
    report = {
        "summary": {
            "total_tickets": data["total_tickets"],
            "successful_tickets": data["successful_tickets"],
            "total_questions": sum(ticket["total_questions"] for ticket in data["tickets"]),
            "questions_with_images": 0,
            "questions_with_hints": 0
        },
        "tickets_details": []
    }
    
    for ticket in data["tickets"]:
        ticket_info = {
            "ticket_number": ticket["ticket_number"],
            "questions_count": ticket["total_questions"],
            "questions_with_images": 0,
            "questions_with_hints": 0
        }
        
        for question in ticket["questions"]:
            if question.get("image_path"):
                ticket_info["questions_with_images"] += 1
                report["summary"]["questions_with_images"] += 1
            
            if question.get("hint") and question["hint"] != "Подсказка недоступна":
                ticket_info["questions_with_hints"] += 1
                report["summary"]["questions_with_hints"] += 1
        
        report["tickets_details"].append(ticket_info)
    
    with open('data/summary_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    print(f"\n📊 Сводный отчет создан: data/summary_report.json")
    return report

if __name__ == "__main__":
    print("🔍 Полный парсер данных с examenpdd.com")
    print("📋 Парсим: номера билетов, вопросы, ответы, изображения, подсказки")
    print("⚠️  Убедитесь, что у вас есть интернет-соединение")
    print("⏱️  Процесс может занять 10-15 минут...")
    
    input("\nНажмите Enter для продолжения...")
    
    # Парсим все данные
    data = scrape_all_tickets()
    
    # Создаем сводный отчет
    print("\n📊 Создаем сводный отчет...")
    report = create_summary_report(data)
    
    print(f"\n🎉 Готово!")
    print(f"📁 Все данные сохранены в папке 'data/'")
    print(f"📄 Основной файл: data/all_tickets.json")
    print(f"📊 Отчет: data/summary_report.json")
    print(f"🖼️  Изображения: data/images/tickets/")











