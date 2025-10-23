import requests
import os
import time
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse

def create_directories():
    """Создаем необходимые директории"""
    if not os.path.exists('images'):
        os.makedirs('images')
    if not os.path.exists('images/tickets'):
        os.makedirs('images/tickets')

def get_ticket_images(ticket_number):
    """Получаем изображения для конкретного билета"""
    url = f"https://examenpdd.com/bilet/{ticket_number}"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Ищем изображения вопросов
        images = []
        
        # Ищем все img теги
        img_tags = soup.find_all('img')
        
        for img in img_tags:
            src = img.get('src')
            if src:
                # Проверяем, что это изображение вопроса
                if 'question' in src.lower() or 'bilet' in src.lower() or 'ticket' in src.lower():
                    full_url = urljoin(url, src)
                    images.append(full_url)
        
        # Также ищем изображения в data-src или других атрибутах
        for img in soup.find_all('img', {'data-src': True}):
            src = img.get('data-src')
            if src and ('question' in src.lower() or 'bilet' in src.lower() or 'ticket' in src.lower()):
                full_url = urljoin(url, src)
                images.append(full_url)
        
        return images
        
    except Exception as e:
        print(f"Ошибка при получении билета {ticket_number}: {e}")
        return []

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
        
        print(f"✓ Скачано: {filename}")
        return True
        
    except Exception as e:
        print(f"✗ Ошибка скачивания {url}: {e}")
        return False

def get_file_extension(url):
    """Получаем расширение файла из URL"""
    parsed = urlparse(url)
    path = parsed.path
    if '.' in path:
        return path.split('.')[-1].lower()
    return 'jpg'  # По умолчанию jpg

def scrape_all_tickets():
    """Парсим все билеты"""
    create_directories()
    
    print("🚀 Начинаем парсинг изображений с examenpdd.com")
    print("=" * 50)
    
    total_images = 0
    successful_tickets = 0
    
    for ticket_num in range(1, 41):  # Билеты с 1 по 40
        print(f"\n📋 Обрабатываем билет {ticket_num}...")
        
        # Получаем изображения для билета
        images = get_ticket_images(ticket_num)
        
        if not images:
            print(f"⚠️  Изображения для билета {ticket_num} не найдены")
            continue
        
        print(f"📸 Найдено {len(images)} изображений")
        
        # Создаем папку для билета
        ticket_dir = f"images/tickets/ticket_{ticket_num:02d}"
        if not os.path.exists(ticket_dir):
            os.makedirs(ticket_dir)
        
        # Скачиваем каждое изображение
        for i, img_url in enumerate(images, 1):
            ext = get_file_extension(img_url)
            filename = f"{ticket_dir}/question_{i:02d}.{ext}"
            
            if download_image(img_url, filename):
                total_images += 1
        
        successful_tickets += 1
        
        # Небольшая пауза между запросами
        time.sleep(1)
    
    print("\n" + "=" * 50)
    print(f"✅ Парсинг завершен!")
    print(f"📊 Обработано билетов: {successful_tickets}/40")
    print(f"🖼️  Скачано изображений: {total_images}")
    print(f"📁 Изображения сохранены в папке: images/tickets/")

def create_image_mapping():
    """Создаем маппинг изображений для использования в приложении"""
    mapping = {}
    
    for ticket_num in range(1, 41):
        ticket_dir = f"images/tickets/ticket_{ticket_num:02d}"
        if os.path.exists(ticket_dir):
            images = []
            for file in sorted(os.listdir(ticket_dir)):
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.svg')):
                    images.append(f"images/tickets/ticket_{ticket_num:02d}/{file}")
            
            if images:
                mapping[ticket_num] = images
    
    # Сохраняем маппинг в JSON файл
    import json
    with open('image_mapping.json', 'w', encoding='utf-8') as f:
        json.dump(mapping, f, ensure_ascii=False, indent=2)
    
    print(f"📝 Создан файл маппинга: image_mapping.json")
    return mapping

if __name__ == "__main__":
    print("🔍 Парсер изображений с examenpdd.com")
    print("⚠️  Убедитесь, что у вас есть интернет-соединение")
    print("⏱️  Процесс может занять несколько минут...")
    
    input("\nНажмите Enter для продолжения...")
    
    # Парсим изображения
    scrape_all_tickets()
    
    # Создаем маппинг
    print("\n📋 Создаем маппинг изображений...")
    mapping = create_image_mapping()
    
    print("\n🎉 Готово! Теперь можно обновить приложение с новыми изображениями.")













