#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json

def main():
    with open('questions_categorized_40_final.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"✅ Всего категорий: {len(data['categories'])}")
    print(f"✅ Всего вопросов: {len(data['questions'])}")
    print(f"✅ Всего билетов: {data['metadata']['total_tickets']}")
    
    if len(data['categories']) == 40:
        print("🎉 УСПЕХ! Создано ровно 40 категорий!")
    else:
        print(f"❌ ОШИБКА! Получено {len(data['categories'])} категорий вместо 40")
    
    print("\n📋 СПИСОК 40 КАТЕГОРИЙ:")
    print("=" * 60)
    
    for i, cat in enumerate(data['categories'], 1):
        print(f"{i:2d}. {cat['code']} {cat['name']} ({cat['group_name']})")

if __name__ == "__main__":
    main()
