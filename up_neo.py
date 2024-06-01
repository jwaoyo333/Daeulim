import json
import os
import sqlite3
import time
from langchain_google_genai import ChatGoogleGenerativeAI
# Use a pipeline as a high-level helper

# 비밀 키 파일 경로
secrets_file_path = './secret.json'

# 비밀 키 파일에서 API 키 읽기
with open(secrets_file_path) as f:
    secrets = json.loads(f.read())
os.environ["GOOGLE_API_KEY"] = secrets["api_key"]

# LangChain Google Generative AI 초기화
llm = ChatGoogleGenerativeAI(
    model="gemini-pro",
    system_prompt="너는 주어진 데이터에서 프로그램, 행사, 교육, 무료 상담 등의 활동들을 구분해내는 서비스야. 이용자의 행복을 위해 최선을 다해 노력해주렴",  # 시스템 프롬프트 설정
    temperature=0.5  # 온도 설정
)

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
        input_text = f"'{title}'이 '교육'이나 대상자를 위한 '프로그램'과 같은 안내 공지면 1을, '강사 모집 공고', '행정 결과' 등과 같은 행정 업무 관련 공지면 0을 반환해줘"
        
        result_value = llm.invoke(input_text)
        print(f"Result for ID {id}: {result_value.content.strip()}")
        
        if result_value.content.strip() == "0":
            ids_to_delete.append(id)

    # 처리된 행 수 업데이트
    processed_rows += len(batch)


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
