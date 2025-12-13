from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)

# 천단위 콤마 추가 필터
@app.template_filter('comma')
def comma_filter(value):
    try:
        return "{:,}".format(value)
    except:
        return value

# 데이터베이스에 접속하는 배달 기사 함수
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row # 데이터를 딕셔너리처럼 다루기 위해 설정
    return conn

@app.route('/')
def index():
    query = request.args.get('q', '') # 검색어 가져오기
    conn = get_db_connection()
    
    # 1. 미용실 목록 가져오기 (검색어가 있으면 필터링)
    if query:
        search_term = f'%{query}%'
        salons = conn.execute('SELECT * FROM salons WHERE name LIKE ? OR location LIKE ?', 
                              (search_term, search_term)).fetchall()
    else:
        salons = conn.execute('SELECT * FROM salons').fetchall()
    
    conn.close()

    # 화면 디자인 (HTML)
    html = """
    <!doctype html>
    <html>
    <head>
        <title>인천대 미용실 찾기</title>
        <style>
            body { font-family: 'Apple SD Gothic Neo', sans-serif; max-width: 600px; margin: 0 auto; padding: 20px; }
            h1 { text-align: center; color: #2c3e50; }
            .search-box { text-align: center; margin-bottom: 30px; }
            input[type="text"] { padding: 10px; width: 70%; border: 1px solid #ddd; border-radius: 5px; }
            button { padding: 10px 20px; background-color: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer; }
            .card { border: 1px solid #eee; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            .salon-name { font-size: 1.5em; font-weight: bold; }
            .rating { color: #f1c40f; }
            .location { color: #7f8c8d; font-size: 0.9em; margin-bottom: 15px; }
            .menu-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            .menu-table td { border-bottom: 1px solid #f0f0f0; padding: 8px 0; }
            .price { text-align: right; font-weight: bold; }
        </style>
    </head>
    <body>
        <h1>✂️ 인천대 헤어샵 모음</h1>
        
        <div class="search-box">
            <form action="">
                <input type="text" name="q" placeholder="미용실 이름이나 위치 검색..." value="{{ request.args.get('q', '') }}">
                <button type="submit">검색</button>
            </form>
            {% if request.args.get('q') %}
            <div style="margin-top:10px;"><a href="/">전체 목록 보기</a></div>
            {% endif %}
        </div>

        {% if not salons %}
            <p style="text-align:center;">검색 결과가 없습니다.</p>
        {% endif %}

        {% for salon in salons %}
        <div class="card">
            <div class="salon-name">
                {{ salon['name'] }} 
                <span class="rating">★ {{ salon['rating'] }}</span>
            </div>
            <div class="location">📍 {{ salon['location'] }}</div>
            
            {% set conn = get_db_connection() %}
            {% set menus = conn.execute('SELECT * FROM menus WHERE salon_id = ?', (salon['id'],)).fetchall() %}
            
            <table class="menu-table">
                {% for menu in menus %}
                <tr>
                    <td>{{ menu['service_name'] }}</td>
                    <td class="price">{{ menu['price'] }}원</td>
                </tr>
                {% endfor %}
            </table>
            {% set _ = conn.close() %}
        </div>
        {% endfor %}
    </body>
    </html>
    """
    return render_template_string(html, salons=salons, get_db_connection=get_db_connection, request=request)

if __name__ == '__main__':
    app.run(debug=True, port=5001)