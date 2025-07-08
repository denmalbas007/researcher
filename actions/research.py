import asyncio
import json
import warnings
from typing import Any, Callable, Optional, Union, Dict, List, Tuple
import re
from bs4 import BeautifulSoup
import aiohttp
from pydantic import TypeAdapter, model_validator, BaseModel, ConfigDict, Field

from researcher.actions.base import Action
from researcher.utils.logger import logger
from researcher.utils.search_engine import SearchEngine
from researcher.utils.web_browser import WebBrowserEngine
from researcher.utils.text import generate_prompt_chunk, reduce_message_length
from researcher.utils.llm import OpenAIClient

LANG_PROMPT = "Please respond in {language}."

RESEARCH_BASE_SYSTEM = """You are an AI critical thinker research assistant. Your sole purpose is to write well \
written, critically acclaimed, objective and structured reports on the given text."""

RESEARCH_TOPIC_SYSTEM = "You are an AI researcher assistant, and your research topic is:\n#TOPIC#\n{topic}"

SEARCH_TOPIC_PROMPT = """Please provide up to 2 necessary keywords related to your research topic for Google search. \
Your response must be in JSON format, for example: ["keyword1", "keyword2"]."""

SUMMARIZE_SEARCH_PROMPT = """### Requirements
1. The keywords related to your research topic and the search results are shown in the "Search Result Information" section.
2. Provide up to {decomposition_nums} queries related to your research topic base on the search results.
3. Please respond in the following JSON format: ["query1", "query2", "query3", ...].

### Search Result Information
{search_results}
"""

WEB_BROWSE_AND_SUMMARIZE_PROMPT = """### Requirements
1. The research question is: {query}
2. The content of the webpage is shown in the "Webpage Content" section.
3. Please provide a detailed summary of the content that is relevant to the research question.
4. If the content is not relevant to the research question, please respond with "Not relevant."

### Webpage Content
{content}
"""

CONDUCT_RESEARCH_PROMPT = """### Requirements
1. The research topic is: {topic}
2. The content for research is shown in the "Research Content" section.
3. Please provide a detailed research report that includes:
   - Introduction
   - Key Findings
   - Analysis
   - Conclusion
4. The report should be well-structured and objective.

### Research Content
{content}
"""

PROMPT_GENERATE_QUERIES = (
    "ВАЖНО: Сейчас 2025 год. Ищи актуальную информацию за 2024-2025 годы.\n"
    "Сгенерируй 3-5 поисковых запроса по теме: {topic} на русском языке и 3-5 на английском языке. "
    "Включи в запросы слова '2024', '2025', 'latest', 'recent' для поиска свежей информации. "
    "Ответь только в формате одного JSON-массива строк, без пояснений, без markdown, без комментариев, только массив в первой строке. "
    "Пример: [\"русский запрос 1 2025\", \"english query 1 2025\", ...]"
)

PROMPT_SUMMARIZE_PAGE = (
    "ВАЖНО: Сейчас 2025 год. Фокусируйся на актуальной информации 2024-2025 годов.\n"
    "Сделай сжатую, но максимально информативную выжимку только по теме '{topic}' из текста страницы ниже. "
    "Приоритет отдавай самой свежей информации. Укажи даты событий если они есть. "
    "Только ключевые факты, никакой воды, только важная информация, без вступлений и общих фраз. "
    "Ответь на русском.\n"
    "Текст страницы:\n{page_text}"
)

PROMPT_FINAL_REPORT = (
    "ВАЖНО: Сейчас 2025 год. В отчете обязательно укажи текущий год и фокусируйся на актуальной информации 2024-2025 годов.\n"
    "На основе следующих кратких выжимок с разных страниц по теме '{topic}' напиши очень подробный, максимально длинный, структурированный исследовательский отчет (200 000+ символов) на русском языке.\n\n"
    "В начале отчета обязательно укажи: 'Данный отчет подготовлен в 2025 году и содержит актуальную информацию.'\n\n"
    "Источники:\n{links_md}\n\n"
    "Также упоминай в отчете источники, из которых были взяты данные, их ссылки и названия.\n\n"
    "Таблица выжимок:\n{sources_md}\n\n"
    "В отчете обязательно должны быть таблицы с данными, только достоверные факты, никакой воды, никаких выдуманных данных.\n\n"
    "Обращай особое внимание на даты и временные рамки - приоритет актуальной информации 2024-2025 годов.\n\n"
    "САМОЕ ГЛАВНОЕ: НЕ ПИШИ ТОЙ ИНФОРМАЦИИ, КОТОРАЯ НЕ ОБНАРУЖЕНА В ВЫЖИМКАХ И ИСТОЧНИКАХ. ТОЛЬКО ТО, ЧТО ЕСТЬ В ВЫЖИМКАХ И ИСТОЧНИКАХ.\n\n"
)

OUTLINE_PROMPT = (
    "ВАЖНО: Сейчас 2025 год. План должен отражать актуальное состояние на 2025 год.\n"
    "На основе темы '{topic}' и кратких выжимок с разных страниц сгенерируй подробный, логичный, структурированный план исследовательского отчета. "
    "План должен включать все ключевые разделы, которые стоит раскрыть по теме, и быть максимально подробным. "
    "Включи разделы о текущем состоянии (2025), трендах и перспективах. "
    "Ответь ТОЛЬКО в формате JSON-массива строк с названиями разделов, без пояснений, без markdown, без комментариев. "
    "Пример: [\"Текущая ситуация на рынке в 2025 году\", \"Основные тренды 2024-2025\", \"Вызовы и возможности\", \"Прогнозы на будущее\"]\n\n"
    "Максимум 6 параграфов\n"
    "Вот краткие выжимки:\n{summaries_md}"
)

class SerperWrapper(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    api_key: str
    url: str = "https://google.serper.dev/search"
    payload: dict = Field(default_factory=lambda: {"page": 1, "num": 10})
    aiosession: Optional[aiohttp.ClientSession] = None
    proxy: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_serper(cls, values: dict) -> dict:
        if "serper_api_key" in values:
            values.setdefault("api_key", values["serper_api_key"])
            warnings.warn("`serper_api_key` is deprecated, use `api_key` instead", DeprecationWarning, stacklevel=2)

        if "api_key" not in values:
            raise ValueError(
                "To use serper search engine, make sure you provide the `api_key` when constructing an object. You can obtain "
                "an API key from https://serper.dev/."
            )

        return values

    async def run(self, query: str, max_results: int = 8, as_string: bool = True, **kwargs: Any) -> str:
        """Run query through Serper and parse result async."""
        if isinstance(query, str):
            return self._process_response((await self.results([query], max_results))[0], as_string=as_string)
        else:
            results = [self._process_response(res, as_string) for res in await self.results(query, max_results)]
        return "\n".join(results) if as_string else results

    async def results(self, queries: list[str], max_results: int = 8) -> dict:
        """Use aiohttp to run query through Serper and return the results async."""

        payloads = self.get_payloads(queries, max_results)
        headers = self.get_headers()

        if not self.aiosession:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.url, data=payloads, headers=headers, proxy=self.proxy) as response:
                    response.raise_for_status()
                    res = await response.json()
        else:
            async with self.aiosession.post(self.url, data=payloads, headers=headers, proxy=self.proxy) as response:
                response.raise_for_status()
                res = await response.json()

        return res

    def get_payloads(self, queries: list[str], max_results: int) -> Dict[str, str]:
        """Get payloads for Serper."""
        payloads = []
        for query in queries:
            _payload = {
                "q": query,
                "num": max_results,
            }
            payloads.append({**self.payload, **_payload})
        return json.dumps(payloads, sort_keys=True)

    def get_headers(self) -> Dict[str, str]:
        headers = {"X-API-KEY": self.api_key, "Content-Type": "application/json"}
        return headers

    @staticmethod
    def _process_response(res: dict, as_string: bool = False) -> str:
        """Process response from SerpAPI."""
        # logger.debug(res)
        focus = ["title", "snippet", "link"]

        def get_focused(x):
            return {i: j for i, j in x.items() if i in focus}

        if "error" in res.keys():
            raise ValueError(f"Got error from SerpAPI: {res['error']}")
        if "answer_box" in res.keys() and "answer" in res["answer_box"].keys():
            toret = res["answer_box"]["answer"]
        elif "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret = res["answer_box"]["snippet"]
        elif "answer_box" in res.keys() and "snippet_highlighted_words" in res["answer_box"].keys():
            toret = res["answer_box"]["snippet_highlighted_words"][0]
        elif "sports_results" in res.keys() and "game_spotlight" in res["sports_results"].keys():
            toret = res["sports_results"]["game_spotlight"]
        elif "knowledge_graph" in res.keys() and "description" in res["knowledge_graph"].keys():
            toret = res["knowledge_graph"]["description"]
        elif "organic" in res.keys() and len(res["organic"]) > 0 and "snippet" in res["organic"][0].keys():
            toret = res["organic"][0]["snippet"]
        else:
            toret = "No good search result found"

        toret_l = []
        if "answer_box" in res.keys() and "snippet" in res["answer_box"].keys():
            toret_l += [get_focused(res["answer_box"])]
        if res.get("organic"):
            toret_l += [get_focused(i) for i in res.get("organic")]

        return str(toret) + "\n" + str(toret_l) if as_string else toret_l

def extract_json_array(text):
    # Извлекаем все массивы и объединяем их в один список
    matches = re.findall(r'\[.*?\]', text, re.DOTALL)
    all_queries = []
    for m in matches:
        try:
            arr = json.loads(m)
            if isinstance(arr, list):
                all_queries.extend(arr)
        except Exception as e:
            logger.warning(f"Failed to parse extracted JSON array: {e}")
    return all_queries

class CollectLinks(Action):
    """Action to collect relevant links for research"""
    
    def is_valid_query(self, q: str) -> bool:
        if not q.strip():
            return False
        if len(q.split()) < 3:
            return False
        return True

    async def run(self, topic: str) -> List[dict]:
        """Collect relevant links for the given topic"""
        max_attempts = 5
        for attempt in range(1, max_attempts + 1):
            prompt = PROMPT_GENERATE_QUERIES.format(topic=topic)
            queries_raw = await self.llm.aask(prompt)
            queries_raw = re.sub(r"^```json|```$", "", queries_raw.strip(), flags=re.MULTILINE).strip()
            queries = extract_json_array(queries_raw)
            queries = [q for q in queries if isinstance(q, str) and self.is_valid_query(q)]
            logger.info(f"[CollectLinks] Attempt {attempt}: Generated queries: {queries}")
            if queries:
                break
            logger.warning(f"[CollectLinks] Attempt {attempt}: No valid queries generated by LLM. Retrying...")
        else:
            logger.warning("[CollectLinks] All attempts failed. Returning empty link list.")
            return []
        all_links = []
        serper = SerperWrapper(api_key="a38832aed2ee67b97da93293d15a7a521f224a5d")
        for query in queries:
            logger.info(f"[CollectLinks] Searching Serper for: {query}")
            await asyncio.sleep(2)
            results = await serper.run(query, max_results=5, as_string=False)
            for res in results:
                all_links.append({
                    "url": res.get("link"),
                    "title": res.get("title"),
                    "snippet": res.get("snippet")
                })
        logger.info(f"[CollectLinks] Collected links: {all_links}")
        return all_links

class WebBrowseAndSummarize(Action):
    """Action to browse web pages and summarize their content"""
    
    async def fetch_text(self, url: str) -> str:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as resp:
                    html = await resp.text(errors='ignore')
            soup = BeautifulSoup(html, 'html.parser')
            for tag in soup(['script', 'style']):
                tag.decompose()
            text = soup.get_text(separator=' ', strip=True)
            return text[:32000]
        except Exception as e:
            return f"[Error fetching {url}: {e}]"

    async def summarize_one(self, topic: str, link: dict) -> dict:
        url = link.get('url')
        page_text = await self.fetch_text(url)
        prompt = PROMPT_SUMMARIZE_PAGE.format(topic=topic, page_text=page_text)
        self.llm.model = 'gpt-4o-mini'
        summary = await self.llm.aask(prompt)
        return {
            'url': url,
            'title': link.get('title'),
            'summary': summary
        }

    async def run(self, topic: str, links: list) -> list:
        tasks = [self.summarize_one(topic, link) for link in links]
        summaries = await asyncio.gather(*tasks)
        logger.info(f"[WebBrowseAndSummarize] Summaries: {summaries}")
        return summaries

class GenerateOutline(Action):
    """Action to generate a detailed outline for the research report"""
    async def run(self, topic: str, summaries: list) -> str:
        # Формируем markdown-таблицу выжимок
        summaries_md = "\n".join(f"- {item.get('summary', '')}" for item in summaries)
        prompt = OUTLINE_PROMPT.format(topic=topic, summaries_md=summaries_md)
        self.llm.model = 'gpt-4o-mini'
        outline_raw = await self.llm.aask(prompt)
        # Парсим JSON-массив с названиями разделов
        try:
            section_titles = json.loads(outline_raw)
            if not isinstance(section_titles, list):
                raise ValueError("Outline is not a list")
            # Формируем markdown-список для совместимости
            outline = "\n".join(f"{i+1}. {title}" for i, title in enumerate(section_titles))
            return outline
        except Exception as e:
            logger.warning(f"Failed to parse outline as JSON: {e}. Falling back to regex parsing.")
            # Fallback: парсим как markdown-список
            section_titles = re.findall(r'^\s*\d+\.\s+(.+)', outline_raw, re.MULTILINE)
            if not section_titles:
                section_titles = ["Full Report"]
            return outline_raw

class ConductResearch(Action):
    """Action to conduct research using collected information"""
    async def run(self, topic: str, summaries: list, outline: str = None) -> str:
        sources_md = "| № | Title | URL | Summary |\n|---|------|-----|---------|\n"
        links_md = "\n".join(f"- [{item.get('title') or item.get('url')}]({item.get('url')})" for item in summaries)
        for i, item in enumerate(summaries, 1):
            title = (item.get('title') or '').replace('|', ' ')
            url = item.get('url') or ''
            summary = (item.get('summary') or '').replace('|', ' ')
            sources_md += f"| {i} | {title[:60]} | {url} | {summary[:200]} |\n"
        # Парсим outline на разделы (ищем строки вида '1. ...', '2. ...', ...)
        section_titles = []
        if outline:
            section_titles = re.findall(r'^\s*\d+\.\s+(.+)', outline, re.MULTILINE)
        if not section_titles:
            # fallback: один большой раздел
            section_titles = ["Full Report"]
        # Генерируем каждый раздел отдельно
        sections = []
        for idx, section in enumerate(section_titles, 1):
            # Собираем названия других разделов для исключения дублирования
            other_sections = [s for i, s in enumerate(section_titles, 1) if i != idx]
            other_sections_text = "\n".join(f"- {s}" for s in other_sections)
            
            prompt = (
                f"Раздел отчета: {section}\n"
                f"Тема: {topic}\n"
                f"ВАЖНО: Текущий год - 2025. Используй только актуальную информацию, относящуюся к 2025 году или более позднему периоду. Если в источниках есть устаревшие данные, укажи это явно.\n"
                f"Источники:\n{links_md}\n"
                f"Таблица выжимок:\n{sources_md}\n"
                f"План отчета:\n{outline}\n\n"
                f"ВАЖНО: В этом разделе НЕ НУЖНО писать информацию по следующим темам, так как они будут раскрыты в других разделах:\n{other_sections_text}\n\n"
                f"Сгенерируй подробный, текст для этого раздела отчета, используя только факты из выжимок и источников. Не выдумывай данные. Включай таблицы, если это уместно. Пиши только по теме раздела, избегая дублирования с другими разделами. также не пиши вступление и заключение, только текст раздела\n"
            )
            self.llm.model = 'gpt-4o-mini'
            section_text = await self.llm.aask(prompt)
            sections.append(f"## {idx}. {section}\n\n{section_text}")
        # Склеиваем все разделы
        report = f"# Исследовательский отчет по теме: {topic}\n\n"
        report += f"### Ссылки-источники\n{links_md}\n\n"
        report += f"### План отчета\n{outline}\n\n"
        report += f"### Таблица выжимок\n{sources_md}\n\n"
        report += "\n\n".join(sections)
        return report

def get_research_system_text(language: str = "en-us") -> str:
    """Get system text for research actions"""
    current_year_context = "ВАЖНО: Сейчас 2025 год. Всегда учитывай это при анализе и поиске информации. Приоритет - актуальная информация 2024-2025 годов."
    
    if language == "Ru-ru":
        return f"""Ты профессиональный исследователь.Текущий год: 2025.Ваша задача заключается в:
1. Сбор актуальной информации (приоритет 2024-2025 гг.)
2. Анализировать информацию
3. Создание отчета об исследовании
Пожалуйста, убедитесь в точности, актуальности и своевременности предоставляемой информации.Сосредоточьтесь на последних разработках и тенденциях."""
    else:
        return f"""You are a professional researcher. Current year: 2025. Your tasks are to:
1. Collect relevant and current information (prioritize 2024-2025 data)
2. Analyze the information with focus on recent developments
3. Generate research reports with current context
Please ensure the accuracy, relevance and timeliness of the information. Focus on latest developments and trends.

{current_year_context}"""
