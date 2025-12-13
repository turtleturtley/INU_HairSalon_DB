import sqlite3 # SQL lite 사용
import os      # [추가됨] 파일 삭제 기능을 위해 필요

def init_db():
    # [추가됨] 기존 database.db 파일이 있으면 삭제함 (매번 rm 치기 귀찮음 방지)
    if os.path.exists('database.db'):
        os.remove('database.db')
        print("기존 데이터베이스를 삭제하고 새로 생성합니다...")

    # 데이터베이스 파일 생성 (파일이 없으면 만들고 연결함)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. 미용실 테이블 (Salons)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        phone TEXT,
        source_url TEXT
    )
    ''')
    
    # 전화번호 컬럼이 없으면 추가 (기존 데이터베이스 마이그레이션)
    try:
        cursor.execute('ALTER TABLE salons ADD COLUMN phone TEXT')
    except sqlite3.OperationalError:
        pass  # 컬럼이 이미 존재하는 경우

    # 2. 메뉴/가격 테이블 (Menus)
    # 미용실 ID(salon_id)를 외래키로 사용하여 미용실과 연결
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS menus (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        salon_id INTEGER,
        service_name TEXT NOT NULL,
        price INTEGER NOT NULL,
        FOREIGN KEY (salon_id) REFERENCES salons (id)
    )
    ''')

    # --- 데이터 입력 ---
    # 데이터가 비어있을 때만 넣기
    cursor.execute('SELECT count(*) FROM salons')
    if cursor.fetchone()[0] == 0:
        print("실제 데이터를 추가합니다...")
        
        # [1] 헤어옵션 살롱
        cursor.execute("INSERT INTO salons (name, location) VALUES (?, ?)",
                       ('헤어옵션 살롱', '인천 연수구 아카데미로 119 복지회관 11호관 2층 207호'))
        salon1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon1_id, '남성 커트', 16000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon1_id, '여성 커트', 18000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon1_id, '펌', 60000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon1_id, '염색', 60000))

        # [2] 올룸
        cursor.execute("INSERT INTO salons (name, location) VALUES (?, ?)",
                       ('올룸', '인천 연수구 하모니로178번길 22 gtx센트럴 b동 304호'))
        salon2_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon2_id, '남성 커트', 27000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon2_id, '여성 커트', 27000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon2_id, '펌', 150000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon2_id, '염색', 110000))

        # [3] 린 헤어
        cursor.execute("INSERT INTO salons (name, location) VALUES (?, ?)",
                       ('린 헤어', '인천 연수구 하모니로188번길 17 sk뷰센트럴오피스텔상가 157호 린헤어'))
        salon3_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon3_id, '남성 커트', 20000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon3_id, '여성 커트', 22000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon3_id, '펌', 70000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon3_id, '염색', 70000))

        # [4] 고정현헤어 쉐라톤점
        cursor.execute("INSERT INTO salons (name, location) VALUES (?, ?)",
                       ('고정현헤어 쉐라톤점', '인천 연수구 컨벤시아대로 153 쉐라톤호텔 6층'))
        salon4_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon4_id, '남성 커트', 38000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon4_id, '여성 커트', 44000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon4_id, '펌', 165000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon4_id, '염색', 170000))

        # [5] 송유헤어
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('송유헤어', '인천 연수구 하모니로138번길 11 송도캐슬센트럴파크 102동 325호', '0507-1396-3022'))
        salon5_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon5_id, '남성 커트', 23000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon5_id, '여성 커트', 28000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon5_id, '펌', 79000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon5_id, '염색', 70000))

        # [6] 리닛
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('리닛', '인천 연수구 하모니로 144 지웰푸르지오 b동 208호', '0507-1419-2453'))
        salon6_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon6_id, '남성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon6_id, '여성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon6_id, '펌', 90000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon6_id, '염색', 90000))

        conn.commit()
    else:
        print("이미 데이터가 존재합니다.")

    conn.close()
    print("데이터베이스 초기화 완료! 'database.db' 파일이 생성되었습니다.")

if __name__ == '__main__':
    init_db()