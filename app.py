from flask import Flask, render_template_string, request, redirect, url_for, jsonify
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
    # 찜 테이블이 없으면 생성
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            salon_id INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (salon_id) REFERENCES salons (id),
            UNIQUE(salon_id)
        )
    ''')
    conn.commit()
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
    show_favorites = request.args.get('favorites', '') == 'true'
    # 찜한 미용실 필터가 활성화되면 항상 이름순으로 정렬
    if show_favorites:
        sort_by = 'name'
        service_type = ''
    else:
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
    
    # 찜한 미용실 필터링
    if show_favorites:
        conn = get_db_connection()
        favorite_ids = [row['salon_id'] for row in conn.execute('SELECT salon_id FROM favorites').fetchall()]
        conn.close()
        salons = [s for s in salons if s['id'] in favorite_ids]
    
    conn.close()
    salons = [dict(s) for s in salons]
    
    # 각 미용실의 위치 정보 처리 및 찜 상태 확인
    conn = get_db_connection()
    favorite_ids = set([row['salon_id'] for row in conn.execute('SELECT salon_id FROM favorites').fetchall()])
    for salon in salons:
        short_loc, full_loc, is_truncated = prepare_location(salon.get('location', ''))
        salon['display_location'] = short_loc
        salon['full_location'] = full_loc
        salon['is_location_truncated'] = is_truncated
        salon['is_favorite'] = salon['id'] in favorite_ids
    conn.close()

    html = """
    <!doctype html>
    <html>
    <head>
        <title>The Cut : INU</title>
        <link rel="icon" type="image/jpeg" href="{{ url_for('static', filename='images/icon.jpg') }}">
        <style>
            @font-face {
                font-family: 'Cafe24Classictype';
                src: url('{{ url_for("static", filename="fonts/Cafe24Classictype-v1.1.ttf") }}') format('truetype');
                font-weight: normal;
                font-style: normal;
            }
            * { box-sizing: border-box; }
            body { font-family: 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 1200px; margin: 0 auto; padding: 0; background-color: #f8f9fa; }
            .cover-image-container { width: 100%; max-width: 1200px; margin: 0 auto; position: relative; }
            .cover-image { width: 100%; height: auto; display: block; object-fit: cover; }
            h1 { font-family: 'Cafe24Classictype', 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-align: center; color: #f0b0b0; font-size: 1.8em; margin: 30px 20px; font-weight: 600; }
            .content-wrapper { padding: 0 20px 20px 20px; }
            .search-box { text-align: center; margin-bottom: 30px; }
            .search-wrapper { position: relative; display: inline-block; width: 70%; max-width: 600px; }
            .search-wrapper::before { content: '🔍'; position: absolute; left: 15px; top: 50%; transform: translateY(-50%); font-size: 1.2em; z-index: 1; }
            input[type="text"] { padding: 12px 15px 12px 45px; width: 100%; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 1em; }
            input[type="text"]:focus { outline: none; border-color: #f0b0b0; box-shadow: 0 0 0 3px rgba(240, 176, 176, 0.1); }
            button[type="submit"] { padding: 12px 20px; background-color: #f0b0b0; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9em; font-weight: 600; margin-top: 15px; box-shadow: 0 4px 15px rgba(240, 176, 176, 0.3); }
            .sort-wrapper { margin-top: 20px; display: flex; justify-content: space-between; align-items: center; gap: 10px; flex-wrap: wrap; }
            .sort-options { display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; flex: 1; }
            .add-salon-btn { padding: 10px 20px; background-color: #f0b0b0; color: white; text-decoration: none; border-radius: 5px; font-weight: 600; box-shadow: 0 2px 8px rgba(240, 176, 176, 0.3); white-space: nowrap; cursor: pointer; border: none; }
            .add-salon-modal { display: none; position: fixed; z-index: 2000; left: 0; top: 0; width: 100%; height: 100%; background-color: rgba(0,0,0,0.5); }
            .add-salon-modal.show { display: flex; align-items: center; justify-content: center; }
            .add-salon-modal-content { background-color: white; padding: 30px; border-radius: 10px; max-width: 600px; width: 90%; max-height: 90vh; overflow-y: auto; box-shadow: 0 4px 20px rgba(0,0,0,0.3); position: relative; }
            .add-salon-modal h2 { font-family: 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin-top: 0; margin-bottom: 20px; color: #333; text-align: center; }
            .add-salon-form-group { margin-bottom: 20px; }
            .add-salon-form-group label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
            .add-salon-form-group input[type="text"], .add-salon-form-group input[type="tel"] { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 1em; }
            .add-salon-menu-item input[type="text"] { padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 1em; }
            .add-salon-menu-item input[type="text"]:focus { outline: none; border-color: #f0b0b0; box-shadow: 0 0 0 3px rgba(240, 176, 176, 0.1); }
            .add-salon-form-group input:focus { outline: none; border-color: #f0b0b0; box-shadow: 0 0 0 3px rgba(240, 176, 176, 0.1); }
            .add-salon-menu-item { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
            .add-salon-menu-item input[type="text"] { flex: 1; }
            .add-salon-remove-btn { padding: 8px 15px; background-color: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9em; }
            .add-salon-remove-btn:hover { background-color: #c82333; }
            .add-salon-add-menu-btn { padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9em; margin-bottom: 20px; }
            .add-salon-add-menu-btn:hover { background-color: #5a6268; }
            .add-salon-submit-btn { padding: 12px 30px; background-color: #f0b0b0; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; font-weight: 600; width: 100%; box-shadow: 0 4px 15px rgba(240, 176, 176, 0.3); }
            .add-salon-submit-btn:hover { background-color: #e0a0a0; }
            .add-salon-close-btn { position: absolute; top: 15px; right: 15px; background: none; border: none; font-size: 24px; cursor: pointer; color: #999; }
            .add-salon-close-btn:hover { color: #333; }
            .add-salon-menu-section { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .add-salon-error { background-color: #f8d7da; color: #721c24; padding: 12px; border-radius: 5px; margin-bottom: 20px; }
            .favorite-btn { padding: 0; background-color: transparent; color: #f0b0b0; border: none; cursor: pointer; font-size: 24px; transition: opacity 0.3s; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; line-height: 1; font-family: Arial, sans-serif; }
            .favorite-btn:hover { opacity: 0.7; }
            .favorite-btn.active { color: #f0b0b0; opacity: 1; }
            .favorite-filter-btn { padding: 10px 20px; background-color: white; color: #666; border: 2px solid #e0e0e0; border-radius: 5px; text-decoration: none; font-size: 0.9em; font-weight: 500; }
            .favorite-filter-btn.active { background-color: #f0b0b0; color: white; border-color: #f0b0b0; }
            .back-to-main-btn { padding: 10px 20px; background-color: #f0b0b0; color: white; text-decoration: none; border-radius: 5px; font-weight: 600; box-shadow: 0 2px 8px rgba(240, 176, 176, 0.3); white-space: nowrap; display: inline-flex; align-items: center; gap: 5px; }
            .back-to-main-btn:hover { background-color: #e0a0a0; }
            .sort-options a { padding: 10px 20px; text-decoration: none; border-radius: 5px; font-size: 0.9em; font-weight: 500; }
            .sort-options a.active { background-color: #f0b0b0; color: white; box-shadow: 0 2px 10px rgba(240, 176, 176, 0.3); }
            .sort-options a:not(.active) { background-color: white; color: #666; border: 2px solid #e0e0e0; }
            .salons-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }
            .card { background: white; border: none; border-radius: 15px; padding: 25px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); position: relative; }
            .card-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 15px; position: relative; }
            .salon-name { font-size: 1.3em; font-weight: 600; color: #333; flex: 1; line-height: 1.4; }
            .reservation-btn { padding: 0; background-color: transparent; border: none; cursor: pointer; position: relative; width: 24px; height: 24px; display: flex; align-items: center; justify-content: center; }
            .reservation-btn img { width: 24px; height: 24px; object-fit: contain; }
            .location { color: #888; font-size: 0.9em; margin-bottom: 15px; display: flex; align-items: center; gap: 5px; cursor: pointer; }
            .location.collapsed { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
            .location.expanded { white-space: normal; }
            .location-icon { width: 16px; height: 16px; object-fit: contain; flex-shrink: 0; }
            .menu-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .menu-table td { border-bottom: 1px solid #f0f0f0; padding: 10px 0; }
            .menu-table tr:last-child td { border-bottom: none; }
            .price { text-align: right; font-weight: 600; color: #f0b0b0; font-size: 1.05em; }
            .modal { display: none; position: absolute; z-index: 1000; }
            .modal.show { display: block; }
            .modal-content { background-color: white; padding: 10px; border-radius: 10px; text-align: center; min-width: 200px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); position: relative; top: 5px; right: 0; }
            .modal-content .phone-number { font-size: 0.9em; font-weight: bold; color: #444; margin: 8px 0; }
            .modal-content .phone-link { display: inline-block; padding: 6px 12px; background-color: #f0b0b0; color: white; text-decoration: none; border-radius: 12px; font-weight: 600; font-size: 0.85em; box-shadow: 0 2px 8px rgba(240, 176, 176, 0.3); }
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
                .sort-wrapper { flex-direction: column; align-items: stretch; }
                .sort-options { justify-content: center; width: 100%; }
                .add-salon-btn { text-align: center; width: 100%; }
            }
        </style>
    </head>
    <body>
        <div class="cover-image-container">
            <img src="{{ url_for('static', filename='images/cover_2.jpg') }}" alt="Cover" class="cover-image">
        </div>
        
        <div class="content-wrapper">
        <h1>The Cut : INU</h1>
        
        <div class="search-box">
            <form action="">
                <div class="search-wrapper">
                    <input type="text" name="q" value="{{ request.args.get('q', '') }}">
                </div>
                <input type="hidden" name="sort" value="{{ request.args.get('sort', 'name') }}">
                {% if show_favorites %}
                <input type="hidden" name="favorites" value="true">
                {% endif %}
                <button type="submit">검색</button>
            </form>
            <div class="sort-wrapper">
                {% if not show_favorites %}
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
                {% endif %}
                <div style="display: flex; gap: 10px; align-items: center;">
                    {% if show_favorites %}
                    <a href="/" class="back-to-main-btn">←</a>
                    {% else %}
                    <a href="?q={{ request.args.get('q', '') }}&sort={{ request.args.get('sort', 'name') }}&favorites=true" class="favorite-filter-btn">찜한 미용실</a>
                    <a href="#" onclick="showAddSalonModal(); return false;" class="add-salon-btn">+add</a>
                    {% endif %}
                </div>
            </div>
        </div>

        {% if not salons %}
            <p style="text-align:center;">검색 결과가 없습니다.</p>
        {% else %}
        <div class="salons-grid">
            {% for salon in salons %}
            <div class="card" data-salon-id="{{ salon['id'] }}">
                <div class="card-header">
                    <div class="salon-name">
                        {{ salon['name'] }}
                    </div>
                    <div style="display: flex; gap: 5px; align-items: center;">
                    {% if salon['phone'] %}
                        <button class="reservation-btn" onclick="showPhoneModal(event, '{{ salon['phone'] }}', {{ salon['id'] }})">
                            <img src="{{ url_for('static', filename='images/call_icon.png') }}" alt="전화">
                        </button>
                        <div id="phoneModal-{{ salon['id'] }}" class="modal">
                            <div class="modal-content">
                                <div class="phone-number" id="modalPhoneNumber-{{ salon['id'] }}"></div>
                                <a href="#" id="modalPhoneLink-{{ salon['id'] }}" class="phone-link">전화 걸기</a>
                            </div>
                        </div>
                    {% endif %}
                        <button class="favorite-btn {% if salon['is_favorite'] %}active{% endif %}" onclick="toggleFavorite({{ salon['id'] }}, this)" data-salon-id="{{ salon['id'] }}">{% if salon['is_favorite'] %}♥{% else %}♡{% endif %}</button>
                    </div>
                </div>
                <div class="location {% if salon['is_location_truncated'] %}collapsed{% endif %}"
                     data-full="{{ salon['full_location'] }}"
                     data-short="{{ salon['display_location'] }}"
                     data-is-long="{{ 'true' if salon['is_location_truncated'] else 'false' }}"
                     onclick="toggleLocation(this)">
                    <img src="{{ url_for('static', filename='images/Subject 6.png') }}" alt="위치" class="location-icon">
                    <span class="location-text">{{ salon['display_location'] if salon['is_location_truncated'] else salon['full_location'] }}</span>
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
            
            // 찜 기능 (DB 기반)
            function toggleFavorite(salonId, btn) {
                const isFavorite = btn.classList.contains('active');
                
                fetch('/api/favorites', {
                    method: isFavorite ? 'DELETE' : 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ salon_id: salonId })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        if (isFavorite) {
                            btn.classList.remove('active');
                            btn.textContent = '♡';
                        } else {
                            btn.classList.add('active');
                            btn.textContent = '♥';
                        }
                        filterFavorites();
                    } else {
                        alert('찜 기능 처리 중 오류가 발생했습니다.');
                    }
                })
                .catch(error => {
                    console.error('Error toggling favorite:', error);
                    alert('찜 기능 처리 중 오류가 발생했습니다.');
                });
            }
            
            function filterFavorites() {
                const showFavorites = new URLSearchParams(window.location.search).get('favorites') === 'true';
                if (!showFavorites) return;
                
                fetch('/api/favorites')
                    .then(response => response.json())
                    .then(data => {
                        const favoriteIds = data.favorites || [];
                        const cards = document.querySelectorAll('.card');
                        
                        cards.forEach(card => {
                            const salonId = parseInt(card.getAttribute('data-salon-id'));
                            if (favoriteIds.includes(salonId)) {
                                card.style.display = '';
                            } else {
                                card.style.display = 'none';
                            }
                        });
                    })
                    .catch(error => {
                        console.error('Error loading favorites:', error);
                    });
            }
            
            // 페이지 로드 시 찜 필터링 적용
            document.addEventListener('DOMContentLoaded', function() {
                filterFavorites();
            });
            
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
                const favorites = '{{ "true" if show_favorites else "" }}';
                const url = '?q=' + encodeURIComponent(query) + '&sort=' + currentSortType + '&service=' + encodeURIComponent(serviceName) + (favorites ? '&favorites=true' : '');
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
            
            function showAddSalonModal() {
                document.getElementById('addSalonModal').classList.add('show');
            }
            
            function closeAddSalonModal() {
                document.getElementById('addSalonModal').classList.remove('show');
            }
            
            function addMenuItem() {
                const container = document.getElementById('add-salon-menu-container');
                const newItem = document.createElement('div');
                newItem.className = 'add-salon-menu-item';
                newItem.innerHTML = `
                    <input type="text" name="service_name[]" placeholder="서비스명 (예: 여성 커트)">
                    <input type="text" name="price[]" placeholder="가격">
                    <button type="button" class="add-salon-remove-btn" onclick="removeMenuItem(this)">삭제</button>
                `;
                container.appendChild(newItem);
                
                const firstItem = container.querySelector('.add-salon-menu-item');
                if (firstItem && container.children.length > 1) {
                    const firstRemoveBtn = firstItem.querySelector('.add-salon-remove-btn');
                    if (firstRemoveBtn) firstRemoveBtn.style.display = 'block';
                }
            }
            
            function removeMenuItem(btn) {
                const container = document.getElementById('add-salon-menu-container');
                if (container.children.length > 1) {
                    btn.parentElement.remove();
                    if (container.children.length === 1) {
                        const firstRemoveBtn = container.querySelector('.add-salon-remove-btn');
                        if (firstRemoveBtn) firstRemoveBtn.style.display = 'none';
                    }
                }
            }
            
            // 모달 외부 클릭 시 닫기
            document.getElementById('addSalonModal')?.addEventListener('click', function(event) {
                if (event.target === this) {
                    closeAddSalonModal();
                }
            });
            
        </script>
        
        <!-- 미용실 추가 모달 -->
        <div id="addSalonModal" class="add-salon-modal">
            <div class="add-salon-modal-content">
                <button class="add-salon-close-btn" onclick="closeAddSalonModal()">&times;</button>
                <h2>새로운 미용실 추가하기</h2>
                
                <div id="addSalonError" class="add-salon-error" style="display: none;"></div>
                
                <form method="POST" action="/add" id="addSalonForm">
                    <div class="add-salon-form-group">
                        <label for="add-salon-name">미용실 이름 *</label>
                        <input type="text" id="add-salon-name" name="name" required>
                    </div>
                    
                    <div class="add-salon-form-group">
                        <label for="add-salon-location">위치</label>
                        <input type="text" id="add-salon-location" name="location">
                    </div>
                    
                    <div class="add-salon-form-group">
                        <label for="add-salon-phone">전화번호</label>
                        <input type="tel" id="add-salon-phone" name="phone" placeholder="예: 0507-1234-5678">
                    </div>
                    
                    <div class="add-salon-menu-section">
                        <label style="margin-bottom: 15px; display: block;">메뉴 및 가격</label>
                        <div id="add-salon-menu-container">
                            <div class="add-salon-menu-item">
                                <input type="text" name="service_name[]" placeholder="서비스명 (예: 남성 커트)">
                                <input type="text" name="price[]" placeholder="가격">
                                <button type="button" class="add-salon-remove-btn" onclick="removeMenuItem(this)" style="display: none;">삭제</button>
                            </div>
                        </div>
                        <button type="button" class="add-salon-add-menu-btn" onclick="addMenuItem()">+ 메뉴 추가</button>
                    </div>
                    
                    <button type="submit" class="add-salon-submit-btn">미용실 등록하기</button>
                </form>
            </div>
        </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(
        html,
        salons=salons,
        get_db_connection=get_db_connection,
        request=request,
        sort_by=sort_by,
        service_type=service_type,
        show_favorites=show_favorites
    )

@app.route('/api/favorites', methods=['GET'])
def get_favorites():
    conn = get_db_connection()
    favorites = conn.execute('SELECT salon_id FROM favorites').fetchall()
    conn.close()
    return jsonify({'favorites': [row['salon_id'] for row in favorites]})

@app.route('/api/favorites', methods=['POST'])
def add_favorite():
    data = request.get_json()
    salon_id = data.get('salon_id')
    
    if not salon_id:
        return jsonify({'success': False, 'error': '미용실 ID가 필요합니다.'})
    
    conn = get_db_connection()
    try:
        conn.execute('INSERT OR IGNORE INTO favorites (salon_id) VALUES (?)', (salon_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/favorites', methods=['DELETE'])
def remove_favorite():
    data = request.get_json()
    salon_id = data.get('salon_id')
    
    if not salon_id:
        return jsonify({'success': False, 'error': '미용실 ID가 필요합니다.'})
    
    conn = get_db_connection()
    try:
        conn.execute('DELETE FROM favorites WHERE salon_id = ?', (salon_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True})
    except Exception as e:
        conn.close()
        return jsonify({'success': False, 'error': str(e)})

@app.route('/add', methods=['POST'])
def add_salon():
    name = request.form.get('name', '').strip()
    location = request.form.get('location', '').strip()
    phone = request.form.get('phone', '').strip() or None
    
    if not name:
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    
    # 미용실 추가
    cursor = conn.cursor()
    cursor.execute('INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)',
                  (name, location, phone))
    salon_id = cursor.lastrowid
    
    # 메뉴 추가
    service_names = request.form.getlist('service_name[]')
    prices = request.form.getlist('price[]')
    
    for service_name, price in zip(service_names, prices):
        service_name = service_name.strip()
        try:
            price = int(price.strip()) if price.strip() else 0
            if service_name and price > 0:
                cursor.execute('INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)',
                             (salon_id, service_name, price))
        except ValueError:
            continue
    
    conn.commit()
    conn.close()
    
    return redirect(url_for('index'))

add_salon_html = """
<!doctype html>
<html>
<head>
    <title>새로운 미용실 추가 - The Cut : INU</title>
    <link rel="icon" type="image/jpeg" href="{{ url_for('static', filename='images/icon.jpg') }}">
    <style>
        @font-face {
            font-family: 'Cafe24Classictype';
            src: url('{{ url_for("static", filename="fonts/Cafe24Classictype-v1.1.ttf") }}') format('truetype');
            font-weight: normal;
            font-style: normal;
        }
        * { box-sizing: border-box; }
        body { font-family: 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f8f9fa; }
        h1 { font-family: 'Cafe24Classictype', 'Apple SD Gothic Neo', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; text-align: center; color: #f0b0b0; font-size: 1.8em; margin-bottom: 30px; font-weight: 600; }
        .form-group { margin-bottom: 20px; }
        label { display: block; margin-bottom: 8px; font-weight: 600; color: #333; }
        input[type="text"], input[type="tel"], input[type="number"] { width: 100%; padding: 12px; border: 2px solid #e0e0e0; border-radius: 5px; font-size: 1em; }
        input[type="text"]:focus, input[type="tel"]:focus, input[type="number"]:focus { outline: none; border-color: #f0b0b0; box-shadow: 0 0 0 3px rgba(240, 176, 176, 0.1); }
        .menu-item { display: flex; gap: 10px; margin-bottom: 10px; align-items: center; }
        .menu-item input[type="text"] { flex: 2; }
        .menu-item input[type="number"] { flex: 1; }
        .remove-btn { padding: 8px 15px; background-color: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9em; }
        .remove-btn:hover { background-color: #c82333; }
        .add-menu-btn { padding: 10px 20px; background-color: #6c757d; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 0.9em; margin-bottom: 20px; }
        .add-menu-btn:hover { background-color: #5a6268; }
        .submit-btn { padding: 12px 30px; background-color: #f0b0b0; color: white; border: none; border-radius: 5px; cursor: pointer; font-size: 1em; font-weight: 600; width: 100%; box-shadow: 0 4px 15px rgba(240, 176, 176, 0.3); }
        .submit-btn:hover { background-color: #e0a0a0; }
        .back-btn { display: inline-block; padding: 10px 20px; background-color: #6c757d; color: white; text-decoration: none; border-radius: 5px; margin-bottom: 20px; }
        .back-btn:hover { background-color: #5a6268; }
        .error { background-color: #f8d7da; color: #721c24; padding: 12px; border-radius: 5px; margin-bottom: 20px; }
        .menu-section { background-color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
    </style>
</head>
<body>
    <h1>새로운 미용실 추가하기</h1>
    
    <a href="/" class="back-btn">← 목록으로 돌아가기</a>
    
    {% if error %}
    <div class="error">{{ error }}</div>
    {% endif %}
    
    <form method="POST" action="/add">
        <div class="form-group">
            <label for="name">미용실 이름 *</label>
            <input type="text" id="name" name="name" required>
        </div>
        
        <div class="form-group">
            <label for="location">위치</label>
            <input type="text" id="location" name="location">
        </div>
        
        <div class="form-group">
            <label for="phone">전화번호</label>
            <input type="tel" id="phone" name="phone" placeholder="예: 0507-1234-5678">
        </div>
        
        <div class="menu-section">
            <label style="margin-bottom: 15px; display: block;">메뉴 및 가격</label>
            <div id="menu-container">
                <div class="menu-item">
                    <input type="text" name="service_name[]" placeholder="서비스명 (예: 남성 커트)">
                    <input type="text" name="price[]" placeholder="가격">
                    <button type="button" class="remove-btn" onclick="removeMenuItem(this)" style="display: none;">삭제</button>
                </div>
            </div>
            <button type="button" class="add-menu-btn" onclick="addMenuItem()">+ 메뉴 추가</button>
        </div>
        
        <button type="submit" class="submit-btn">미용실 등록하기</button>
    </form>
    
    <script>
        function addMenuItem() {
            const container = document.getElementById('menu-container');
            const newItem = document.createElement('div');
            newItem.className = 'menu-item';
            newItem.innerHTML = `
                <input type="text" name="service_name[]" placeholder="서비스명 (예: 여성 커트)">
                <input type="number" name="price[]" placeholder="가격" min="0">
                <button type="button" class="remove-btn" onclick="removeMenuItem(this)">삭제</button>
            `;
            container.appendChild(newItem);
            
            // 첫 번째 항목에도 삭제 버튼 표시
            const firstItem = container.querySelector('.menu-item');
            if (firstItem && container.children.length > 1) {
                const firstRemoveBtn = firstItem.querySelector('.remove-btn');
                if (firstRemoveBtn) firstRemoveBtn.style.display = 'block';
            }
        }
        
        function removeMenuItem(btn) {
            const container = document.getElementById('menu-container');
            if (container.children.length > 1) {
                btn.parentElement.remove();
                
                // 마지막 하나 남으면 첫 번째 항목의 삭제 버튼 숨기기
                if (container.children.length === 1) {
                    const firstRemoveBtn = container.querySelector('.remove-btn');
                    if (firstRemoveBtn) firstRemoveBtn.style.display = 'none';
                }
            }
        }
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    app.run(debug=True, port=5001)