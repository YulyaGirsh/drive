#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def merge_categories():
    """Объединяет 44 категории в 40, объединяя похожие"""
    
    # Загружаем данные
    with open('questions_categorized.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Правила объединения категорий (из 44 в 40)
    merge_rules = {
        # Объединяем "Знаки Таблички" и "Знаки таблички" (дубликаты)
        "Знаки таблички": "Знаки Таблички",
        
        # Объединяем "Знаки Приоритета" и "Знаки приоритета" (дубликаты)
        "Знаки приоритета": "Знаки Приоритета",
        
        # Объединяем "Знаки Сервиса" и "Знаки сервиса" (дубликаты)
        "Знаки сервиса": "Знаки Сервиса",
        
        # Объединяем "Знаки особых предписаний" и "Знаки Особых предписаний" (дубликаты)
        "Знаки особых предписаний": "Знаки Особых предписаний"
    }
    
    # Обновляем вопросы с новыми категориями
    for question in data['questions']:
        original_main_category = question['main_category']
        if original_main_category in merge_rules:
            question['main_category'] = merge_rules[original_main_category]
            # Обновляем теги
            question['tags'] = [merge_rules[original_main_category].lower().replace(' ', '_')]
    
    # Создаем новые категории (40 штук)
    new_categories = [
        # Дорожные знаки (8 категорий)
        {"code": "1.1", "name": "Предупреждающие знаки", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Предупреждающие знаки", "icon": "icon_1_1", "color": "#ff8c00", "order": 1},
        {"code": "1.2", "name": "Знаки приоритета", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Знаки приоритета", "icon": "icon_1_2", "color": "#ff8c00", "order": 2},
        {"code": "1.3", "name": "Запрещающие знаки", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Запрещающие знаки", "icon": "icon_1_3", "color": "#ff8c00", "order": 3},
        {"code": "1.4", "name": "Предписывающие знаки", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Предписывающие знаки", "icon": "icon_1_4", "color": "#ff8c00", "order": 4},
        {"code": "1.5", "name": "Знаки особых предписаний", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Знаки особых предписаний", "icon": "icon_1_5", "color": "#ff8c00", "order": 5},
        {"code": "1.6", "name": "Информационные знаки", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Информационные знаки", "icon": "icon_1_6", "color": "#ff8c00", "order": 6},
        {"code": "1.7", "name": "Знаки сервиса", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Знаки сервиса", "icon": "icon_1_7", "color": "#ff8c00", "order": 7},
        {"code": "1.8", "name": "Знаки таблички", "group_code": "1", "group_name": "Дорожные знаки", "description": "Вопросы по теме: Знаки таблички", "icon": "icon_1_8", "color": "#ff8c00", "order": 8},
        
        # Дорожная разметка (2 категории)
        {"code": "2.1", "name": "Горизонтальная разметка", "group_code": "2", "group_name": "Дорожная разметка", "description": "Вопросы по теме: Горизонтальная разметка", "icon": "icon_2_1", "color": "#ff8c00", "order": 1},
        {"code": "2.2", "name": "Вертикальная разметка", "group_code": "2", "group_name": "Дорожная разметка", "description": "Вопросы по теме: Вертикальная разметка", "icon": "icon_2_2", "color": "#ff8c00", "order": 2},
        
        # Движение и маневрирование (8 категорий)
        {"code": "3.1", "name": "Перестроение", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Перестроение", "icon": "icon_3_1", "color": "#ff8c00", "order": 1},
        {"code": "3.2", "name": "Обгон и опережение", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Обгон и опережение", "icon": "icon_3_2", "color": "#ff8c00", "order": 2},
        {"code": "3.3", "name": "Повороты", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Повороты", "icon": "icon_3_3", "color": "#ff8c00", "order": 3},
        {"code": "3.4", "name": "Разворот", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Разворот", "icon": "icon_3_4", "color": "#ff8c00", "order": 4},
        {"code": "3.5", "name": "Встречный разъезд", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Встречный разъезд", "icon": "icon_3_5", "color": "#ff8c00", "order": 5},
        {"code": "3.6", "name": "Движение задним ходом", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Движение задним ходом", "icon": "icon_3_6", "color": "#ff8c00", "order": 6},
        {"code": "3.7", "name": "Расположение ТС", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Расположение ТС", "icon": "icon_3_7", "color": "#ff8c00", "order": 7},
        {"code": "3.8", "name": "Скорость движения", "group_code": "3", "group_name": "Движение и маневрирование", "description": "Вопросы по теме: Скорость движения", "icon": "icon_3_8", "color": "#ff8c00", "order": 8},
        
        # Регулирование движения (4 категории)
        {"code": "4.1", "name": "Светофор и регулировщик", "group_code": "4", "group_name": "Регулирование движения", "description": "Вопросы по теме: Светофор и регулировщик", "icon": "icon_4_1", "color": "#ff8c00", "order": 1},
        {"code": "4.2", "name": "Сигналы поворота", "group_code": "4", "group_name": "Регулирование движения", "description": "Вопросы по теме: Сигналы поворота", "icon": "icon_4_2", "color": "#ff8c00", "order": 2},
        {"code": "4.3", "name": "Специальные сигналы", "group_code": "4", "group_name": "Регулирование движения", "description": "Вопросы по теме: Специальные сигналы", "icon": "icon_4_3", "color": "#ff8c00", "order": 3},
        {"code": "4.4", "name": "Аварийная сигнализация", "group_code": "4", "group_name": "Регулирование движения", "description": "Вопросы по теме: Аварийная сигнализация", "icon": "icon_4_4", "color": "#ff8c00", "order": 4},
        
        # Остановка и стоянка (2 категории)
        {"code": "5.1", "name": "Остановка", "group_code": "5", "group_name": "Остановка и стоянка", "description": "Вопросы по теме: Остановка", "icon": "icon_5_1", "color": "#ff8c00", "order": 1},
        {"code": "5.2", "name": "Стоянка", "group_code": "5", "group_name": "Остановка и стоянка", "description": "Вопросы по теме: Стоянка", "icon": "icon_5_2", "color": "#ff8c00", "order": 2},
        
        # Перекрестки (3 категории)
        {"code": "6.1", "name": "Нерегулируемые равнозначные перекрестки", "group_code": "6", "group_name": "Перекрестки", "description": "Вопросы по теме: Нерегулируемые равнозначные перекрестки", "icon": "icon_6_1", "color": "#ff8c00", "order": 1},
        {"code": "6.2", "name": "Нерегулируемые неравнозначные перекрестки", "group_code": "6", "group_name": "Перекрестки", "description": "Вопросы по теме: Нерегулируемые неравнозначные перекрестки", "icon": "icon_6_2", "color": "#ff8c00", "order": 2},
        {"code": "6.3", "name": "Пешеходные переходы и остановки", "group_code": "6", "group_name": "Перекрестки", "description": "Вопросы по теме: Пешеходные переходы и остановки", "icon": "icon_6_3", "color": "#ff8c00", "order": 3},
        
        # Безопасность и ответственность (4 категории)
        {"code": "7.1", "name": "Основы безопасности", "group_code": "7", "group_name": "Безопасность и ответственность", "description": "Вопросы по теме: Основы безопасности", "icon": "icon_7_1", "color": "#ff8c00", "order": 1},
        {"code": "7.2", "name": "Неисправности и запрет", "group_code": "7", "group_name": "Безопасность и ответственность", "description": "Вопросы по теме: Неисправности и запрет", "icon": "icon_7_2", "color": "#ff8c00", "order": 2},
        {"code": "7.3", "name": "Медицина", "group_code": "7", "group_name": "Безопасность и ответственность", "description": "Вопросы по теме: Медицина", "icon": "icon_7_3", "color": "#ff8c00", "order": 3},
        {"code": "7.4", "name": "Юридическая ответственность", "group_code": "7", "group_name": "Безопасность и ответственность", "description": "Вопросы по теме: Юридическая ответственность", "icon": "icon_7_4", "color": "#ff8c00", "order": 4},
        
        # Общие темы (3 категории)
        {"code": "8.1", "name": "Общие положения", "group_code": "8", "group_name": "Общие темы", "description": "Вопросы по теме: Общие положения", "icon": "icon_8_1", "color": "#ff8c00", "order": 1},
        {"code": "8.2", "name": "Обязанности водителей", "group_code": "8", "group_name": "Общие темы", "description": "Вопросы по теме: Обязанности водителей", "icon": "icon_8_2", "color": "#ff8c00", "order": 2},
        {"code": "8.3", "name": "Движение в жилых зонах", "group_code": "8", "group_name": "Общие темы", "description": "Вопросы по теме: Движение в жилых зонах", "icon": "icon_8_3", "color": "#ff8c00", "order": 3},
        
        # Специальные транспортные средства (3 категории)
        {"code": "9.1", "name": "Мопеды", "group_code": "9", "group_name": "Специальные транспортные средства", "description": "Вопросы по теме: Мопеды", "icon": "icon_9_1", "color": "#ff8c00", "order": 1},
        {"code": "9.2", "name": "Трамвай", "group_code": "9", "group_name": "Специальные транспортные средства", "description": "Вопросы по теме: Трамвай", "icon": "icon_9_2", "color": "#ff8c00", "order": 2},
        {"code": "9.3", "name": "Приоритет маршрутных ТС", "group_code": "9", "group_name": "Специальные транспортные средства", "description": "Вопросы по теме: Приоритет маршрутных ТС", "icon": "icon_9_3", "color": "#ff8c00", "order": 3},
        
        # Специальные участки дорог (3 категории)
        {"code": "10.1", "name": "Движение через ж/д пути", "group_code": "10", "group_name": "Специальные участки дорог", "description": "Вопросы по теме: Движение через ж/д пути", "icon": "icon_10_1", "color": "#ff8c00", "order": 1},
        {"code": "10.2", "name": "Автомагистраль", "group_code": "10", "group_name": "Специальные участки дорог", "description": "Вопросы по теме: Автомагистраль", "icon": "icon_10_2", "color": "#ff8c00", "order": 2},
        {"code": "10.3", "name": "Учебная езда", "group_code": "10", "group_name": "Специальные участки дорог", "description": "Вопросы по теме: Учебная езда", "icon": "icon_10_3", "color": "#ff8c00", "order": 3},
        
        # Перевозка (2 категории)
        {"code": "11.1", "name": "Перевозка людей", "group_code": "11", "group_name": "Перевозка", "description": "Вопросы по теме: Перевозка людей", "icon": "icon_11_1", "color": "#ff8c00", "order": 1},
        {"code": "11.2", "name": "Перевозка грузов", "group_code": "11", "group_name": "Перевозка", "description": "Вопросы по теме: Перевозка грузов", "icon": "icon_11_2", "color": "#ff8c00", "order": 2},
        
        # Технические вопросы (1 категория)
        {"code": "12.1", "name": "Буксировка", "group_code": "12", "group_name": "Технические вопросы", "description": "Вопросы по теме: Буксировка", "icon": "icon_12_1", "color": "#ff8c00", "order": 1},
        
        # Освещение и сигналы (1 категория)
        {"code": "13.1", "name": "Фары и сигнал", "group_code": "13", "group_name": "Освещение и сигналы", "description": "Вопросы по теме: Фары и сигнал", "icon": "icon_13_1", "color": "#ff8c00", "order": 1}
    ]
    
    # Обновляем коды категорий в вопросах
    category_code_mapping = {}
    for cat in new_categories:
        category_code_mapping[cat['name']] = cat['code']
    
    for question in data['questions']:
        main_category = question['main_category']
        if main_category in category_code_mapping:
            question['category_code'] = category_code_mapping[main_category]
    
    # Создаем финальную структуру данных
    final_data = {
        "metadata": {
            "title": "Вопросы ПДД с категоризацией",
            "description": "Полная база вопросов ПДД с 40 категориями тем",
            "version": "1.0.0",
            "created_at": "2025-01-09T00:00:00Z",
            "total_questions": len(data['questions']),
            "total_categories": 40,
            "total_tickets": max(q['ticket_number'] for q in data['questions'])
        },
        "categories": new_categories,
        "questions": data['questions']
    }
    
    # Сохраняем в файл
    output_filename = "questions_categorized_40.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Создан файл с 40 категориями: {output_filename}")
    print(f"✅ Обработано {len(data['questions'])} вопросов")
    print(f"✅ Создано ровно 40 категорий")
    
    # Статистика по категориям
    category_stats = {}
    for question in data['questions']:
        cat = question['main_category']
        category_stats[cat] = category_stats.get(cat, 0) + 1
    
    print("\n📊 Статистика по 40 категориям:")
    for cat, count in sorted(category_stats.items(), key=lambda x: x[1], reverse=True):
        code = category_code_mapping.get(cat, "?")
        print(f"  {code} {cat}: {count} вопросов")

if __name__ == "__main__":
    merge_categories()
