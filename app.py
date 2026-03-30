import requests
from flask import Flask, render_template_string
from datetime import datetime, timedelta
import re

app = Flask(__name__)

def fetch_schedule():
    """Пробует получить расписание через API или прямой запрос"""
    try:
        # Пробуем получить страницу с группой (возможно, сайт использует GET-параметры)
        url = "https://raspisanie.doyupk.ru/"
        params = {
            "group": "СЭЗ-24-2",
            "date": datetime.now().strftime("%Y-%m-%d")
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.encoding = 'utf-8'
        
        # Ищем в ответе строки с расписанием
        text = response.text
        
        # Простой поиск пар по паттерну (время, предмет, кабинет)
        # Ищем строки типа "08:30" или "9:20" и рядом предмет
        schedule = {}
        
        # Разбиваем на строки
        lines = text.split('\n')
        current_date = None
        
        for line in lines:
            # Ищем дату
            date_match = re.search(r'(\d{2}\.\d{2}\.\d{4})', line)
            if date_match:
                current_date = date_match.group(1)
                schedule[current_date] = []
                continue
            
            # Ищем время и предмет
            if current_date and ('(I)' in line or 'подгруппа I' in line):
                time_match = re.search(r'\((\d{1,2}:\d{2})\)', line)
                subject_match = re.search(r'([А-Яа-яёЁ]+(?:[\s\-][А-Яа-яёЁ]+)*)\s*\(I\)', line)
                room_match = re.search(r'\(I\)\s*(\d+[А-Яа-я]?)', line)
                
                if subject_match:
                    subject = subject_match.group(1).strip()
                    room = room_match.group(1) if room_match else ""
                    time = time_match.group(1) if time_match else "—"
                    schedule[current_date].append({'time': time, 'subject': subject, 'room': room})
        
        return schedule if schedule else None
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

@app.route('/')
def index():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    today_str = today.strftime("%d.%m.%Y")
    tomorrow_str = tomorrow.strftime("%d.%m.%Y")
    
    schedule = fetch_schedule()
    
    if schedule:
        today_pairs = schedule.get(today_str, [])
        tomorrow_pairs = schedule.get(tomorrow_str, [])
        note = "✅ Расписание загружено с сайта колледжа"
    else:
        today_pairs = []
        tomorrow_pairs = []
        note = "⚠️ Не удалось загрузить расписание. Возможно, сайт изменил структуру."
    
    # HTML такой же, как в прошлый раз (красивый, с физикой)
    html = '''
    <!DOCTYPE html>
    <html lang="ru">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0, user-scalable=yes">
        <title>Расписание СЭЗ-24-2</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: 'Segoe UI', 'Inter', system-ui, sans-serif;
                background: linear-gradient(135deg, #1a0b2e 0%, #2a1a4a 40%, #3a2a6a 100%);
                background-attachment: fixed;
                min-height: 100vh;
                padding: 2rem 1.5rem;
                animation: breath 10s ease-in-out infinite;
                color: #f0eaff;
                overflow-y: auto;
            }
            @keyframes breath {
                0% { background-size: 100% 100%; background-position: 0% 0%; }
                50% { background-size: 150% 150%; background-position: 100% 50%; }
                100% { background-size: 100% 100%; background-position: 0% 0%; }
            }
            .container { max-width: 750px; margin: 0 auto; display: flex; flex-direction: column; gap: 2rem; }
            .header { text-align: center; margin-bottom: 0.5rem; }
            .group { font-size: 2rem; font-weight: 800; background: linear-gradient(135deg, #e0aaff, #c77dff, #9d4edd); -webkit-background-clip: text; background-clip: text; color: transparent; text-shadow: 0 2px 10px rgba(160, 100, 255, 0.3); }
            .sub { font-size: 0.9rem; opacity: 0.8; margin-top: 0.25rem; }
            .note-banner { background: rgba(255, 200, 100, 0.2); border-left: 4px solid #ffaa44; padding: 0.75rem; border-radius: 1rem; font-size: 0.8rem; text-align: center; margin-top: 0.5rem; }
            .day-card { background: rgba(25, 15, 45, 0.65); backdrop-filter: blur(12px); border-radius: 2rem; padding: 1.5rem; border: 1px solid rgba(200, 130, 255, 0.35); box-shadow: 0 20px 35px -15px rgba(0,0,0,0.5); transition: transform 0.2s ease; }
            .day-title { font-size: 1.6rem; font-weight: 600; margin-bottom: 0.25rem; display: flex; align-items: baseline; flex-wrap: wrap; gap: 0.75rem; }
            .day-name { background: linear-gradient(120deg, #d4a5ff, #b77eff); -webkit-background-clip: text; background-clip: text; color: transparent; }
            .date { font-size: 0.9rem; opacity: 0.7; font-weight: normal; }
            .pair-list { margin-top: 1.2rem; display: flex; flex-direction: column; gap: 0.8rem; }
            .pair { background: rgba(40, 28, 65, 0.8); backdrop-filter: blur(4px); border-radius: 1.5rem; padding: 1rem 1.2rem; display: flex; align-items: center; gap: 1rem; flex-wrap: wrap; border: 1px solid rgba(180, 110, 255, 0.5); box-shadow: 0 6px 12px rgba(0,0,0,0.2); transition: all 0.15s cubic-bezier(0.2, 1.2, 0.4, 1); cursor: default; }
            .pair:hover { transform: translateY(-3px) scale(1.01); background: rgba(70, 50, 100, 0.85); border-color: rgba(200, 140, 255, 0.8); box-shadow: 0 15px 25px -8px rgba(0,0,0,0.4); }
            .time { font-weight: 700; background: #4a3780; padding: 0.3rem 0.9rem; border-radius: 2rem; font-size: 0.85rem; color: #e9d5ff; min-width: 70px; text-align: center; }
            .subject { font-size: 1.05rem; font-weight: 500; flex: 1; }
            .room { font-size: 0.8rem; background: rgba(0,0,0,0.4); padding: 0.2rem 0.8rem; border-radius: 2rem; color: #cdb5ff; }
            .empty-message { text-align: center; padding: 2rem; background: rgba(0,0,0,0.25); border-radius: 1.5rem; font-style: italic; }
            footer { text-align: center; font-size: 0.7rem; opacity: 0.5; margin-top: 1rem; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="group">СЭЗ-24-2</div>
                <div class="sub">подгруппа I</div>
                <div class="note-banner">{{ note }}</div>
            </div>
            <div class="day-card">
                <div class="day-title"><span class="day-name">Сегодня</span><span class="date">{{ today_date }}</span></div>
                <div class="pair-list">
                    {% for pair in today_pairs %}
                    <div class="pair"><div class="time">{{ pair.time }}</div><div class="subject">{{ pair.subject }}</div><div class="room">{{ pair.room }}</div></div>
                    {% else %}
                    <div class="empty-message">📭 Пар на сегодня нет</div>
                    {% endfor %}
                </div>
            </div>
            <div class="day-card">
                <div class="day-title"><span class="day-name">Завтра</span><span class="date">{{ tomorrow_date }}</span></div>
                <div class="pair-list">
                    {% for pair in tomorrow_pairs %}
                    <div class="pair"><div class="time">{{ pair.time }}</div><div class="subject">{{ pair.subject }}</div><div class="room">{{ pair.room }}</div></div>
                    {% else %}
                    <div class="empty-message">📭 Пар на завтра нет</div>
                    {% endfor %}
                </div>
            </div>
            <footer>обновляется автоматически • с физикой</footer>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, 
                                  today_pairs=today_pairs,
                                  tomorrow_pairs=tomorrow_pairs,
                                  today_date=today_str,
                                  tomorrow_date=tomorrow_str,
                                  note=note)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
