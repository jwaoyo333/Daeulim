import json
import os
import sqlite3
import time
from langchain_google_genai import ChatGoogleGenerativeAI

# 비밀 키 파일 경로
secrets_file_path = './secret.json'

# 비밀 키 파일에서 API 키 읽기
with open(secrets_file_path) as f:
    secrets = json.loads(f.read())
os.environ["GOOGLE_API_KEY"] = secrets["api_key"]

# LangChain Google Generative AI 초기화
llm = ChatGoogleGenerativeAI(model="gemini-pro")

# 기존 SQLite 데이터베이스 파일 경로
db_path = './db.sqlite3'

# 새로운 SQLite 데이터베이스 파일 경로
cleaned_db_path = './cleaned_db.sqlite3'

# 기존 데이터베이스 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 새로운 데이터베이스 연결
cleaned_conn = sqlite3.connect(cleaned_db_path)
cleaned_cursor = cleaned_conn.cursor()

# 기존 데이터베이스의 구조를 새로운 데이터베이스에 복사
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='search_post'")
create_table_query = cursor.fetchone()[0]
cleaned_cursor.execute(create_table_query)

# 'title' 칼럼을 모두 가져오는 SQL 쿼리
query = 'SELECT * FROM search_post'  # search_post를 실제 테이블 이름으로 바꾸세요

# SQL 쿼리 실행
cursor.execute(query)

# 결과를 가져와서 한 행씩 처리
rows = cursor.fetchall()

# 총 행 수와 처리된 행 수 초기화
total_rows = len(rows)
processed_rows = 0

# 각 title을 개별적으로 검사하여 30초마다 10개씩 처리
while processed_rows < total_rows:
    batch = rows[processed_rows:processed_rows + 10]

    for row in batch:
        id, title = row[0], row[1]  # ID와 Title 칼럼을 가져옵니다.
        print(f"Checking title: {title}")
        input_text = f"You are a service that find programs or educations informations for old aged or disabled people or teenagers. In '{title}', if you find '교육'or'프로그램'or'캠페인'or'참여자'or'신청자'or'무료' return 1. else return 0."
        
        result_value = llm.invoke(input_text)
        print(f"Result for ID {id}: {result_value.content.strip()}")
        
        if result_value.content.strip() == "1":
            # 해당 행을 새로운 데이터베이스에 삽입
            placeholders = ', '.join(['?'] * len(row))
            insert_query = f'INSERT INTO search_post VALUES ({placeholders})'
            cleaned_cursor.execute(insert_query, row)

    # 처리된 행 수 업데이트
    processed_rows += len(batch)

    # 30초 동안 대기
    time.sleep(30)

# 변경사항 커밋
cleaned_conn.commit()

# 연결 닫기
conn.close()
cleaned_conn.close()

print("Completed processing and saved to cleaned_db.sqlite3.")
