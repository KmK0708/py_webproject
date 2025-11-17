"""
Flask REST API 서버 (React Frontend용)
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from collectors.binance_api import BinanceCollector
from collectors.news_scraper import NewsScraper
from database.models import Database
from datetime import datetime, timedelta
import requests
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

app = Flask(__name__)
CORS(app)  # React와 통신을 위한 CORS 설정

# 전역 변수
db = Database('crypto_dashboard.db')
collector = BinanceCollector()
news_scraper = NewsScraper()

# 캔들스틱 데이터 캐시 (메모리)
# 구조: {f"{symbol}_{interval}": {"data": [...], "timestamp": datetime}}
klines_cache = {}
CACHE_DURATION = timedelta(minutes=1)  # 1분 동안 캐시 유지

# 모니터링할 코인 리스트
COIN_SYMBOLS = collector.get_all_symbols()
@app.route('/api/health')
def health_check():
    """API 서버 상태 확인"""
    return jsonify({
        'success': True,
        'message': 'Backend API is running',
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

@app.route('/api/fear-greed')
def get_fear_greed():
    # Alternative.me API 예시
    url = 'https://api.alternative.me/fng/?limit=30'  # 최근 30일치
    res = requests.get(url)
    data = res.json()
    return jsonify({
        "success": True,
        "data": data.get("data", [])
    })

@app.route('/api/current-prices')
def get_current_prices():
    """
    현재 코인 시세를 반환하는 API
    Returns:
        JSON: 코인 시세 리스트
        /api/current-prices?page=1&limit=50
    """
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 50))

        all_coins = collector.get_multiple_tickers(COIN_SYMBOLS)
        total = len(all_coins)

        # 페이지 슬라이싱
        start = (page - 1) * limit
        end = start + limit
        sliced = all_coins[start:end]

        return jsonify({
            'success': True,
            'data': sliced,
            'page': page,
            'limit': limit,
            'total': total,
            'total_pages': (total + limit - 1) // limit,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history/<symbol>')
def get_price_history(symbol):
    """
    특정 코인의 과거 시세 데이터를 반환하는 API

    Args:
        symbol (str): 코인 심볼

    Returns:
        JSON: 시세 히스토리
    """
    try:
        prices = db.get_recent_prices(symbol.upper(), limit=100)

        # 시간순으로 정렬 (오래된 것부터)
        prices.reverse()

        history = [{
            'timestamp': price.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            'price': price.current_price,
            'volume': price.volume,
            'change_percent': price.price_change_percent
        } for price in prices]

        return jsonify({
            'success': True,
            'symbol': symbol.upper(),
            'data': history
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/save-current-data')
def save_current_data():
    """
    현재 코인 데이터를 데이터베이스에 저장하는 API
    (테스트 및 수동 저장용)
    """
    try:
        coins = collector.get_multiple_tickers(COIN_SYMBOLS)
        saved_count = 0

        for coin in coins:
            if db.add_coin_price(coin):
                saved_count += 1

        return jsonify({
            'success': True,
            'message': f'{saved_count}개 코인 데이터 저장 완료',
            'saved_count': saved_count
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stats')
def get_stats():
    """전체 통계 정보를 반환하는 API"""
    try:
        symbols = db.get_all_symbols()
        total_records = sum([len(db.get_recent_prices(s, limit=1000)) for s in symbols])

        return jsonify({
            'success': True,
            'data': {
                'total_symbols': len(symbols),
                'symbols': symbols,
                'total_records': total_records
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/klines/<symbol>')
def get_klines(symbol):
    """
    특정 코인의 캔들스틱 데이터를 반환하는 API (차트용)
    캐싱을 통해 Binance API 요청 횟수를 최소화

    Args:
        symbol (str): 코인 심볼 (예: BTCUSDT)

    Query params:
        interval (str): 시간 간격 (1m, 5m, 15m, 1h, 4h, 1d) - 기본값: 1h
        limit (int): 캔들 개수 - 기본값: 24

    Returns:
        JSON: 캔들스틱 데이터
    """
    try:
        interval = request.args.get('interval', '1h')
        limit = int(request.args.get('limit', 24))

        # 심볼이 USDT로 끝나지 않으면 자동으로 추가
        if not symbol.upper().endswith('USDT'):
            symbol = f"{symbol.upper()}USDT"
        else:
            symbol = symbol.upper()

        # 캐시 키 생성
        cache_key = f"{symbol}_{interval}_{limit}"
        current_time = datetime.now()

        # 캐시 확인
        if cache_key in klines_cache:
            cached_item = klines_cache[cache_key]
            cache_age = current_time - cached_item['timestamp']

            # 캐시가 유효한 경우
            if cache_age < CACHE_DURATION:
                print(f"✅ 캐시 사용: {cache_key} (나이: {cache_age.seconds}초)")
                return jsonify({
                    'success': True,
                    'symbol': symbol,
                    'interval': interval,
                    'data': cached_item['data'],
                    'cached': True,
                    'cache_age_seconds': cache_age.seconds
                })

        # 캐시 미스 또는 만료 - Binance API 호출
        print(f"🔄 Binance API 호출: {cache_key}")
        klines = collector.get_klines(symbol, interval, limit)

        # 캐시에 저장
        klines_cache[cache_key] = {
            'data': klines,
            'timestamp': current_time
        }

        # 오래된 캐시 정리 (메모리 절약)
        _cleanup_old_cache()

        return jsonify({
            'success': True,
            'symbol': symbol,
            'interval': interval,
            'data': klines,
            'cached': False
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


def _cleanup_old_cache():
    """오래된 캐시 항목 삭제 (메모리 관리)"""
    current_time = datetime.now()
    keys_to_delete = []

    for key, value in klines_cache.items():
        if current_time - value['timestamp'] > CACHE_DURATION * 2:
            keys_to_delete.append(key)

    for key in keys_to_delete:
        del klines_cache[key]

    if keys_to_delete:
        print(f"🗑️ 오래된 캐시 {len(keys_to_delete)}개 삭제")


@app.route('/api/news')
def get_news():
    """
    최근 뉴스를 반환하는 API

    Query params:
        limit (int): 조회할 뉴스 개수 - 기본값: 20
        source (str): 특정 소스만 조회 (선택) - CoinDesk, CryptoNews, CoinTelegraph

    Returns:
        JSON: 뉴스 리스트
    """
    try:
        limit = int(request.args.get('limit', 20))
        source = request.args.get('source', None)

        # 데이터베이스에서 뉴스 조회
        news_list = db.get_recent_news(limit=limit, source=source)

        # 딕셔너리로 변환
        news_data = [{
            'id': news.id,
            'title': news.title,
            'url': news.url,
            'source': news.source,
            'published_at': news.published_at.isoformat() if news.published_at else None,
            'related_coins': news.related_coins.split(',') if news.related_coins else [],
            'timestamp': news.timestamp.isoformat()
        } for news in news_list]

        return jsonify({
            'success': True,
            'data': news_data,
            'count': len(news_data),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/news/<coin_symbol>')
def get_news_by_coin(coin_symbol):
    """
    특정 코인과 관련된 뉴스를 반환하는 API

    Args:
        coin_symbol (str): 코인 심볼 (예: BTC, ETH)

    Query params:
        limit (int): 조회할 뉴스 개수 - 기본값: 20

    Returns:
        JSON: 뉴스 리스트
    """
    try:
        limit = int(request.args.get('limit', 20))

        # 데이터베이스에서 코인별 뉴스 조회
        news_list = db.get_news_by_coin(coin_symbol.upper(), limit=limit)

        # 딕셔너리로 변환
        news_data = [{
            'id': news.id,
            'title': news.title,
            'url': news.url,
            'source': news.source,
            'published_at': news.published_at.isoformat() if news.published_at else None,
            'related_coins': news.related_coins.split(',') if news.related_coins else [],
            'timestamp': news.timestamp.isoformat()
        } for news in news_list]

        return jsonify({
            'success': True,
            'coin': coin_symbol.upper(),
            'data': news_data,
            'count': len(news_data),
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/scrape-news')
def scrape_news():
    """
    뉴스를 크롤링하고 데이터베이스에 저장하는 API
    (테스트 및 수동 수집용)

    Query params:
        limit (int): 각 소스별 수집할 뉴스 개수 - 기본값: 10

    Returns:
        JSON: 수집 결과
    """
    try:
        limit_per_source = int(request.args.get('limit', 10))

        # 뉴스 크롤링
        news_list = news_scraper.scrape_all_sources(limit_per_source=limit_per_source)

        saved_count = 0
        skipped_count = 0

        # 데이터베이스에 저장
        for news in news_list:
            # 관련 코인 추출
            related_coins = news_scraper.extract_coin_mentions(news['title'])
            news['related_coins'] = ','.join(related_coins) if related_coins else None

            # 🔥 published_at이 None이면 현재시간으로 채움
            published_at = news.get('published_at')
            if not published_at:
                published_at = datetime.now()
            news['published_at'] = published_at

            if db.add_news(news):
                saved_count += 1
            else:
                skipped_count += 1  # 이미 존재하는 뉴스

        return jsonify({
            'success': True,
            'message': f'{saved_count}개 뉴스 저장 완료 ({skipped_count}개 중복 제외)',
            'saved_count': saved_count,
            'skipped_count': skipped_count,
            'total_scraped': len(news_list)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# ============================================
# 백그라운드 자동 작업 (APScheduler)
# ============================================

def auto_collect_news():
    """
    백그라운드에서 자동으로 뉴스를 수집하는 함수
    """
    try:
        print("\n" + "=" * 60)
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 자동 뉴스 수집 시작")
        print("=" * 60)

        news_list = news_scraper.scrape_all_sources(limit_per_source=10)
        saved_count = 0
        skipped_count = 0

        for news in news_list:
            related_coins = news_scraper.extract_coin_mentions(news['title'])
            news['related_coins'] = ','.join(related_coins) if related_coins else None

            if db.add_news(news):
                saved_count += 1
            else:
                skipped_count += 1

        print(f"✅ 뉴스 수집 완료: {saved_count}개 저장, {skipped_count}개 중복 제외")
        print("=" * 60 + "\n")

    except Exception as e:
        print(f"❌ 자동 뉴스 수집 오류: {e}")


def auto_save_prices():
    """
    백그라운드에서 자동으로 코인 가격을 저장하는 함수
    """
    try:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 자동 가격 저장 시작")

        coins = collector.get_multiple_tickers(COIN_SYMBOLS)
        saved_count = 0

        for coin in coins:
            if db.add_coin_price(coin):
                saved_count += 1

        print(f"✅ 가격 데이터 저장 완료: {saved_count}개 코인")

    except Exception as e:
        print(f"❌ 자동 가격 저장 오류: {e}")


# 스케줄러 설정
scheduler = BackgroundScheduler()

# 뉴스 수집: 30분마다 실행
scheduler.add_job(
    func=auto_collect_news,
    trigger="interval",
    minutes=30,
    id='news_collector',
    name='뉴스 자동 수집',
    replace_existing=True
)

# 가격 저장: 10분마다 실행
scheduler.add_job(
    func=auto_save_prices,
    trigger="interval",
    minutes=10,
    id='price_saver',
    name='가격 자동 저장',
    replace_existing=True
)

# 서버 시작 시 스케줄러 시작
scheduler.start()

# 서버 종료 시 스케줄러 정리
atexit.register(lambda: scheduler.shutdown())


if __name__ == '__main__':
    print("=" * 60)
    print(" Flask REST API 서버 시작 (React Frontend용) ")
    print("=" * 60)
    print(f"모니터링 코인: {len(COIN_SYMBOLS)}개")
    print("API 주소: http://localhost:5000")
    print("CORS: 활성화 (React 통신 가능)")
    print("\n백그라운드 작업:")
    print("  ✓ 뉴스 자동 수집: 30분마다")
    print("  ✓ 가격 자동 저장: 10분마다")
    print("=" * 60)

    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000, use_reloader=False)
