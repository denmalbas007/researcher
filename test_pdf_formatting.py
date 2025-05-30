#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from roles.researcher import create_safe_filename
import markdown
from weasyprint import HTML
from pathlib import Path

def test_pdf_formatting():
    """Test PDF formatting with tables and various content"""
    
    # Sample markdown content with tables
    markdown_content = """
# Тестовый отчет по форматированию PDF

## 1. Введение

Это тестовый отчет для проверки качества форматирования PDF-документов с таблицами и другими элементами.

## 2. Основные показатели

### 2.1 Таблица гиперпараметров

| Гиперпараметр | Возможные значения | Рекомендации |
|---------------|-------------------|--------------|
| Скорость обучения | 0.001, 0.01, 0.1 | Начинать с малых значений, использовать адаптивные методы |
| Размер батча | 32, 64, 128 | Размер батча должен быть кратен размеру GPU памяти |
| Количество эпох | 10, 50, 100 | Следует контролировать сходимость на валидационной выборке |

### 2.2 Результаты экспериментов

| Модель | Точность | Время обучения | Размер модели |
|--------|----------|----------------|---------------|
| BERT-base | 85.4% | 2.5 часа | 110M параметров |
| RoBERTa | 87.1% | 3.2 часа | 125M параметров |
| GPT-3.5 | 91.2% | N/A | 175B параметров |

## 3. Проблемы с градиентами

Несмотря на успехи заранее обученных составных сетей, которые помогают решить проблему исчезающих градиентов в глубоких нейронных сетях, все еще существуют проблемы с:

- Взрывающимися градиентами
- Переобучением на малых датасетах  
- Неустойчивостью при обучении

### 3.1 Методы решения

1. **Gradient Clipping** - ограничение нормы градиентов
2. **Dropout** - случайное отключение нейронов
3. **Batch Normalization** - нормализация входов слоев

```python
# Пример кода для gradient clipping
torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
```

## 4. Заключение

Современные методы машинного обучения показывают отличные результаты при правильной настройке гиперпараметров и использовании соответствующих техник регуляризации.

> **Важно**: Всегда тестируйте модель на отложенной выборке перед развертыванием в продакшене.

### Ссылки
- [Документация PyTorch](https://pytorch.org/docs/)
- [Hugging Face Transformers](https://huggingface.co/docs/transformers/)
"""

    # Convert markdown to HTML with table extension
    html = markdown.markdown(markdown_content, extensions=['tables', 'codehilite'])
    
    # Apply the same styling as in the main code
    styled_html = f"""
    <!DOCTYPE html>
    <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{
                    margin: 2cm;
                    size: A4;
                    @bottom-center {{
                        content: counter(page);
                    }}
                }}
                
                body {{
                    font-family: 'Arial', 'DejaVu Sans', sans-serif;
                    line-height: 1.6;
                    color: #333;
                    font-size: 12px;
                    margin: 0;
                    padding: 0;
                }}
                
                h1 {{
                    color: #2c3e50;
                    border-bottom: 3px solid #3498db;
                    padding-bottom: 10px;
                    margin-bottom: 30px;
                    font-size: 24px;
                    page-break-after: avoid;
                }}
                
                h2 {{
                    color: #34495e;
                    margin-top: 40px;
                    margin-bottom: 20px;
                    font-size: 18px;
                    border-left: 4px solid #3498db;
                    padding-left: 15px;
                    page-break-after: avoid;
                }}
                
                h3 {{
                    color: #2c3e50;
                    margin-top: 30px;
                    margin-bottom: 15px;
                    font-size: 16px;
                    page-break-after: avoid;
                }}
                
                p {{
                    margin-bottom: 15px;
                    text-align: justify;
                    text-indent: 0;
                }}
                
                a {{
                    color: #3498db;
                    text-decoration: none;
                }}
                
                a:hover {{
                    text-decoration: underline;
                }}
                
                /* Стили для таблиц */
                table {{
                    width: 100%;
                    border-collapse: collapse;
                    margin: 25px 0;
                    font-size: 11px;
                    min-width: 400px;
                    box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
                    page-break-inside: avoid;
                }}
                
                table thead tr {{
                    background-color: #3498db;
                    color: #ffffff;
                    text-align: left;
                }}
                
                table th,
                table td {{
                    padding: 12px 15px;
                    border: 1px solid #dddddd;
                    text-align: left;
                    vertical-align: top;
                    word-wrap: break-word;
                }}
                
                table th {{
                    font-weight: bold;
                    background-color: #3498db;
                    color: white;
                }}
                
                table tbody tr {{
                    border-bottom: 1px solid #dddddd;
                }}
                
                table tbody tr:nth-of-type(even) {{
                    background-color: #f8f9fa;
                }}
                
                table tbody tr:last-of-type {{
                    border-bottom: 2px solid #3498db;
                }}
                
                /* Стили для списков */
                ul, ol {{
                    margin: 15px 0;
                    padding-left: 30px;
                }}
                
                li {{
                    margin-bottom: 8px;
                    line-height: 1.5;
                }}
                
                /* Стили для блоков кода */
                code {{
                    background-color: #f4f4f4;
                    padding: 2px 6px;
                    border-radius: 3px;
                    font-family: 'Courier New', monospace;
                    font-size: 11px;
                }}
                
                pre {{
                    background-color: #f4f4f4;
                    padding: 15px;
                    border-radius: 5px;
                    border-left: 4px solid #3498db;
                    overflow-x: auto;
                    margin: 20px 0;
                }}
                
                /* Стили для цитат */
                blockquote {{
                    border-left: 4px solid #bdc3c7;
                    margin: 20px 0;
                    padding: 10px 20px;
                    background-color: #f8f9fa;
                    font-style: italic;
                }}
                
                /* Разрывы страниц */
                .page-break {{
                    page-break-before: always;
                }}
                
                /* Избегаем разрывов внутри важных элементов */
                h1, h2, h3, h4, h5, h6 {{
                    page-break-after: avoid;
                    page-break-inside: avoid;
                }}
                
                table, figure, img {{
                    page-break-inside: avoid;
                }}
                
                /* Стили для мета-информации */
                .meta-info {{
                    background-color: #ecf0f1;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 20px 0;
                    border-left: 4px solid #95a5a6;
                }}
                
                .meta-info h3 {{
                    margin-top: 0;
                    color: #7f8c8d;
                }}
            </style>
        </head>
        <body>
            {html}
        </body>
    </html>
    """
    
    # Create test PDF
    research_path = Path("research_reports")
    if not research_path.exists():
        research_path.mkdir(parents=True)
    
    pdf_path = research_path / "test_formatting.pdf"
    
    # Generate PDF
    HTML(string=styled_html).write_pdf(
        pdf_path,
        stylesheets=None,
        presentational_hints=True,
        optimize_images=True
    )
    
    print(f"Тестовый PDF создан: {pdf_path}")
    print("Проверьте качество форматирования таблиц и других элементов.")

if __name__ == "__main__":
    test_pdf_formatting() 