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

def prepare_location(address, limit=35):
    if not address:
        return '', '', False
    address = address.strip()
    if len(address) <= limit:
        return address, address, False
    short = address[:limit].rstrip() + '...'
    return short, address, True

@app.route('/')
def index():
    query = request.args.get('q', '') 
    sort_by = request.args.get('sort', 'name')  # name, price_low_서비스명, price_high_서비스명
    service_type = request.args.get('service', '')  # 남성커트, 여성커트, 펌, 염색
    conn = get_db_connection()
    
    if query:
        search_term = f'%{query}%'
        # 띄어쓰기 제거한 검색어도 준비
        search_term_no_space = f'%{query.replace(" ", "")}%'
        # 미용실 이름, 위치, 그리고 메뉴 이름으로 검색 (띄어쓰기 무시)
        if sort_by.startswith('price_low') and service_type:
            # 특정 서비스 가격 낮은순
            salons = conn.execute('''
                SELECT DISTINCT s.*, m.price as service_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE (s.name LIKE ? 
                   OR s.location LIKE ? 
                   OR m.service_name LIKE ?
                   OR REPLACE(s.name, ' ', '') LIKE ?
                   OR REPLACE(s.location, ' ', '') LIKE ?
                   OR REPLACE(m.service_name, ' ', '') LIKE ?)
                   AND (m.service_name = ? OR REPLACE(m.service_name, ' ', '') = ?)
                ORDER BY m.price ASC, s.name
            ''', (search_term, search_term, search_term, search_term_no_space, search_term_no_space, search_term_no_space, service_type, service_type.replace(' ', ''))).fetchall()
        elif sort_by.startswith('price_high') and service_type:
            # 특정 서비스 가격 높은순
            salons = conn.execute('''
                SELECT DISTINCT s.*, m.price as service_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE (s.name LIKE ? 
                   OR s.location LIKE ? 
                   OR m.service_name LIKE ?
                   OR REPLACE(s.name, ' ', '') LIKE ?
                   OR REPLACE(s.location, ' ', '') LIKE ?
                   OR REPLACE(m.service_name, ' ', '') LIKE ?)
                   AND (m.service_name = ? OR REPLACE(m.service_name, ' ', '') = ?)
                ORDER BY m.price DESC, s.name
            ''', (search_term, search_term, search_term, search_term_no_space, search_term_no_space, search_term_no_space, service_type, service_type.replace(' ', ''))).fetchall()
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
        if sort_by.startswith('price_low') and service_type:
            # 특정 서비스 가격 낮은순
            salons = conn.execute('''
                SELECT s.*, m.price as service_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE m.service_name = ? OR REPLACE(m.service_name, ' ', '') = ?
                ORDER BY m.price ASC, s.name
            ''', (service_type, service_type.replace(' ', ''))).fetchall()
        elif sort_by.startswith('price_high') and service_type:
            # 특정 서비스 가격 높은순
            salons = conn.execute('''
                SELECT s.*, m.price as service_price FROM salons s
                LEFT JOIN menus m ON s.id = m.salon_id
                WHERE m.service_name = ? OR REPLACE(m.service_name, ' ', '') = ?
                ORDER BY m.price DESC, s.name
            ''', (service_type, service_type.replace(' ', ''))).fetchall()
        else:
            # 이름순
            salons = conn.execute('SELECT * FROM salons ORDER BY name').fetchall()
    
    conn.close()
    salons = [dict(s) for s in salons]
    for salon in salons:
        short_loc, full_loc, is_truncated = prepare_location(salon.get('location', ''))
        salon['display_location'] = short_loc
        salon['full_location'] = full_loc
        salon['is_location_truncated'] = is_truncated

    html = """
    <!doctype html>
    <html>
    <head>
        <title>인천대 미용실 찾기</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
            h1 { text-align: center; color: #FF6B9D; font-size: 1.8em; margin-bottom: 30px; font-weight: 600; }
            .search-box { text-align: center; margin-bottom: 30px; }
            .search-wrapper { position: relative; display: inline-block; width: 70%; max-width: 600px; }
            .search-wrapper::before { content: '🔍'; position: absolute; left: 15px; top: 50%; transform: translateY(-50%); font-size: 1.2em; z-index: 1; }
            input[type="text"] { padding: 12px 15px 12px 45px; width: 100%; border: 2px solid #e0e0e0; border-radius: 25px; font-size: 1em; }
            input[type="text"]:focus { outline: none; border-color: #FF6B9D; box-shadow: 0 0 0 3px rgba(255, 107, 157, 0.1); }
            button[type="submit"] { padding: 12px 30px; background-color: #FF6B9D; color: white; border: none; border-radius: 25px; cursor: pointer; font-size: 1em; font-weight: 600; margin-top: 15px; box-shadow: 0 4px 15px rgba(255, 107, 157, 0.3); }
            .sort-options { margin-top: 20px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }
            .sort-options a { padding: 10px 20px; text-decoration: none; border-radius: 20px; font-size: 0.9em; font-weight: 500; }
            .sort-options a.active { background-color: #FF6B9D; color: white; box-shadow: 0 2px 10px rgba(255, 107, 157, 0.3); }
            .sort-options a:not(.active) { background-color: white; color: #666; border: 2px solid #e0e0e0; }
            .salons-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
            .card { background: white; border: none; border-radius: 15px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); position: relative; }
            .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; position: relative; }
            .salon-name { font-size: 1.3em; font-weight: 600; color: #333; flex: 1; line-height: 1.4; }
            .reservation-btn { padding: 8px 12px; background-color: #FF6B9D; color: white; border: none; border-radius: 20px; cursor: pointer; font-size: 1.2em; box-shadow: 0 2px 8px rgba(255, 107, 157, 0.3); position: relative; }
            .location { color: #888; font-size: 0.9em; margin-bottom: 15px; display: flex; align-items: center; gap: 5px; cursor: pointer; }
            .location.collapsed { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .location.expanded { white-space: normal; }
            .location::before { content: '📍'; font-size: 1.1em; }
            .menu-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .menu-table td { border-bottom: 1px solid #f0f0f0; padding: 10px 0; }
            .menu-table tr:last-child td { border-bottom: none; }
            .price { text-align: right; font-weight: 600; color: #FF6B9D; font-size: 1.05em; }
            .modal { display: none; position: absolute; z-index: 1000; }
            .modal.show { display: block; }
            .modal-content { background-color: white; padding: 10px; border-radius: 10px; text-align: center; min-width: 200px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); position: relative; top: 5px; right: 0; }
            .modal-content .phone-number { font-size: 0.9em; font-weight: bold; color: #444; margin: 8px 0; }
            .modal-content .phone-link { display: inline-block; padding: 6px 12px; background-color: #FF6B9D; color: white; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 0.85em; box-shadow: 0 2px 8px rgba(255, 107, 157, 0.3); }
            .reservation-btn { position: relative; }
            .reservation-btn .modal { left: auto; right: 0; top: 100%; margin-top: 5px; }
            .service-options { display: flex; flex-direction: row; gap: 8px; }
            .service-btn { padding: 8px 12px; background-color: white; color: #666; border: 2px solid #e0e0e0; border-radius: 8px; cursor: pointer; font-size: 0.85em; font-weight: 500; }
            .sort-options { position: relative; }
            .sort-options a { position: relative; display: inline-block; }
            .sort-options .modal { left: 0; top: 100%; margin-top: 5px; white-space: nowrap; }
            .modal-content { padding: 10px; }
            @media (max-width: 768px) {
                .salons-grid { grid-template-columns: 1fr; }
                .search-wrapper { width: 100%; }
            }
        </style>
    </head>
    <body>
        <h1>✂️ 인천대 헤어샵 모음</h1>
        
        <div class="search-box">
            <form action="">
                <div class="search-wrapper">
                    <input type="text" name="q" placeholder="미용실 이름, 위치, 메뉴 검색 (예: 남성커트, 여성커트)..." value="{{ request.args.get('q', '') }}">
                </div>
                <input type="hidden" name="sort" value="{{ request.args.get('sort', 'name') }}">
                <button type="submit">검색</button>
            </form>
            <div class="sort-options" style="position: relative;">
                {% set current_sort = request.args.get('sort', 'name') %}
                {% set is_price_low = 'price_low' in current_sort %}
                {% set is_price_high = 'price_high' in current_sort %}
                <a href="?q={{ request.args.get('q', '') }}&sort=name" class="{{ 'active' if current_sort == 'name' else '' }}">이름순</a>
                <a href="#" onclick="showServiceModal(event, 'price_low'); return false;" class="{{ 'active' if is_price_low else '' }}">가격 낮은순
                    <div id="serviceModal-price_low" class="modal">
                        <div class="modal-content">
                            <div class="service-options">
                                <button class="service-btn" onclick="selectService('남성 커트')">남성 커트</button>
                                <button class="service-btn" onclick="selectService('여성 커트')">여성 커트</button>
                                <button class="service-btn" onclick="selectService('펌')">펌</button>
                                <button class="service-btn" onclick="selectService('염색')">염색</button>
                            </div>
                        </div>
                    </div>
                </a>
                <a href="#" onclick="showServiceModal(event, 'price_high'); return false;" class="{{ 'active' if is_price_high else '' }}">가격 높은순
                    <div id="serviceModal-price_high" class="modal">
                        <div class="modal-content">
                            <div class="service-options">
                                <button class="service-btn" onclick="selectService('남성 커트')">남성 커트</button>
                                <button class="service-btn" onclick="selectService('여성 커트')">여성 커트</button>
                                <button class="service-btn" onclick="selectService('펌')">펌</button>
                                <button class="service-btn" onclick="selectService('염색')">염색</button>
                            </div>
                        </div>
                    </div>
                </a>
            </div>
        </div>

        {% if not salons %}
            <p style="text-align:center;">검색 결과가 없습니다.</p>
        {% else %}
        <div class="salons-grid">
            {% for salon in salons %}
            <div class="card">
                <div class="card-header">
                    <div class="salon-name">{{ salon['name'] }}</div>
                    {% if salon['phone'] %}
                    <button class="reservation-btn" onclick="showPhoneModal(event, '{{ salon['phone'] }}', {{ salon['id'] }})">📞
                        <div id="phoneModal-{{ salon['id'] }}" class="modal">
                            <div class="modal-content">
                                <div class="phone-number" id="modalPhoneNumber-{{ salon['id'] }}"></div>
                                <a href="#" id="modalPhoneLink-{{ salon['id'] }}" class="phone-link">전화 걸기</a>
                            </div>
                        </div>
                    </button>
                    {% endif %}
                </div>
                <div class="location {% if salon['is_location_truncated'] %}collapsed{% endif %}"
                     data-full="{{ salon['full_location'] }}"
                     data-short="{{ salon['display_location'] }}"
                     data-is-long="{{ 'true' if salon['is_location_truncated'] else 'false' }}"
                     onclick="toggleLocation(this)">
                    📍 <span class="location-text">{{ salon['display_location'] if salon['is_location_truncated'] else salon['full_location'] }}</span>
                </div>
                
                {% set conn = get_db_connection() %}
                {% set service_filter = service_type if sort_by.startswith('price_') else '' %}
                {% if service_filter %}
                    {% set menus = conn.execute('SELECT * FROM menus WHERE salon_id = ? AND (service_name = ? OR REPLACE(service_name, " ", "") = ?)', (salon['id'], service_filter, service_filter.replace(" ", ""))).fetchall() %}
                {% else %}
                    {% set menus = conn.execute('SELECT * FROM menus WHERE salon_id = ?', (salon['id'],)).fetchall() %}
                {% endif %}
                <table class="menu-table">
                    {% for menu in menus %}
                    <tr>
                        <td>{{ menu['service_name'] }}</td>
                        <td class="price">{{ menu['price'] | comma }}원</td>
                    </tr>
                    {% endfor %}
                </table>
                {% set _ = conn.close() %}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <script>
            let currentSortType = '';
            
            function showPhoneModal(event, phoneNumber, salonId) {
                event.stopPropagation();
                // 다른 모달 닫기
                document.querySelectorAll('.modal').forEach(m => {
                    if (m.id !== 'phoneModal-' + salonId && !m.id.startsWith('serviceModal-')) {
                        m.classList.remove('show');
                    }
                });
                const modal = document.getElementById('phoneModal-' + salonId);
                document.getElementById('modalPhoneNumber-' + salonId).textContent = phoneNumber;
                document.getElementById('modalPhoneLink-' + salonId).href = 'tel:' + phoneNumber;
                modal.classList.add('show');
            }
            
            function showServiceModal(event, sortType) {
                event.stopPropagation();
                currentSortType = sortType;
                // 다른 모달 닫기
                document.querySelectorAll('.modal').forEach(m => {
                    if (m.id !== 'serviceModal-' + sortType) {
                        m.classList.remove('show');
                    }
                });
                const modal = document.getElementById('serviceModal-' + sortType);
                modal.classList.add('show');
            }
            
            function selectService(serviceName) {
                const query = '{{ request.args.get("q", "") }}';
                const url = '?q=' + encodeURIComponent(query) + '&sort=' + currentSortType + '&service=' + encodeURIComponent(serviceName);
                window.location.href = url;
            }

            function toggleLocation(element) {
                if (element.dataset.isLong !== 'true') return;
                const textEl = element.querySelector('.location-text');
                const isExpanded = element.classList.toggle('expanded');
                element.classList.toggle('collapsed', !isExpanded);
                textEl.textContent = isExpanded ? element.dataset.full : element.dataset.short;
            }
            
            // 모달 외부 클릭 시 닫기
            document.addEventListener('click', function(event) {
                if (!event.target.closest('.modal') && !event.target.closest('.reservation-btn') && !event.target.closest('.sort-options a') && !event.target.closest('.service-btn')) {
                    document.querySelectorAll('.modal').forEach(m => m.classList.remove('show'));
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(
        html,
        salons=salons,
        get_db_connection=get_db_connection,
        request=request,
        sort_by=sort_by,
        service_type=service_type
    )

if __name__ == '__main__':
    app.run(debug=True, port=5001)