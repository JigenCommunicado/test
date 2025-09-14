#!/usr/bin/env python3
"""
Простая проверка Excel файла
"""

import os

def check_excel():
    excel_file = "data/все_заявки.xlsx"
    
    print(f"Проверка файла: {excel_file}")
    print(f"Существует: {os.path.exists(excel_file)}")
    
    if os.path.exists(excel_file):
        size = os.path.getsize(excel_file)
        print(f"Размер: {size} байт")
        
        if size == 0:
            print("⚠️  Файл пустой!")
        else:
            print("✅ Файл не пустой")

if __name__ == "__main__":
    check_excel()


