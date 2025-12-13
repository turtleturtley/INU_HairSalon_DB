import sqlite3 #SQL lite 사용

def init_db():
    # 데이터베이스 파일 생성 (파일이 없으면 만들고 연결함)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # 1. 미용실 테이블 (Salons)
    # 기존 평점(rating)을 저장할 수 있게 설계
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS salons (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        location TEXT,
        rating REAL,
        source_url TEXT
    )
    ''')

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

    # --- 샘플 데이터 입력 (테스트용) ---
    # 데이터가 비어있을 때만 넣기
    cursor.execute('SELECT count(*) FROM salons')
    if cursor.fetchone()[0] == 0:
        print("샘플 데이터를 추가합니다...")
        
        # 미용실 1: 인천대 미용실 (예시)
        cursor.execute("INSERT INTO salons (name, location, rating) VALUES (?, ?, ?)",
                       ('스타일 헤어', '인천대 입구역 2번 출구', 4.5))
        salon1_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon1_id, '남성 커트', 15000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon1_id, '다운펌', 30000))

        # 미용실 2: 솔찬 공원 헤어 (예시)
        cursor.execute("INSERT INTO salons (name, location, rating) VALUES (?, ?, ?)",
                       ('솔찬 헤어샵', '송도동 123-45', 4.8))
        salon2_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon2_id, '여성 커트', 20000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon2_id, '전체 염색', 80000))

        conn.commit()
    else:
        print("이미 데이터가 존재합니다.")

    conn.close()
    print("데이터베이스 초기화 완료! 'database.db' 파일이 생성되었습니다.")

if __name__ == '__main__':
    init_db()