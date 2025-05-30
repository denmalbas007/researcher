import asyncio
import re
from pathlib import Path
from typing import List, Optional
import logging
import markdown
from weasyprint import HTML
from pydantic import BaseModel
import hashlib
from datetime import datetime

from researcher.actions.research import CollectLinks, ConductResearch, WebBrowseAndSummarize, GenerateOutline, get_research_system_text
from researcher.actions.base import Action
from researcher.utils.logger import logger

RESEARCH_PATH = Path("research_reports")

def create_safe_filename(topic: str, max_length: int = 80) -> str:
    """
    Создаёт безопасное имя файла из темы исследования.
    
    Args:
        topic: Тема исследования
        max_length: Максимальная длина имени файла (без расширения)
    
    Returns:
        Безопасное имя файла
    """
    # Убираем недопустимые символы
    filename = re.sub(r'[\/:":*?<>|]+', " ", topic)
    filename = filename.replace("\n", " ").replace("\r", " ")
    # Убираем лишние пробелы
    filename = re.sub(r'\s+', ' ', filename).strip()
    
    # Обрезаем до максимальной длины
    if len(filename) > max_length:
        filename = filename[:max_length].strip()
    
    # Если имя пустое или состоит только из пробелов, создаём имя с timestamp
    if not filename or filename.isspace():
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"research_report_{timestamp}"
    
    return filename

class ResearchReport(BaseModel):
    """Research report model"""
    content: str
    references: Optional[List[dict]] = None
    summaries: Optional[List[dict]] = None
    pdf_path: Optional[str] = None

class Researcher:
    """Researcher role that conducts research on a given topic"""
    
    def __init__(self, language: str = "en-us"):
        self.language = language
        self.actions: List[Action] = [
            CollectLinks(),
            WebBrowseAndSummarize(),
            GenerateOutline(),
            ConductResearch()
        ]
        
        # Set system message for all actions
        system_text = get_research_system_text(language)
        for action in self.actions:
            action.system_text = system_text
    
    async def generate_section(self, topic: str, section: str, idx: int, total_sections: int, all_sections: list, progress_callback=None) -> str:
        """Generate a single section of the report"""
        # Собираем названия других разделов для исключения дублирования
        other_sections = [s for i, s in enumerate(all_sections, 1) if i != idx]
        other_sections_text = "\n".join(f"- {s}" for s in other_sections)
        
        # Проверяем, является ли раздел введением или заключением
        section_lower = section.lower()
        if any(keyword in section_lower for keyword in ['введение', 'заключение', 'выводы', 'резюме', 'summary', 'conclusion', 'introduction']):
            # Пропускаем введение и заключение
            return ""
        
        prompt = (
            f"Раздел отчета: {section}\n"
            f"Тема: {topic}\n"
            f"ВАЖНО: Текущий год - 2025. Используй только актуальную информацию 2024-2025 годов. Если в источниках есть устаревшие данные, явно укажи их дату и отметь, что информация может быть неактуальной.\n"
            f"ВАЖНО: В этом разделе НЕ НУЖНО писать информацию по следующим темам, так как они будут раскрыты в других разделах:\n{other_sections_text}\n\n"
            f"Сгенерируй подробный текст ТОЛЬКО для раздела '{section}', используя только факты из выжимок и источников. "
            f"Приоритет отдавай самой свежей информации. Укажи конкретные даты событий если они есть в источниках. "
            f"Не выдумывай данные. Включай таблицы, если это уместно. "
            f"НЕ ПИШИ введение или заключение для этого раздела, только основной текст по теме раздела. "
            f"Избегай дублирования с другими разделами.\n"
        )
        
        section_text = await self.actions[3].llm.aask(prompt)
        return f"## {idx}. {section}\n\n{section_text}"

    async def run(self, topic: str, progress_callback=None) -> ResearchReport:
        """Run research on the given topic"""
        logger.info(f"[Researcher] Start research for topic: {topic}")
        if progress_callback:
            await progress_callback(0, "collect_links", "")
        links = await self.actions[0].run(topic)
        logger.info(f"[Researcher] Links collected: {len(links)}")
        if progress_callback:
            await progress_callback(10, "summarize", "")
        summaries = await self.actions[1].run(topic, links)
        logger.info(f"[Researcher] Summaries collected: {len(summaries)}")
        if progress_callback:
            await progress_callback(30, "outline", "")
        outline = await self.actions[2].run(topic, summaries)
        logger.info(f"[Researcher] Outline generated: {outline}")
        if progress_callback:
            await progress_callback(40, "report", "начало генерации разделов")
        
        # Генерируем каждый раздел отдельно и обновляем прогресс
        section_titles = re.findall(r'^\s*\d+\.\s+(.+)', outline, re.MULTILINE) if outline else []
        if not section_titles:
            section_titles = ["Full Report"]
        
        # Возвращаем параллельную генерацию разделов для скорости
        if progress_callback:
            await progress_callback(45, "report", f"генерация {len(section_titles)} разделов параллельно")
        
        # Создаем задачи для асинхронной генерации разделов
        tasks = []
        for idx, section in enumerate(section_titles, 1):
            task = self.generate_section(topic, section, idx, len(section_titles), section_titles, None)  # Убираем progress_callback
            tasks.append(task)
        
        # Запускаем все задачи параллельно
        sections = await asyncio.gather(*tasks)
        
        if progress_callback:
            await progress_callback(90, "report", "объединение разделов")
        
        # Фильтруем пустые разделы (введение и заключение)
        non_empty_sections = [section for section in sections if section.strip()]
        
        report = f"# Исследовательский отчет по теме: {topic}\n\n"
        report += "\n\n".join(non_empty_sections)
        
        # Генерируем PDF
        if progress_callback:
            await progress_callback(95, "pdf", "создание PDF документа")
        pdf_path = self.generate_pdf(topic, report)
        
        if progress_callback:
            await progress_callback(100, "done", "")
            
        return ResearchReport(
            content=report,
            references=links,
            summaries=summaries,
            pdf_path=pdf_path
        )

    def generate_pdf(self, topic: str, content: str) -> str:
        """Generate PDF from markdown content"""
        # Convert markdown to HTML
        html = markdown.markdown(content, extensions=['tables', 'codehilite'])
        
        # Add comprehensive styling
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
        
        # Create PDF with safe filename
        filename = create_safe_filename(topic)
        if not RESEARCH_PATH.exists():
            RESEARCH_PATH.mkdir(parents=True)
        pdf_path = RESEARCH_PATH / f"{filename}.pdf"
        
        # Generate PDF with better options
        HTML(string=styled_html).write_pdf(
            pdf_path,
            stylesheets=None,
            presentational_hints=True,
            optimize_images=True
        )
        return str(pdf_path)

    def write_report(self, topic: str, content: str):
        """Write the research report to a file.

        Args:
            topic: The research topic.
            content: The report content.
        """
        filename = create_safe_filename(topic)
        if not RESEARCH_PATH.exists():
            RESEARCH_PATH.mkdir(parents=True)
        filepath = RESEARCH_PATH / f"{filename}.md"
        filepath.write_text(content)
        logger.info(f"[Researcher] Report saved to {filepath}") 