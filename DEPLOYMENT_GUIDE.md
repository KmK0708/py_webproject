# 웹 배포 가이드

## 📋 배포 개요

- **Backend**: Render (Flask API)
- **Frontend**: Vercel (React)
- **Database**: Supabase (PostgreSQL)

---

## 🗄️ 1단계: Supabase 데이터베이스 설정 (완료)

이미 Supabase에 데이터베이스를 올리셨으므로 이 단계는 완료되었습니다.

### 필요한 정보:
Supabase에서 다음 정보를 확인하세요:
- **Database URL**: `postgresql://user:password@host:5432/database`

Supabase 대시보드 → Settings → Database → Connection String에서 확인 가능합니다.

---

## 🚀 2단계: Backend 배포 (Render)

### 2-1. Render 계정 생성
1. https://render.com 접속
2. GitHub 계정으로 로그인

### 2-2. GitHub 저장소 연결
1. Git 저장소를 GitHub에 푸시:
```bash
cd "c:\Users\user\OneDrive\바탕 화면\CPP\Py_webproject"
git add .
git commit -m "배포 준비 완료"
git push origin master
```

### 2-3. Render에서 Web Service 생성
1. Render 대시보드 → **New +** → **Web Service**
2. GitHub 저장소 연결 (Py_webproject)
3. 다음 설정 입력:

**기본 설정:**
- **Name**: `crypto-dashboard-api` (원하는 이름)
- **Region**: `Oregon (US West)` 또는 `Singapore` (한국과 가까움)
- **Branch**: `master`
- **Root Directory**: `backend`
- **Runtime**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT`

**환경 변수 (Environment Variables):**

| Key | Value |
|-----|-------|
| `DATABASE_URL` | `postgresql://user:password@host:5432/database` (Supabase URL) |
| `FLASK_ENV` | `production` |
| `FLASK_DEBUG` | `False` |
| `PYTHON_VERSION` | `3.11.0` |

4. **Create Web Service** 클릭

### 2-4. 배포 확인
- 배포 완료 후 URL이 생성됩니다: `https://crypto-dashboard-api.onrender.com`
- `/api/health` 엔드포인트로 테스트:
  ```
  https://crypto-dashboard-api.onrender.com/api/health
  ```

⚠️ **무료 플랜 주의사항:**
- 15분 동안 요청이 없으면 서버가 슬립 모드로 전환됩니다
- 첫 요청 시 30초~1분 정도 걸릴 수 있습니다

---

## 🌐 3단계: Frontend 배포 (Vercel)

### 3-1. Vercel 계정 생성
1. https://vercel.com 접속
2. GitHub 계정으로 로그인

### 3-2. 프로젝트 Import
1. Vercel 대시보드 → **Add New** → **Project**
2. GitHub 저장소 선택 (Py_webproject)
3. 다음 설정 입력:

**기본 설정:**
- **Framework Preset**: `Create React App`
- **Root Directory**: `frontend`
- **Build Command**: `npm run build` (자동 감지됨)
- **Output Directory**: `build` (자동 감지됨)

**환경 변수 (Environment Variables):**

| Name | Value |
|------|-------|
| `REACT_APP_API_URL` | `https://crypto-dashboard-api.onrender.com` (2단계에서 생성된 Render URL) |

4. **Deploy** 클릭

### 3-3. 배포 확인1
- 배포 완료 후 URL이 생성됩니다: `https://your-project.vercel.app`
- 브라우저에서 접속하여 확인

---

## 🔧 4단계: CORS 설정 확인

Backend의 `app.py`에서 CORS가 올바르게 설정되어 있는지 확인:

```python
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # 모든 도메인 허용 (개발용)

# 또는 특정 도메인만 허용 (프로덕션 권장)
# CORS(app, origins=["https://your-project.vercel.app"])
```

**프로덕션 환경에서는 특정 도메인만 허용하는 것이 보안상 좋습니다.**

---

## 📝 5단계: Frontend API URL 업데이트

모든 컴포넌트에서 `localhost:5000` 대신 환경 변수를 사용하도록 수정해야 합니다.

### 방법 1: config.js 사용 (권장)

`frontend/src/config.js` 파일을 생성했으므로, 각 컴포넌트에서:

```javascript
import { API_URL } from '../config';

// 기존
fetch('http://localhost:5000/api/news')

// 변경
fetch(`${API_URL}/api/news`)
```

### 수정이 필요한 파일:
1. ✅ `src/config.js` (이미 생성됨)
2. ⚠️ `src/App.js`
3. ⚠️ `src/Components/NewsSection.jsx`
4. ⚠️ `src/Components/CoinChartModal.jsx`
5. ⚠️ `src/Components/LivePriceSection.jsx`

**현재 상태:** 파일들은 아직 `localhost:5000`을 하드코딩하고 있습니다.
**다음 작업:** 제가 이 파일들을 자동으로 수정해드릴까요?

---

## 🧪 6단계: 배포 테스트

### Backend 테스트
```bash
# Health check
curl https://crypto-dashboard-api.onrender.com/api/health

# 뉴스 조회
curl https://crypto-dashboard-api.onrender.com/api/news?limit=5

# 코인 시세
curl https://crypto-dashboard-api.onrender.com/api/current-prices?page=1&limit=10
```

### Frontend 테스트
1. Vercel URL로 접속
2. 코인 데이터가 로드되는지 확인
3. 뉴스가 표시되는지 확인
4. 차트가 정상 작동하는지 확인
5. 브라우저 콘솔에서 CORS 에러가 없는지 확인

---

## ⚙️ 7단계: 자동 배포 설정 (선택사항)

### Render 자동 배포
- GitHub에 push하면 자동으로 배포됩니다 (기본 활성화)

### Vercel 자동 배포
- GitHub에 push하면 자동으로 배포됩니다 (기본 활성화)

---

## 🐛 문제 해결 (Troubleshooting)

### 1. Backend가 502 Bad Gateway 에러
- **원인**: 무료 플랜이라 슬립 모드
- **해결**: 1분 정도 기다리면 자동으로 깨어남

### 2. Frontend에서 API 호출 실패
- **원인**: CORS 에러 또는 잘못된 API URL
- **해결**:
  - Render의 환경 변수 확인
  - `app.py`에서 CORS 설정 확인
  - Vercel의 `REACT_APP_API_URL` 환경 변수 확인

### 3. 데이터베이스 연결 실패
- **원인**: Supabase URL이 잘못됨
- **해결**:
  - Supabase 대시보드에서 정확한 CONNECTION STRING 복사
  - Render 환경 변수에 정확히 붙여넣기

### 4. 뉴스가 로드되지 않음
- **원인**: 데이터베이스가 비어있음
- **해결**:
  - Backend에서 `/api/scrape-news` 엔드포인트 호출
  - 또는 Frontend에서 "뉴스 수집" 버튼 클릭

---

## 📊 배포 후 확인 사항

### ✅ 체크리스트
- [ ] Backend `/api/health` 응답 정상
- [ ] Database 연결 정상
- [ ] Frontend 로드 정상
- [ ] 코인 시세 표시
- [ ] 뉴스 표시
- [ ] 차트 정상 작동
- [ ] Fear & Greed 지수 표시
- [ ] 검색 기능 작동
- [ ] 페이지네이션 작동
- [ ] CORS 에러 없음

---

## 🔐 보안 권장사항

### 1. CORS 설정 강화
```python
# app.py에서
CORS(app, origins=[
    "https://your-project.vercel.app",
    "http://localhost:3000"  # 개발용
])
```

### 2. Rate Limiting 추가 (향후)
```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route('/api/scrape-news')
@limiter.limit("10 per hour")  # 시간당 10회 제한
def scrape_news():
    # ...
```

### 3. 환경 변수 보호
- `.env` 파일은 절대 Git에 커밋하지 않기
- `.gitignore`에 `.env` 추가되어 있는지 확인

---

## 💰 비용 안내

### 무료 플랜 (현재)
- **Render**: 750시간/월 무료
- **Vercel**: 100GB 대역폭/월 무료
- **Supabase**: 500MB 저장소 무료

### 업그레이드 필요 시점
- 월 방문자 > 10,000명
- 데이터베이스 크기 > 500MB
- 슬립 모드 없이 24/7 운영 필요

---

## 📞 다음 단계

배포 후 추가로 할 수 있는 작업:
1. 커스텀 도메인 연결 (예: crypto-dashboard.com)
2. Google Analytics 추가
3. SEO 최적화 (메타 태그, sitemap.xml)
4. PWA 변환 (모바일 앱처럼 설치 가능)
5. 성능 모니터링 (Sentry, LogRocket)

---

**작성일**: 2025-11-17
**버전**: 1.0
