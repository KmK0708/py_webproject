# PostgreSQL 설정 가이드

## 📋 목차
1. [PostgreSQL 데이터베이스 생성](#1-postgresql-데이터베이스-생성)
2. [환경 변수 설정](#2-환경-변수-설정)
3. [데이터 마이그레이션](#3-데이터-마이그레이션)
4. [연결 테스트](#4-연결-테스트)
5. [문제 해결](#5-문제-해결)

---

## 1. PostgreSQL 데이터베이스 생성

### Windows에서 PostgreSQL 데이터베이스 생성

1. **pgAdmin 또는 명령줄 사용**

   **방법 A: pgAdmin 사용 (GUI)**
   - pgAdmin 4 실행
   - Servers → PostgreSQL → Databases 우클릭
   - Create → Database 선택
   - Database name: `crypto_db` 입력
   - Save 클릭

   **방법 B: 명령줄 사용 (cmd/PowerShell)**
   ```bash
   # PostgreSQL 명령줄 접속 (비밀번호 입력 필요)
   psql -U postgres

   # 데이터베이스 생성
   CREATE DATABASE crypto_db;

   # 생성 확인
   \l

   # 종료
   \q
   ```

2. **연결 정보 확인**
   - Host: `localhost`
   - Port: `5432` (기본값)
   - Database: `crypto_db`
   - Username: `postgres`
   - Password: 설치 시 설정한 비밀번호

---

## 2. 환경 변수 설정

### `.env` 파일 수정

1. `backend/.env` 파일을 열기

2. 기존 SQLite 설정을 주석 처리하고 PostgreSQL 설정 활성화:

   ```bash
   # Database Configuration
   # SQLite (기본값)
   # DATABASE_URL=sqlite:///crypto_dashboard.db

   # PostgreSQL (로컬) - 사용 중
   DATABASE_URL=postgresql://postgres:your_password@localhost:5432/crypto_db

   # Flask Configuration
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

3. **중요**: `your_password`를 실제 postgres 비밀번호로 변경!

### 연결 문자열 형식

```
postgresql://username:password@host:port/database
```

예시:
- 로컬: `postgresql://postgres:mypassword@localhost:5432/crypto_db`
- 클라우드 (Render): `postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname`
- 클라우드 (Supabase): `postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres`

---

## 3. 데이터 마이그레이션

### SQLite → PostgreSQL 데이터 이전

1. **마이그레이션 스크립트 실행**

   ```bash
   cd backend
   python migrate_to_postgresql.py
   ```

2. **진행 과정**
   - 소스 데이터베이스 (SQLite) 연결
   - 타겟 데이터베이스 (PostgreSQL) 연결
   - 코인 가격 데이터 복사
   - 뉴스 데이터 복사
   - 검증

3. **예상 출력**
   ```
   ╔══════════════════════════════════════════════════════════════════════════════╗
   ║                    SQLite → PostgreSQL 마이그레이션                         ║
   ╚══════════════════════════════════════════════════════════════════════════════╝

   ============================================================
   현재 설정:
   ============================================================
   데이터베이스 타입: postgresql
   DATABASE_URL: postgresql://postgres:***@localhost:5432...
   FLASK_ENV: development
   FLASK_DEBUG: True
   ============================================================

   [1] 소스 데이터베이스 연결 중...
   ✅ SQLite 연결: sqlite:///crypto_dashboard.db
   ✅ 소스 연결 완료

   [2] 타겟 데이터베이스 연결 중...
   ✅ PostgreSQL 연결 성공: localhost:5432/crypto_db
   ✅ 타겟 연결 완료

   [3] 코인 가격 데이터 마이그레이션 중...
     총 1234개의 코인 가격 레코드 발견
     진행 중... 100/1234
     진행 중... 200/1234
     ...
   ✅ 코인 가격 마이그레이션 완료: 1234개 성공, 0개 실패

   [4] 뉴스 데이터 마이그레이션 중...
     총 456개의 뉴스 레코드 발견
     진행 중... 50/456
     ...
   ✅ 뉴스 마이그레이션 완료: 456개 성공, 0개 실패
   ```

---

## 4. 연결 테스트

### app.py로 연결 확인

```bash
cd backend
python app.py
```

**성공 시 출력:**
```
✅ PostgreSQL 연결 성공: localhost:5432/crypto_db
============================================================
 Flask REST API 서버 시작 (React Frontend용)
============================================================
모니터링 코인: 100개
API 주소: http://localhost:5000
CORS: 활성화 (React 통신 가능)

백그라운드 작업:
  ✓ 뉴스 자동 수집: 30분마다
  ✓ 가격 자동 저장: 10분마다
============================================================
```

### 웹 브라우저에서 API 테스트

브라우저에서 다음 URL 접속:
- http://localhost:5000/api/health - 서버 상태 확인
- http://localhost:5000/api/current-prices - 코인 가격 확인
- http://localhost:5000/api/news - 뉴스 확인

---

## 5. 문제 해결

### 문제 1: `psycopg2` 설치 오류

**오류 메시지:**
```
ERROR: Could not build wheels for psycopg2
```

**해결 방법:**
```bash
pip install psycopg2-binary
```

---

### 문제 2: 연결 거부 (Connection refused)

**오류 메시지:**
```
could not connect to server: Connection refused
```

**해결 방법:**
1. PostgreSQL 서비스가 실행 중인지 확인
   - Windows: 서비스 관리자에서 `postgresql-x64-xx` 확인
   - 시작 → 서비스 → postgresql 찾기 → 실행 중인지 확인

2. 포트 번호 확인 (기본값: 5432)

---

### 문제 3: 인증 실패 (Authentication failed)

**오류 메시지:**
```
FATAL: password authentication failed for user "postgres"
```

**해결 방법:**
1. `.env` 파일의 비밀번호가 정확한지 확인
2. 비밀번호에 특수문자가 있다면 URL 인코딩 필요
   - 예: `@` → `%40`, `#` → `%23`

---

### 문제 4: 데이터베이스가 존재하지 않음

**오류 메시지:**
```
FATAL: database "crypto_db" does not exist
```

**해결 방법:**
```sql
-- psql -U postgres 실행 후
CREATE DATABASE crypto_db;
```

---

### 문제 5: 마이그레이션 중 중복 키 오류

**오류 메시지:**
```
duplicate key value violates unique constraint
```

**해결 방법:**
1. PostgreSQL 데이터베이스 초기화
   ```sql
   DROP DATABASE crypto_db;
   CREATE DATABASE crypto_db;
   ```

2. 마이그레이션 재실행
   ```bash
   python migrate_to_postgresql.py
   ```

---

## 6. SQLite로 되돌리기

PostgreSQL에서 다시 SQLite로 되돌리려면:

1. `.env` 파일 수정:
   ```bash
   # PostgreSQL 주석 처리
   # DATABASE_URL=postgresql://postgres:password@localhost:5432/crypto_db

   # SQLite 활성화
   DATABASE_URL=sqlite:///crypto_dashboard.db
   ```

2. 서버 재시작

---

## 7. 프로덕션 배포 시

### Render.com PostgreSQL 사용

1. Render 대시보드에서 PostgreSQL 생성
2. Internal Database URL 복사
3. `.env` 파일에 붙여넣기

### Supabase 사용

1. Supabase 프로젝트 생성
2. Settings → Database → Connection String 복사
3. `.env` 파일에 붙여넣기

---

## 📌 체크리스트

마이그레이션 완료 후 확인:

- [ ] PostgreSQL 서비스 실행 중
- [ ] `crypto_db` 데이터베이스 생성됨
- [ ] `.env` 파일에 PostgreSQL URL 설정
- [ ] `pip install -r requirements.txt` 실행
- [ ] `python migrate_to_postgresql.py` 성공
- [ ] `python app.py` 실행 시 "PostgreSQL 연결 성공" 메시지
- [ ] 웹 브라우저에서 API 정상 작동
- [ ] 프론트엔드에서 데이터 정상 표시

---

## 💡 추가 정보

### PostgreSQL vs SQLite 비교

| 특징 | SQLite | PostgreSQL |
|------|--------|------------|
| 설치 | 불필요 | 필요 |
| 동시 접속 | 제한적 | 우수 |
| 성능 (대용량) | 느림 | 빠름 |
| 배포 | 어려움 | 쉬움 |
| 백업 | 파일 복사 | pg_dump |
| 권장 용도 | 개발/테스트 | 프로덕션 |

### 유용한 PostgreSQL 명령어

```sql
-- 데이터베이스 목록
\l

-- 테이블 목록
\dt

-- 테이블 구조
\d coin_prices

-- 레코드 수 확인
SELECT COUNT(*) FROM coin_prices;

-- 최근 데이터 확인
SELECT * FROM coin_prices ORDER BY timestamp DESC LIMIT 10;
```

---

**문제가 발생하면 이 가이드를 참고하세요!** 🚀
