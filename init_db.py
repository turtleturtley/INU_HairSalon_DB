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

        # [7] 리안헤어 송도웰카운티점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('리안헤어 송도웰카운티점', '인천 연수구 인천타워대로54번길 9 에몬스프라자 1층 114호', '0507-1484-8214'))
        salon7_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon7_id, '남성 커트', 19800))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon7_id, '여성 커트', 22500))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon7_id, '펌', 78000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon7_id, '염색', 48000))

        # [8] 리안헤어 송도아메리칸타운더샵점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('리안헤어 송도아메리칸타운더샵점', '인천 연수구 송도과학로27번길 27 204-C동 2층 C217호', '0507-1395-5824'))
        salon8_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon8_id, '남성 커트', 20000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon8_id, '여성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon8_id, '펌', 70000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon8_id, '염색', 56000))

        # [9] WE.
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('WE.', '인천 연수구 하모니로 158 c동 409호', '0507-1475-4245'))
        salon9_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon9_id, '남성 커트', 28000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon9_id, '여성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon9_id, '펌', 140000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon9_id, '염색', 80000))

        # [10] 옵트헤어 인천송도점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('옵트헤어 인천송도점', '인천 연수구 하모니로 158 타임스페이스 C동 303호', '0507-1385-7108'))
        salon10_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon10_id, '남성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon10_id, '여성 커트', 22000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon10_id, '펌', 110000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon10_id, '염색', 100000))

        # [11] 에이앤느 송도 타임스페이스 본점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('에이앤느 송도 타임스페이스 본점', '인천 연수구 송도동 8-21', '0507-1445-0710'))
        salon11_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon11_id, '남성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon11_id, '여성 커트', 33000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon11_id, '펌', 110000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon11_id, '염색', 66000))

        # [12] 아슈드 헤어살롱 송도타임스페이스점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('아슈드 헤어살롱 송도타임스페이스점', '인천 연수구 하모니로 158 타임스페이스 C동 304호', None))
        salon12_id = cursor.lastrowid
        
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon12_id, '남성 커트', 22000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon12_id, '여성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon12_id, '펌', 90000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon12_id, '염색', 70000))

        # [13] 마끼에 타임스페이스점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('마끼에 타임스페이스점', '인천 연수구 하모니로 158 C동 307호, 308호', '0507-1411-5326'))
        salon13_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon13_id, '남성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon13_id, '여성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon13_id, '펌', 100000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon13_id, '염색', 120000))

        # [14] 아인크헤어 인천송도점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('아인크헤어 인천송도점', '인천 연수구 하모니로178번길 6 송도 중앙타워 2층 215, 216, 217호', '0507-1350-7471'))
        salon14_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon14_id, '남성 커트', 35000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon14_id, '여성 커트', 35000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon14_id, '펌', 140000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon14_id, '염색', 130000))

        # [15] 로미 메이크 헤어
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('로미 메이크 헤어', '인천 연수구 송도과학로27번길 15 1층 121호 로미 메이크 헤어', '0507-1329-7699'))
        salon15_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon15_id, '남성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon15_id, '여성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon15_id, '펌', 100000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon15_id, '염색', 100000))

        # [16] 제이디로얄 맨즈헤어 송도점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('제이디로얄 맨즈헤어 송도점', '인천 연수구 연구단지로55번길 16 2층 235호', '0507-1479-9326'))
        salon16_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon16_id, '남성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon16_id, '펌', 90000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon16_id, '염색', 70000))

        # [17] 잇키
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('잇키', '인천 연수구 인천타워대로180번길 11 B동 201, 202호', '0507-1416-1192'))
        salon17_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon17_id, '남성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon17_id, '여성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon17_id, '펌', 120000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon17_id, '염색', 110000))

        # [18] 라비앙르로즈 송도동점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('라비앙르로즈 송도동점', '인천 연수구 하모니로 158 타임스페이스 C동 212호', '0507-1483-6616'))
        salon18_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon18_id, '남성 커트', 13000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon18_id, '여성 커트', 13000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon18_id, '펌', 35000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon18_id, '염색', 38000))

        # [19] 스타일하우스 송도퍼스트파크점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('스타일하우스 송도퍼스트파크점', '인천 연수구 컨벤시아대로230번길 54 닥터플러스몰 A동 216호 스타일하우스 송도퍼스트파크점', '0507-1442-7926'))
        salon19_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon19_id, '남성 커트', 26000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon19_id, '여성 커트', 28000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon19_id, '펌', 100000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon19_id, '염색', 110000))

        # [20] 덕무드헤어 송도타임스페이스점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('덕무드헤어 송도타임스페이스점', '인천 연수구 하모니로 158 B동 314호', '0507-1449-0237'))
        salon20_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon20_id, '남성 커트', 23000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon20_id, '여성 커트', 23000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon20_id, '펌', 84000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon20_id, '염색', 70000))

        # [21] 아버헤어 트리플 2호점
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('아버헤어 트리플 2호점', '인천 연수구 송도과학로16번길 33-4 트리플스트리트 D동 지하 1층', '0507-1332-9360'))
        salon21_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon21_id, '남성 커트', 25000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon21_id, '여성 커트', 30000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon21_id, '펌', 100000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon21_id, '염색', 100000))

        # [22] 오프블랙바버샵
        cursor.execute("INSERT INTO salons (name, location, phone) VALUES (?, ?, ?)",
                       ('오프블랙바버샵', '인천 연수구 하모니로 158 타임스페이스 C동 지하1층 B20호', '0507-1371-7969'))
        salon22_id = cursor.lastrowid
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon22_id, '남성 커트', 45000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon22_id, '펌', 140000))
        cursor.execute("INSERT INTO menus (salon_id, service_name, price) VALUES (?, ?, ?)", (salon22_id, '염색', 45000))

        conn.commit()
    else:
        print("이미 데이터가 존재합니다.")

    conn.close()
    print("데이터베이스 초기화 완료! 'database.db' 파일이 생성되었습니다.")

if __name__ == '__main__':
    init_db()