import streamlit as st
import requests
import time
import os
from pathlib import Path

st.set_page_config(page_title="AI Researcher Demo", layout="wide")

# Добавляем пользовательские стили CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        text-align: center;
        margin: 0;
        font-size: 2.5rem;
    }
    .success-banner {
        background: linear-gradient(90deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
        color: white;
        font-weight: bold;
    }
    .info-card {
        background: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 4px solid #667eea;
        margin: 1rem 0;
    }
    .summary-container {
        background: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .download-section {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    .stExpander > div > div > div > div {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

# Заголовок с градиентом
st.markdown('<div class="main-header"><h1>🤖 AI Researcher: Автоматический исследователь</h1></div>', unsafe_allow_html=True)

API_URL = "http://localhost:8000/research"
STATUS_URL = "http://localhost:8000/status/{}"
RESULT_URL = "http://localhost:8000/result/{}"

# Инициализируем session state для сохранения результатов
if 'research_result' not in st.session_state:
    st.session_state.research_result = None
if 'research_topic' not in st.session_state:
    st.session_state.research_topic = None

# Основная форма
st.markdown("### 📝 Введите тему для исследования")
with st.form("research_form"):
    topic = st.text_area(
        "Тема исследования:", 
        height=80,
        placeholder="Например: Влияние искусственного интеллекта на рынок труда в 2024-2025 годах"
    )
    
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        submitted = st.form_submit_button("🚀 Запустить исследование", use_container_width=True)

if submitted and topic.strip():
    # Сохраняем тему в session state
    st.session_state.research_topic = topic.strip()
    
    progress_text = st.empty()
    progress_bar = st.progress(0)
    
    with st.spinner("🔍 Выполняется исследование, пожалуйста, подождите..."):
        try:
            # Отправляем запрос и получаем topic_id
            response = requests.post(API_URL, json={"topic": topic.strip()})
            if response.status_code == 200:
                topic_id = response.json().get("topic_id")
                
                # Polling статуса с более информативными сообщениями
                while True:
                    status = requests.get(STATUS_URL.format(topic_id)).json()
                    progress = status.get("progress", 0)
                    stage = status.get("stage", "")
                    section = status.get("section", "")
                    progress_bar.progress(progress)
                    
                    if stage == "report" and section:
                        if "раздел" in section:
                            progress_text.text(f"📝 Генерируется {section}")
                        else:
                            progress_text.text(f"📝 {section}")
                    elif stage == "collect_links":
                        progress_text.text("🔗 Сбор ссылок и источников...")
                    elif stage == "summarize":
                        progress_text.text("📄 Анализ и суммаризация страниц...")
                    elif stage == "outline":
                        progress_text.text("📋 Создание структуры отчета...")
                    elif stage == "pdf":
                        progress_text.text("📄 Создание PDF документа...")
                    elif stage == "done":
                        progress_text.text("✅ Исследование завершено!")
                        break
                    elif stage == "error":
                        st.error(f"❌ Ошибка: {section}")
                        break
                    time.sleep(1)
                
                # Получаем результат
                result = requests.get(RESULT_URL.format(topic_id)).json()
                
                # Сохраняем результат в session state
                st.session_state.research_result = result
                
                # Показываем баннер успеха
                st.markdown('<div class="success-banner">🎉 Исследование успешно завершено!</div>', unsafe_allow_html=True)
                
        except Exception as e:
            st.error(f"❌ Ошибка при обращении к API: {e}")

# Отображаем результаты, если они есть в session state
if st.session_state.research_result:
    result = st.session_state.research_result
    
    # Секция управления с кнопками
    st.markdown('<div class="download-section">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if result.get("pdf_path"):
            with open(result["pdf_path"], "rb") as f:
                pdf_data = f.read()
            st.download_button(
                label="📄 Скачать отчет в PDF",
                data=pdf_data,
                file_name=os.path.basename(result["pdf_path"]),
                mime="application/pdf",
                use_container_width=True
            )
    
    with col2:
        # Показываем размер файла если есть PDF
        if result.get("pdf_path"):
            file_size = len(pdf_data) / 1024  # KB
            if file_size > 1024:
                st.info(f"📊 Размер файла: {file_size/1024:.1f} MB")
            else:
                st.info(f"📊 Размер файла: {file_size:.1f} KB")
    
    with col3:
        if st.button("🗑️ Очистить", use_container_width=True):
            st.session_state.research_result = None
            st.session_state.research_topic = None
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Основной отчет
    st.markdown("---")
    st.subheader(f"📋 Исследовательский отчет")
    st.markdown(f"**Тема:** {st.session_state.research_topic}")
    
    # Добавляем информацию о времени создания
    st.markdown(f"**Создан:** {time.strftime('%d.%m.%Y в %H:%M')}")
    
    st.markdown("---")
    st.markdown(result["report"])
    
    # Статистика
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        sources_count = len(result.get("references", []))
        st.metric("🔗 Источников", sources_count)
    with col2:
        summaries_count = len(result.get("summaries", []))
        st.metric("📝 Суммаризаций", summaries_count)
    with col3:
        word_count = len(result["report"].split())
        st.metric("📊 Слов в отчете", word_count)
    
    # Сворачиваемые разделы с улучшенным дизайном
    with st.expander("🔗 Источники и ссылки", expanded=False):
        if result.get("references"):
            st.success(f"Найдено и обработано **{len(result['references'])}** источников")
            
            for i, ref in enumerate(result["references"], 1):
                with st.container():
                    url = ref.get("url")
                    title = ref.get("title") or "Без названия"
                    
                    col1, col2 = st.columns([1, 10])
                    with col1:
                        st.write(f"**{i}.**")
                    with col2:
                        st.markdown(f"[{title}]({url})")
                        st.caption(f"🌐 {url}")
                    
                    if i < len(result["references"]):
                        st.divider()
        else:
            st.warning("Источники не найдены")
    
    with st.expander("📝 Краткие выжимки по страницам", expanded=False):
        if result.get("summaries"):
            st.success(f"Обработано **{len(result['summaries'])}** веб-страниц")
            
            # Инициализируем состояние для показа полных суммаризаций
            if 'show_full_summaries' not in st.session_state:
                st.session_state.show_full_summaries = set()
            
            for i, summ in enumerate(result["summaries"], 1):
                with st.container():
                    st.markdown(f"### {i}. {summ.get('title') or 'Без названия'}")
                    st.caption(f"🌐 [{summ.get('url')}]({summ.get('url')})")
                    
                    # Обрабатываем суммаризацию
                    summary_text = summ.get("summary", "Суммаризация не доступна")
                    summary_key = f"summary_{i}"
                    
                    if len(summary_text) > 300:
                        # Показываем сокращенную версию
                        if summary_key not in st.session_state.show_full_summaries:
                            st.markdown(f'<div class="summary-container">{summary_text[:300]}...</div>', unsafe_allow_html=True)
                            if st.button(f"📖 Показать полностью ({len(summary_text)} символов)", key=f"show_{summary_key}"):
                                st.session_state.show_full_summaries.add(summary_key)
                                st.rerun()
                        else:
                            # Показываем полную версию
                            st.markdown(f'<div class="summary-container">{summary_text}</div>', unsafe_allow_html=True)
                            if st.button(f"📝 Свернуть", key=f"hide_{summary_key}"):
                                st.session_state.show_full_summaries.discard(summary_key)
                                st.rerun()
                    else:
                        # Короткая суммаризация - показываем полностью
                        st.markdown(f'<div class="summary-container">{summary_text}</div>', unsafe_allow_html=True)
                    
                    if i < len(result["summaries"]):
                        st.divider()
        else:
            st.warning("Суммаризации не найдены")

else:
    # Приветственное сообщение
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("""
    ### 🎯 Как это работает:
    
    1. **Введите тему** - опишите, что вы хотите исследовать
    2. **Запустите анализ** - ИИ найдет и проанализирует релевантные источники
    3. **Получите отчет** - структурированный отчет с источниками и выводами
    4. **Скачайте PDF** - красиво оформленный документ для сохранения
    
    ### 💡 Примеры тем:
    - Тенденции развития ИИ в 2024-2025 годах
    - Влияние блокчейна на финансовый сектор
    - Экологические технологии в энергетике
    - Новые методы лечения онкологических заболеваний
    """)
    st.markdown('</div>', unsafe_allow_html=True) 