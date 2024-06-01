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

# SQLite 데이터베이스 파일 경로
db_path = './db.sqlite3'

# 데이터베이스 연결
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 'title' 칼럼을 모두 가져오는 SQL 쿼리
query = 'SELECT id, title FROM search_post'  # search_post를 실제 테이블 이름으로 바꾸세요

# SQL 쿼리 실행
cursor.execute(query)

# 결과를 가져와서 한 행씩 처리
rows = cursor.fetchall()

# 삭제할 행들의 ID를 저장할 리스트
ids_to_delete = []

# 총 행 수와 처리된 행 수 초기화
total_rows = len(rows)
processed_rows = 0

# 각 title을 개별적으로 검사하여 30초마다 10개씩 처리
while processed_rows < total_rows:
    batch = rows[processed_rows:processed_rows + 10]

    for row in batch:
        id, title = row
        print(f"Checking title: {title}")
        input_text = f"'{title}'에서 '교육' 또는 '프로그램' 또는 '캠페인' 또는 '참여자' 또는 '신청자' 또는 '무료'라는 단어가 있으면 1을, 없으면 0을 반환해줘"
        
        result_value = llm.invoke(input_text)
        print(f"Result for ID {id}: {result_value.content.strip()}")
        
        if result_value.content.strip() == "0":
            ids_to_delete.append(id)

    # 처리된 행 수 업데이트
    processed_rows += len(batch)

    # 30초 동안 대기
    time.sleep(30)

# 삭제할 행들을 데이터베이스에서 제거
delete_query = 'DELETE FROM search_post WHERE id = ?'
for id_to_delete in ids_to_delete:
    cursor.execute(delete_query, (id_to_delete,))
    print(f"Deleted ID {id_to_delete}")

# 변경사항 커밋
conn.commit()

# 연결 닫기
conn.close()

print("Completed deletions.")
