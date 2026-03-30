import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template_string
from datetime import datetime, timedelta
import re

app = Flask(__name__)

def get_schedule_for_date(date_str):
    """
    Парсит расписание для заданной даты (формат DD.MM.YYYY)
    Возвращает список пар [{time, subject, room}]
    """
    # Здесь будет реальный парсинг после анализа сайта
    # Пока возвращаем демо-данные
    return [
        {"time": "08:30-10:00", "subject": "Программирование", "room": "216"},
        {"time": "10:15-11:45", "subject": "Базы данных", "room": "108"},
        {"time": "12:00-13:30", "subject": "Физика", "room": "301"}
    ]

@app.route('/')
def index():
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    today_str = today.strftime("%d.%m.%Y")
    tomorrow_str = tomorrow.strftime("%d.%m.%Y")
    
    today_schedule = get_schedule_for_date(today_str)
    tomorrow_schedule = get_schedule_for_date(tomorrow_str)
    
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
            
            .container {
                max-width: 750px;
                margin: 0 auto;
                display: flex;
                flex-direction: column;
                gap: 2rem;
            }
            
            .header {
                text-align: center;
                margin-bottom: 0.5rem;
            }
            
            .group {
                font-size: 2rem;
                font-weight: 800;
                background: linear-gradient(135deg, #e0aaff, #c77dff, #9d4edd);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
                text-shadow: 0 2px 10px rgba(160, 100, 255, 0.3);
            }
            
            .sub {
                font-size: 0.9rem;
                opacity: 0.8;
                margin-top: 0.25rem;
            }
            
            .day-card {
                background: rgba(25, 15, 45, 0.65);
                backdrop-filter: blur(12px);
                border-radius: 2rem;
                padding: 1.5rem;
                border: 1px solid rgba(200, 130, 255, 0.35);
                box-shadow: 0 20px 35px -15px rgba(0,0,0,0.5);
                transition: transform 0.2s ease;
            }
            
            .day-title {
                font-size: 1.6rem;
                font-weight: 600;
                margin-bottom: 0.25rem;
                display: flex;
                align-items: baseline;
                flex-wrap: wrap;
                gap: 0.75rem;
            }
            
            .day-name {
                background: linear-gradient(120deg, #d4a5ff, #b77eff);
                -webkit-background-clip: text;
                background-clip: text;
                color: transparent;
            }
            
            .date {
                font-size: 0.9rem;
                opacity: 0.7;
                font-weight: normal;
            }
            
            .pair-list {
                margin-top: 1.2rem;
                display: flex;
                flex-direction: column;
                gap: 0.8rem;
            }
            
            .pair {
                background: rgba(40, 28, 65, 0.8);
                backdrop-filter: blur(4px);
                border-radius: 1.5rem;
                padding: 1rem 1.2rem;
                display: flex;
                align-items: center;
                gap: 1rem;
                flex-wrap: wrap;
                border: 1px solid rgba(180, 110, 255, 0.5);
                box-shadow: 0 6px 12px rgba(0,0,0,0.2);
                transition: all 0.15s cubic-bezier(0.2, 1.2, 0.4, 1);
                cursor: default;
            }
            
            .pair:hover {
                transform: translateY(-3px) scale(1.01);
                background: rgba(70, 50, 100, 0.85);
                border-color: rgba(200, 140, 255, 0.8);
                box-shadow: 0 15px 25px -8px rgba(0,0,0,0.4);
            }
            
            .time {
                font-weight: 700;
                background: #4a3780;
                padding: 0.3rem 0.9rem;
                border-radius: 2rem;
                font-size: 0.85rem;
                color: #e9d5ff;
                min-width: 95px;
                text-align: center;
            }
            
            .subject {
                font-size: 1.05rem;
                font-weight: 500;
                flex: 1;
            }
            
            .room {
                font-size: 0.8rem;
                background: rgba(0,0,0,0.4);
                padding: 0.2rem 0.8rem;
                border-radius: 2rem;
                color: #cdb5ff;
            }
            
            .empty-message {
                text-align: center;
                padding: 2rem;
                background: rgba(0,0,0,0.25);
                border-radius: 1.5rem;
                font-style: italic;
            }
            
            footer {
                text-align: center;
                font-size: 0.7rem;
                opacity: 0.5;
                margin-top: 1rem;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <div class="group">СЭЗ-24-2</div>
                <div class="sub">подгруппа I • данные с raspisanie.doyupk.ru</div>
            </div>
            
            <div class="day-card">
                <div class="day-title">
                    <span class="day-name">Сегодня</span>
                    <span class="date">{{ today_date }}</span>
                </div>
                <div class="pair-list">
                    {% if today_schedule %}
                        {% for pair in today_schedule %}
                        <div class="pair">
                            <div class="time">{{ pair.time }}</div>
                            <div class="subject">{{ pair.subject }}</div>
                            <div class="room">{{ pair.room }}</div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-message">📭 Пар на сегодня нет</div>
                    {% endif %}
                </div>
            </div>
            
            <div class="day-card">
                <div class="day-title">
                    <span class="day-name">Завтра</span>
                    <span class="date">{{ tomorrow_date }}</span>
                </div>
                <div class="pair-list">
                    {% if tomorrow_schedule %}
                        {% for pair in tomorrow_schedule %}
                        <div class="pair">
                            <div class="time">{{ pair.time }}</div>
                            <div class="subject">{{ pair.subject }}</div>
                            <div class="room">{{ pair.room }}</div>
                        </div>
                        {% endfor %}
                    {% else %}
                        <div class="empty-message">📭 Пар на завтра нет</div>
                    {% endif %}
                </div>
            </div>
            <footer>обновляется автоматически • с физикой</footer>
        </div>
    </body>
    </html>
    '''
    
    return render_template_string(html, 
                                  today_schedule=today_schedule,
                                  tomorrow_schedule=tomorrow_schedule,
                                  today_date=today.strftime("%d.%m.%Y"),
                                  tomorrow_date=tomorrow.strftime("%d.%m.%Y"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
