import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, ConnectionPatch, Rectangle
import numpy as np

# Настройка русского шрифта
plt.rcParams['font.family'] = ['DejaVu Sans', 'Arial Unicode MS', 'Tahoma']
plt.rcParams['axes.unicode_minus'] = False

def create_ml_pipeline_diagram():
    """Создает схему ML pipeline и взаимодействия агентов"""
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 20))
    
    # === СХЕМА 1: ML PIPELINE ===
    ax1.set_xlim(0, 10)
    ax1.set_ylim(0, 12)
    ax1.set_title('AI Researcher - ML Pipeline Architecture', fontsize=16, fontweight='bold', pad=20)
    
    # Цвета для разных типов компонентов
    colors = {
        'input': '#E8F4FD',      # Светло-голубой
        'processing': '#FFF2CC',  # Светло-желтый
        'ai': '#D5E8D4',         # Светло-зеленый
        'output': '#F8CECC',     # Светло-красный
        'storage': '#E1D5E7'     # Светло-фиолетовый
    }
    
    # Входные данные
    input_box = FancyBboxPatch((0.5, 10), 2, 1, boxstyle="round,pad=0.1", 
                               facecolor=colors['input'], edgecolor='black', linewidth=2)
    ax1.add_patch(input_box)
    ax1.text(1.5, 10.5, 'User Input\n(Research Topic)', ha='center', va='center', fontweight='bold')
    
    # API Gateway
    api_box = FancyBboxPatch((4, 10), 2, 1, boxstyle="round,pad=0.1",
                             facecolor=colors['processing'], edgecolor='black', linewidth=2)
    ax1.add_patch(api_box)
    ax1.text(5, 10.5, 'FastAPI\nGateway', ha='center', va='center', fontweight='bold')
    
    # Task Queue
    queue_box = FancyBboxPatch((7.5, 10), 2, 1, boxstyle="round,pad=0.1",
                               facecolor=colors['storage'], edgecolor='black', linewidth=2)
    ax1.add_patch(queue_box)
    ax1.text(8.5, 10.5, 'Background\nTask Queue', ha='center', va='center', fontweight='bold')
    
    # Researcher Agent
    researcher_box = FancyBboxPatch((4, 8), 2, 1.5, boxstyle="round,pad=0.1",
                                    facecolor=colors['ai'], edgecolor='black', linewidth=3)
    ax1.add_patch(researcher_box)
    ax1.text(5, 8.75, 'Researcher\nAgent', ha='center', va='center', fontweight='bold', fontsize=12)
    
    # Action Pipeline
    actions = [
        ('CollectLinks', 6.5),
        ('WebBrowse\n& Summarize', 5.5),
        ('Generate\nOutline', 4.5),
        ('Conduct\nResearch', 3.5)
    ]
    
    for i, (action, y) in enumerate(actions):
        action_box = FancyBboxPatch((1, y-0.3), 2, 0.6, boxstyle="round,pad=0.05",
                                    facecolor=colors['processing'], edgecolor='blue', linewidth=1)
        ax1.add_patch(action_box)
        ax1.text(2, y, action, ha='center', va='center', fontsize=10)
    
    # LLM Integration
    llm_box = FancyBboxPatch((7, 6), 2.5, 2, boxstyle="round,pad=0.1",
                             facecolor=colors['ai'], edgecolor='green', linewidth=3)
    ax1.add_patch(llm_box)
    ax1.text(8.25, 7, 'OpenAI GPT-4\nLanguage Model\n\n• Text Generation\n• Summarization\n• Analysis', 
             ha='center', va='center', fontweight='bold', fontsize=10)
    
    # External Services
    search_box = FancyBboxPatch((0.5, 6), 1.5, 0.8, boxstyle="round,pad=0.05",
                                facecolor='#FFE6CC', edgecolor='orange', linewidth=2)
    ax1.add_patch(search_box)
    ax1.text(1.25, 6.4, 'Google\nSearch API', ha='center', va='center', fontsize=9)
    
    web_box = FancyBboxPatch((0.5, 4.5), 1.5, 0.8, boxstyle="round,pad=0.05",
                             facecolor='#FFE6CC', edgecolor='orange', linewidth=2)
    ax1.add_patch(web_box)
    ax1.text(1.25, 4.9, 'Web Scraping\n(aiohttp)', ha='center', va='center', fontsize=9)
    
    # Output Processing
    pdf_box = FancyBboxPatch((4, 1.5), 2, 1, boxstyle="round,pad=0.1",
                             facecolor=colors['output'], edgecolor='red', linewidth=2)
    ax1.add_patch(pdf_box)
    ax1.text(5, 2, 'PDF Generation\n(WeasyPrint)', ha='center', va='center', fontweight='bold')
    
    # Storage
    storage_box = FancyBboxPatch((7.5, 1.5), 2, 1, boxstyle="round,pad=0.1",
                                 facecolor=colors['storage'], edgecolor='purple', linewidth=2)
    ax1.add_patch(storage_box)
    ax1.text(8.5, 2, 'File Storage\n(research_reports/)', ha='center', va='center', fontweight='bold')
    
    # Стрелки потока данных
    arrows = [
        ((2.5, 10.5), (4, 10.5)),      # Input -> API
        ((6, 10.5), (7.5, 10.5)),      # API -> Queue
        ((8.5, 10), (5, 9.5)),         # Queue -> Researcher
        ((5, 8), (2, 6.8)),            # Researcher -> Actions
        ((3, 6.5), (7, 7)),            # Actions -> LLM
        ((2, 6.2), (1.25, 6.8)),       # Actions -> Search
        ((2, 5.2), (1.25, 5.3)),       # Actions -> Web
        ((5, 8), (5, 2.5)),            # Researcher -> PDF
        ((6, 2), (7.5, 2)),            # PDF -> Storage
    ]
    
    for start, end in arrows:
        arrow = ConnectionPatch(start, end, "data", "data", 
                               arrowstyle="->", shrinkA=5, shrinkB=5, 
                               mutation_scale=20, fc="black", lw=2)
        ax1.add_patch(arrow)
    
    ax1.set_xticks([])
    ax1.set_yticks([])
    ax1.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['bottom'].set_visible(False)
    ax1.spines['left'].set_visible(False)
    
    # === СХЕМА 2: ВЗАИМОДЕЙСТВИЕ АГЕНТОВ ===
    ax2.set_xlim(0, 12)
    ax2.set_ylim(0, 10)
    ax2.set_title('Agent Interaction & Communication Flow', fontsize=16, fontweight='bold', pad=20)
    
    # Пользователь
    user_box = FancyBboxPatch((0.5, 8), 2, 1.5, boxstyle="round,pad=0.1",
                              facecolor='#E8F4FD', edgecolor='blue', linewidth=3)
    ax2.add_patch(user_box)
    ax2.text(1.5, 8.75, 'User\n(Streamlit UI)', ha='center', va='center', fontweight='bold')
    
    # API Orchestrator
    orchestrator_box = FancyBboxPatch((4.5, 8), 3, 1.5, boxstyle="round,pad=0.1",
                                      facecolor='#FFF2CC', edgecolor='orange', linewidth=3)
    ax2.add_patch(orchestrator_box)
    ax2.text(6, 8.75, 'API Orchestrator\n(FastAPI + Background Tasks)', ha='center', va='center', fontweight='bold')
    
    # Researcher Agent (центральный)
    main_agent_box = FancyBboxPatch((4.5, 5.5), 3, 2, boxstyle="round,pad=0.1",
                                    facecolor='#D5E8D4', edgecolor='green', linewidth=4)
    ax2.add_patch(main_agent_box)
    ax2.text(6, 6.5, 'Researcher Agent\n(Main Coordinator)\n\n• Manages workflow\n• Coordinates actions\n• Progress tracking', 
             ha='center', va='center', fontweight='bold', fontsize=11)
    
    # Action Agents
    action_agents = [
        ('Search Agent\n(CollectLinks)', 1, 3.5, '#FFE6CC'),
        ('Web Agent\n(WebBrowse)', 3.5, 3.5, '#FFE6CC'),
        ('Outline Agent\n(GenerateOutline)', 8.5, 3.5, '#FFE6CC'),
        ('Report Agent\n(ConductResearch)', 11, 3.5, '#FFE6CC')
    ]
    
    for name, x, y, color in action_agents:
        agent_box = FancyBboxPatch((x-0.75, y-0.5), 1.5, 1, boxstyle="round,pad=0.05",
                                   facecolor=color, edgecolor='orange', linewidth=2)
        ax2.add_patch(agent_box)
        ax2.text(x, y, name, ha='center', va='center', fontsize=9, fontweight='bold')
    
    # LLM Service
    llm_service_box = FancyBboxPatch((9, 6.5), 2.5, 2, boxstyle="round,pad=0.1",
                                     facecolor='#E1D5E7', edgecolor='purple', linewidth=3)
    ax2.add_patch(llm_service_box)
    ax2.text(10.25, 7.5, 'LLM Service\n(OpenAI Client)\n\n• Shared resource\n• Rate limiting\n• Error handling', 
             ha='center', va='center', fontweight='bold', fontsize=10)
    
    # External Services
    external_box = FancyBboxPatch((0.5, 1), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor='#F8CECC', edgecolor='red', linewidth=2)
    ax2.add_patch(external_box)
    ax2.text(2, 1.75, 'External Services\n• Google Search API\n• Web Scraping\n• PDF Generation', 
             ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Progress Tracking
    progress_box = FancyBboxPatch((8.5, 1), 3, 1.5, boxstyle="round,pad=0.1",
                                  facecolor='#E8F4FD', edgecolor='blue', linewidth=2)
    ax2.add_patch(progress_box)
    ax2.text(10, 1.75, 'Progress Tracking\n• Real-time status\n• Stage monitoring\n• Error reporting', 
             ha='center', va='center', fontweight='bold', fontsize=10)
    
    # Стрелки взаимодействия
    interaction_arrows = [
        # User interactions
        ((2.5, 8.75), (4.5, 8.75), 'HTTP Request'),
        ((4.5, 8.25), (2.5, 8.25), 'Response/Status'),
        
        # Orchestrator to Researcher
        ((6, 8), (6, 7.5), 'Task Assignment'),
        
        # Researcher to Actions
        ((5.25, 5.5), (1, 4), 'Search Query'),
        ((5.5, 5.5), (3.5, 4), 'URLs to Process'),
        ((6.5, 5.5), (8.5, 4), 'Generate Plan'),
        ((6.75, 5.5), (11, 4), 'Create Report'),
        
        # Actions to LLM
        ((1.75, 3.5), (9.5, 6.5), 'LLM Requests'),
        ((4.25, 3.5), (9.25, 6.5), ''),
        ((9.25, 3.5), (9.75, 6.5), ''),
        ((10.25, 3.5), (10, 6.5), ''),
        
        # External services
        ((1, 3), (2, 2.5), 'API Calls'),
        
        # Progress tracking
        ((7.5, 6), (8.5, 2.5), 'Progress Updates'),
    ]
    
    for i, arrow_data in enumerate(interaction_arrows):
        if len(arrow_data) == 3:
            start, end, label = arrow_data
            color = 'blue' if 'Request' in label or 'Assignment' in label else 'green'
        else:
            start, end = arrow_data
            label = ''
            color = 'gray'
        
        arrow = ConnectionPatch(start, end, "data", "data", 
                               arrowstyle="->", shrinkA=5, shrinkB=5, 
                               mutation_scale=15, fc=color, ec=color, lw=1.5)
        ax2.add_patch(arrow)
        
        if label and i < 4:  # Показываем подписи только для основных стрелок
            mid_x = (start[0] + end[0]) / 2
            mid_y = (start[1] + end[1]) / 2
            ax2.text(mid_x, mid_y + 0.2, label, ha='center', va='bottom', 
                    fontsize=8, bbox=dict(boxstyle="round,pad=0.3", facecolor='white', alpha=0.8))
    
    ax2.set_xticks([])
    ax2.set_yticks([])
    ax2.spines['top'].set_visible(False)
    ax2.spines['right'].set_visible(False)
    ax2.spines['bottom'].set_visible(False)
    ax2.spines['left'].set_visible(False)
    
    # Легенда
    legend_elements = [
        mpatches.Patch(color=colors['input'], label='Input/UI Components'),
        mpatches.Patch(color=colors['processing'], label='Processing/Orchestration'),
        mpatches.Patch(color=colors['ai'], label='AI/ML Components'),
        mpatches.Patch(color=colors['output'], label='Output Generation'),
        mpatches.Patch(color=colors['storage'], label='Storage/Queue'),
        mpatches.Patch(color='#FFE6CC', label='External Services')
    ]
    
    ax2.legend(handles=legend_elements, loc='upper right', bbox_to_anchor=(1, 1))
    
    plt.tight_layout()
    plt.savefig('researcher/ml_pipeline_architecture.png', dpi=300, bbox_inches='tight')
    plt.show()

def create_sequence_diagram():
    """Создает диаграмму последовательности взаимодействий"""
    
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.set_title('AI Researcher - Sequence Diagram', fontsize=16, fontweight='bold', pad=20)
    
    # Участники
    participants = [
        ('User', 1),
        ('Streamlit', 2.5),
        ('FastAPI', 4),
        ('Researcher', 5.5),
        ('Actions', 7),
        ('LLM', 8.5)
    ]
    
    # Рисуем участников
    for name, x in participants:
        rect = Rectangle((x-0.3, 14), 0.6, 0.8, facecolor='lightblue', edgecolor='black')
        ax.add_patch(rect)
        ax.text(x, 14.4, name, ha='center', va='center', fontweight='bold')
        
        # Линии жизни
        ax.plot([x, x], [14, 0.5], 'k--', alpha=0.5)
    
    # Сообщения (сверху вниз)
    messages = [
        (1, 2.5, 13, 'Enter topic'),
        (2.5, 4, 12.5, 'POST /research'),
        (4, 5.5, 12, 'create_task()'),
        (5.5, 7, 11.5, 'collect_links()'),
        (7, 8.5, 11, 'search_query()'),
        (8.5, 7, 10.5, 'search_results'),
        (7, 5.5, 10, 'links[]'),
        (5.5, 7, 9.5, 'browse_and_summarize()'),
        (7, 8.5, 9, 'summarize_content()'),
        (8.5, 7, 8.5, 'summaries'),
        (7, 5.5, 8, 'summaries[]'),
        (5.5, 7, 7.5, 'generate_outline()'),
        (7, 8.5, 7, 'create_structure()'),
        (8.5, 7, 6.5, 'outline'),
        (7, 5.5, 6, 'outline'),
        (5.5, 7, 5.5, 'conduct_research()'),
        (7, 8.5, 5, 'generate_report()'),
        (8.5, 7, 4.5, 'final_report'),
        (7, 5.5, 4, 'report + pdf'),
        (5.5, 4, 3.5, 'task_complete'),
        (4, 2.5, 3, 'GET /result'),
        (2.5, 1, 2.5, 'Display report + PDF')
    ]
    
    # Рисуем сообщения
    for x1, x2, y, text in messages:
        if x1 < x2:  # Стрелка вправо
            ax.annotate('', xy=(x2-0.1, y), xytext=(x1+0.1, y),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='blue'))
        else:  # Стрелка влево
            ax.annotate('', xy=(x2+0.1, y), xytext=(x1-0.1, y),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color='green'))
        
        # Подпись сообщения
        mid_x = (x1 + x2) / 2
        ax.text(mid_x, y + 0.1, text, ha='center', va='bottom', fontsize=9,
               bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Активные блоки (прямоугольники на линиях жизни)
    activations = [
        (2.5, 12.5, 2.5),  # Streamlit
        (4, 12.5, 3),      # FastAPI
        (5.5, 12, 4),      # Researcher
        (7, 11.5, 5.5),    # Actions
        (8.5, 11, 5)       # LLM
    ]
    
    for x, start_y, duration in activations:
        rect = Rectangle((x-0.05, start_y-duration), 0.1, duration, 
                        facecolor='yellow', alpha=0.7, edgecolor='black')
        ax.add_patch(rect)
    
    ax.set_xticks([])
    ax.set_yticks([])
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    plt.tight_layout()
    plt.savefig('researcher/sequence_diagram.png', dpi=300, bbox_inches='tight')
    plt.show()

if __name__ == "__main__":
    print("Создание схемы ML Pipeline и взаимодействия агентов...")
    create_ml_pipeline_diagram()
    print("Схема сохранена как 'ml_pipeline_architecture.png'")
    
    print("\nСоздание диаграммы последовательности...")
    create_sequence_diagram()
    print("Диаграмма сохранена как 'sequence_diagram.png'")
    
    print("\nГотово! Схемы созданы и сохранены.") 