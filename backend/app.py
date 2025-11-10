"""
Flask REST API 서버 (React Frontend용)
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from collectors.binance_api import BinanceCollector
from database.models import Database
from datetime import datetime, timedelta
import requests

app = Flask(__name__)
CORS(app)  # React와 통신을 위한 CORS 설정

# 전역 변수
db = Database('crypto_dashboard.db')
collector = BinanceCollector()

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


if __name__ == '__main__':
    print("=" * 60)
    print(" Flask REST API 서버 시작 (React Frontend용) ")
    print("=" * 60)
    print(f"모니터링 코인: {', '.join(COIN_SYMBOLS)}")
    print("API 주소: http://localhost:5000")
    print("CORS: 활성화 (React 통신 가능)")
    print("=" * 60)

    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
