# 클라우드 데이터베이스 설정 가이드 (집/회사 공유)

여러 위치에서 동일한 데이터베이스에 접속하기 위한 가이드입니다.

---

## 🎯 목표
- 회사와 집에서 같은 데이터베이스 사용
- 로컬 PostgreSQL 불필요
- 데이터 자동 동기화

---

## 방법 1: Supabase (가장 추천)

### 장점
- ✅ 완전 무료 (500MB)
- ✅ 설정 매우 간단 (5분 이내)
- ✅ 웹 대시보드 제공
- ✅ 자동 백업
- ✅ SSL 보안 연결

### 단계별 설정

#### 1. Supabase 계정 생성
1. https://supabase.com 접속
2. "Start your project" 클릭
3. GitHub 계정으로 로그인

#### 2. 프로젝트 생성
1. "New Project" 클릭
2. 다음 정보 입력:
   - **Name**: `crypto-dashboard` (원하는 이름)
   - **Database Password**: 강력한 비밀번호 입력 (꼭 기억하세요!)
   - **Region**: `Northeast Asia (Seoul)` 선택 (한국에서 가장 빠름)
3. "Create new project" 클릭
4. 프로젝트 생성 대기 (약 2분)

#### 3. 연결 정보 확인
1. 프로젝트 대시보드에서 **Settings** (⚙️) → **Database** 클릭
2. **Connection String** 섹션에서 **URI** 탭 선택
3. "Use connection pooling" 체크박스 **해제**
4. 연결 문자열 복사:
   ```
   postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres
   ```

#### 4. `.env` 파일 수정
```bash
# Database Configuration
# Supabase PostgreSQL (클라우드)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.xxxxx.supabase.co:5432/postgres

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

**중요:** `[YOUR-PASSWORD]` 부분을 실제 비밀번호로 변경!

#### 5. 데이터 마이그레이션
```bash
cd backend
python migrate_to_postgresql.py
```

#### 6. 테스트
```bash
python test_db_connection.py
```

성공 시 출력:
```
[OK] PostgreSQL connected: db.xxxxx.supabase.co:5432/postgres
[SUCCESS] All tests passed!
```

#### 7. 다른 컴퓨터에서 사용
1. 프로젝트를 Git으로 동기화 (또는 USB로 복사)
2. `.env` 파일만 동일하게 설정
3. 바로 사용 가능! 🎉

---

## 방법 2: Railway (무료 크레딧 $5)

### 장점
- ✅ $5 무료 크레딧 제공
- ✅ 사용량 기반 과금 (작은 프로젝트는 거의 무료)
- ✅ 자동 백업
- ✅ 빠른 속도

### 단계별 설정

#### 1. Railway 계정 생성
1. https://railway.app 접속
2. "Start a New Project" 클릭
3. GitHub 계정으로 로그인

#### 2. PostgreSQL 생성
1. "New Project" → "Provision PostgreSQL" 클릭
2. 프로젝트 이름 입력 (예: `crypto-dashboard`)
3. PostgreSQL 서비스 자동 생성됨

#### 3. 연결 정보 확인
1. PostgreSQL 서비스 클릭
2. **Variables** 탭에서 `DATABASE_URL` 복사
3. 형식: `postgresql://postgres:password@xxx.railway.app:5432/railway`

#### 4. `.env` 파일 수정
```bash
# Database Configuration
# Railway PostgreSQL (클라우드)
DATABASE_URL=postgresql://postgres:password@xxx.railway.app:5432/railway

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

#### 5. 마이그레이션 및 테스트
```bash
cd backend
python migrate_to_postgresql.py
python test_db_connection.py
```

---

## 방법 3: ElephantSQL (20MB 무료)

### 장점
- ✅ 설정 가장 간단
- ✅ 영구 무료 (20MB)
- ✅ 신용카드 불필요

### 단계별 설정

#### 1. 계정 생성
1. https://elephantsql.com 접속
2. "Get a managed database today" 클릭
3. 이메일로 회원가입

#### 2. 인스턴스 생성
1. "Create New Instance" 클릭
2. **Name**: `crypto-dashboard`
3. **Plan**: `Tiny Turtle (Free)` 선택
4. **Region**: `Azure: South Korea (Seoul)` 선택
5. "Create instance" 클릭

#### 3. 연결 정보 확인
1. 생성된 인스턴스 클릭
2. **URL** 복사
3. 형식: `postgresql://xxx:xxx@suleiman.db.elephantsql.com/xxx`

#### 4. `.env` 파일 수정
```bash
# Database Configuration
# ElephantSQL (클라우드)
DATABASE_URL=postgresql://xxx:xxx@suleiman.db.elephantsql.com/xxx

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
```

---

## 비교표

| 서비스 | 무료 용량 | 장점 | 단점 |
|--------|----------|------|------|
| **Supabase** | 500MB | 대시보드 우수, 한국 서버 | - |
| **Railway** | $5 크레딧 | 속도 빠름 | 크레딧 소진 시 유료 |
| **ElephantSQL** | 20MB | 가장 간단 | 용량 작음 |

### 추천
- **프로젝트 테스트용**: Supabase (500MB면 충분)
- **빠른 속도 필요**: Railway
- **가장 간단**: ElephantSQL (데이터 적을 때)

---

## Git으로 여러 컴퓨터에서 작업하기

### 1. `.env` 파일 보안 설정

`.env` 파일은 비밀번호가 포함되어 있어서 Git에 올리면 안 됩니다!

#### 이미 `.gitignore`에 추가되어 있는지 확인:
```bash
cat .gitignore
```

`.env`가 있어야 합니다. 없다면 추가:
```bash
echo ".env" >> .gitignore
```

### 2. 회사에서 Git Push
```bash
cd d:\py_webproject
git add .
git commit -m "PostgreSQL setup complete"
git push origin main
```

### 3. 집에서 Git Pull
```bash
cd ~/py_webproject
git pull origin main
```

### 4. 집에서 `.env` 파일 생성
```bash
cd backend
cp .env.example .env
# 그리고 .env 파일 열어서 Supabase URL 입력
```

### 5. 패키지 설치
```bash
pip install -r requirements.txt
```

### 6. 바로 사용!
```bash
python app.py
```

---

## 데이터베이스 전환 체크리스트

### 로컬 PostgreSQL → 클라우드 PostgreSQL

- [ ] 클라우드 데이터베이스 생성 (Supabase/Railway/ElephantSQL)
- [ ] 연결 URL 복사
- [ ] `.env` 파일에 URL 붙여넣기
- [ ] `python test_db_connection.py` 실행
- [ ] 연결 성공 확인
- [ ] `python migrate_to_postgresql.py` 실행 (기존 데이터 이전)
- [ ] `python app.py` 실행
- [ ] 프론트엔드에서 데이터 확인
- [ ] Git push (`.env` 제외)
- [ ] 다른 컴퓨터에서 Git pull
- [ ] 다른 컴퓨터에서 `.env` 파일 생성
- [ ] 다른 컴퓨터에서 바로 사용

---

## 문제 해결

### 문제 1: "SSL connection required"

**해결:**
DATABASE_URL 끝에 `?sslmode=require` 추가:
```bash
DATABASE_URL=postgresql://postgres:pass@host:5432/db?sslmode=require
```

### 문제 2: "too many connections"

**해결:**
무료 플랜은 동시 연결 수 제한이 있습니다.
- app.py에서 `pool_size=5, max_overflow=10`으로 수정
- 또는 연결 풀링 사용

### 문제 3: "connection timeout"

**해결:**
- 방화벽 확인
- 인터넷 연결 확인
- 클라우드 DB가 깨어있는지 확인 (무료 플랜은 비활성화될 수 있음)

---

## 보안 팁

### `.env` 파일 관리
1. **절대 Git에 올리지 마세요!**
2. 각 컴퓨터에서 개별로 생성
3. 비밀번호는 안전하게 보관

### 안전한 비밀번호 공유 방법
- 1Password, Bitwarden 등 비밀번호 관리자 사용
- 또는 암호화된 메신저 사용 (Signal, Telegram)
- 이메일로 보내지 마세요!

---

## 다음 단계

클라우드 DB 설정이 완료되면:

1. ✅ 회사와 집에서 동일한 데이터 사용 가능
2. ✅ 데이터 자동 동기화
3. ✅ 백업 걱정 없음
4. ✅ 언제든 배포 가능 (Render, Vercel 등)

---

**추천 순서:**
1. Supabase 선택 (가장 쉽고 용량 큼)
2. 프로젝트 생성 (5분)
3. DATABASE_URL 복사
4. `.env` 수정
5. 마이그레이션
6. Git push
7. 집에서 pull 후 바로 사용!

궁금한 점이 있으면 언제든 물어보세요! 🚀
