#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def main():
    with open('questions_categorized_40.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Всего категорий: {len(data['categories'])}")
    print(f"✅ Всего вопросов: {len(data['questions'])}")
    print(f"✅ Всего билетов: {data['metadata']['total_tickets']}")
    
    print("\n📋 СПИСОК 40 КАТЕГОРИЙ:")
    print("=" * 60)
    
    for i, cat in enumerate(data['categories'], 1):
        print(f"{i:2d}. {cat['code']} {cat['name']} ({cat['group_name']})")
    
    print("\n📊 ПРОВЕРКА УНИКАЛЬНОСТИ:")
    category_names = [cat['name'] for cat in data['categories']]
    unique_names = set(category_names)
    print(f"Уникальных названий: {len(unique_names)}")
    print(f"Всего категорий: {len(category_names)}")
    
    if len(unique_names) == len(category_names):
        print("✅ Все категории уникальны!")
    else:
        print("❌ Есть дубликаты!")
        duplicates = [name for name in category_names if category_names.count(name) > 1]
        print(f"Дубликаты: {set(duplicates)}")

if __name__ == "__main__":
    main()
