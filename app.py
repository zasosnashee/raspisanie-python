import asyncio
from flask import Flask
from pyppeteer import launch

app = Flask(__name__)

async def debug_page():
    browser = None
    try:
        browser = await launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = await browser.newPage()
        
        await page.goto('https://raspisanie.doyupk.ru/', {'waitUntil': 'networkidle2', 'timeout': 30000})
        
        # Выбираем группу
        await page.waitForSelector('input[value="group"]', {'timeout': 5000})
        await page.click('input[value="group"]')
        
        await page.waitForSelector('input[placeholder="Поиск группы"]', {'timeout': 5000})
        await page.type('input[placeholder="Поиск группы"]', 'СЭЗ-24-2')
        
        await page.waitForTimeout(1500)
        await page.click('.ui-menu-item')
        
        await page.waitForTimeout(4000)
        
        # Получаем текст
        page_text = await page.evaluate('document.body.innerText')
        
        print("=" * 50)
        print("ТЕКСТ СТРАНИЦЫ:")
        print("=" * 50)
        print(page_text)
        print("=" * 50)
        
        return page_text
        
    except Exception as e:
        print(f"Ошибка: {e}")
        return None
    finally:
        if browser:
            await browser.close()

@app.route('/')
def index():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    text = loop.run_until_complete(debug_page())
    
    if text:
        return f"<pre>Текст получен. Смотри логи Render.</pre>"
    else:
        return "Ошибка загрузки"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
