from flask import Flask, render_template_string, request
import sqlite3

app = Flask(__name__)

# [기능] 천단위 콤마 찍어주는 필터
@app.template_filter('comma')
def comma_filter(value):
    try:
        return "{:,}".format(value)
    except:
        return value

def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row 
    return conn

@app.route('/')
def index():
    query = request.args.get('q', '') 
    sort_by = request.args.get('sort', 'name')  # name, price_low, price_high
    conn = get_db_connection()
    
    if query:
        search_term = f'%{query}%'
        # 띄어쓰기 제거한 검색어도 준비
        search_term_no_space = f'%{query.replace(" ", "")}%'
        # 미용실 이름, 위치, 그리고 메뉴 이름으로 검색 (띄어쓰기 무시)
        if sort_by == 'price_low':
            # 최저가 기준 오름차순
            salons = conn.execute('''
                SELECT DISTINCT s.*, MIN(m.price) as min_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE s.name LIKE ? 
                   OR s.location LIKE ? 
                   OR m.service_name LIKE ?
                   OR REPLACE(s.name, ' ', '') LIKE ?
                   OR REPLACE(s.location, ' ', '') LIKE ?
                   OR REPLACE(m.service_name, ' ', '') LIKE ?
                GROUP BY s.id
                ORDER BY min_price ASC, s.name
            ''', (search_term, search_term, search_term, search_term_no_space, search_term_no_space, search_term_no_space)).fetchall()
        elif sort_by == 'price_high':
            # 최고가 기준 내림차순
            salons = conn.execute('''
                SELECT DISTINCT s.*, MAX(m.price) as max_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE s.name LIKE ? 
                   OR s.location LIKE ? 
                   OR m.service_name LIKE ?
                   OR REPLACE(s.name, ' ', '') LIKE ?
                   OR REPLACE(s.location, ' ', '') LIKE ?
                   OR REPLACE(m.service_name, ' ', '') LIKE ?
                GROUP BY s.id
                ORDER BY max_price DESC, s.name
            ''', (search_term, search_term, search_term, search_term_no_space, search_term_no_space, search_term_no_space)).fetchall()
        else:
            # 이름순
            salons = conn.execute('''
                SELECT DISTINCT s.* FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE s.name LIKE ? 
                   OR s.location LIKE ? 
                   OR m.service_name LIKE ?
                   OR REPLACE(s.name, ' ', '') LIKE ?
                   OR REPLACE(s.location, ' ', '') LIKE ?
                   OR REPLACE(m.service_name, ' ', '') LIKE ?
                ORDER BY s.name
            ''', (search_term, search_term, search_term, search_term_no_space, search_term_no_space, search_term_no_space)).fetchall()
    else:
        if sort_by == 'price_low':
            # 최저가 기준 오름차순
            salons = conn.execute('''
                SELECT s.*, MIN(m.price) as min_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                GROUP BY s.id
                ORDER BY min_price ASC, s.name
            ''').fetchall()
        elif sort_by == 'price_high':
            # 최고가 기준 내림차순
            salons = conn.execute('''
                SELECT s.*, MAX(m.price) as max_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                GROUP BY s.id
                ORDER BY max_price DESC, s.name
            ''').fetchall()
        else:
            # 이름순
            salons = conn.execute('SELECT * FROM salons ORDER BY name').fetchall()
    
    conn.close()

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
            .sort-options { margin-top: 15px; display: flex; justify-content: center; gap: 10px; }
            .sort-options a { padding: 8px 15px; text-decoration: none; border-radius: 5px; font-size: 0.9em; }
            .sort-options a.active { background-color: #3498db; color: white; }
            .sort-options a:not(.active) { background-color: #ecf0f1; color: #34495e; }
            .sort-options a:not(.active):hover { background-color: #bdc3c7; }
            .card { border: 1px solid #eee; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); }
            .salon-name { font-size: 1.5em; font-weight: bold; color: #333; }
            .location { color: #7f8c8d; font-size: 0.9em; margin-bottom: 15px; margin-top: 5px; }
            .menu-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .menu-table td { border-bottom: 1px solid #f0f0f0; padding: 8px 0; }
            .price { text-align: right; font-weight: bold; color: #e74c3c; }
            .reservation-section { margin-top: 15px; text-align: center; }
            .reservation-btn { padding: 10px 20px; background-color: #27ae60; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; }
            .reservation-btn:hover { background-color: #229954; }
            .phone-display { margin-top: 10px; padding: 10px; background-color: #ecf0f1; border-radius: 5px; font-size: 1.1em; font-weight: bold; color: #2c3e50; display: none; }
            .phone-display.show { display: block; }
        </style>
    </head>
    <body>
        <h1>✂️ 인천대 헤어샵 모음</h1>
        
        <div class="search-box">
            <form action="">
                <input type="text" name="q" placeholder="미용실 이름, 위치, 메뉴 검색 (예: 남성커트, 여성커트)..." value="{{ request.args.get('q', '') }}">
                <input type="hidden" name="sort" value="{{ request.args.get('sort', 'name') }}">
                <button type="submit">검색</button>
            </form>
            <div class="sort-options">
                {% set current_sort = request.args.get('sort', 'name') %}
                <a href="?q={{ request.args.get('q', '') }}&sort=name" class="{{ 'active' if current_sort == 'name' else '' }}">이름순</a>
                <a href="?q={{ request.args.get('q', '') }}&sort=price_low" class="{{ 'active' if current_sort == 'price_low' else '' }}">가격 낮은순</a>
                <a href="?q={{ request.args.get('q', '') }}&sort=price_high" class="{{ 'active' if current_sort == 'price_high' else '' }}">가격 높은순</a>
            </div>
            {% if request.args.get('q') %}
            <div style="margin-top:10px;"><a href="/">전체 목록 보기</a></div>
            {% endif %}
        </div>

        {% if not salons %}
            <p style="text-align:center;">검색 결과가 없습니다.</p>
        {% endif %}

        {% for salon in salons %}
        <div class="card">
            <div class="salon-name">{{ salon['name'] }}</div>
            <div class="location">📍 {{ salon['location'] }}</div>
            
            {% set conn = get_db_connection() %}
            {% set menus = conn.execute('SELECT * FROM menus WHERE salon_id = ?', (salon['id'],)).fetchall() %}
            
            <table class="menu-table">
                {% for menu in menus %}
                <tr>
                    <td>{{ menu['service_name'] }}</td>
                    <td class="price">{{ menu['price'] | comma }}원</td>
                </tr>
                {% endfor %}
            </table>
            {% if salon['phone'] %}
            <div class="reservation-section">
                <button class="reservation-btn" onclick="togglePhone({{ salon['id'] }})">📞 예약하기</button>
                <div id="phone-{{ salon['id'] }}" class="phone-display">
                    전화번호: <a href="tel:{{ salon['phone'] }}" style="color: #3498db; text-decoration: none;">{{ salon['phone'] }}</a>
                </div>
            </div>
            {% endif %}
            {% set _ = conn.close() %}
        </div>
        {% endfor %}
        
        <script>
            function togglePhone(salonId) {
                const phoneDisplay = document.getElementById('phone-' + salonId);
                phoneDisplay.classList.toggle('show');
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, salons=salons, get_db_connection=get_db_connection, request=request)

if __name__ == '__main__':
    app.run(debug=True, port=5001)