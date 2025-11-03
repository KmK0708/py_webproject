"""
Flask REST API 서버 (React Frontend용)
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
from collectors.binance_api import BinanceCollector
from database.models import Database
from datetime import datetime
import requests

app = Flask(__name__)
CORS(app)  # React와 통신을 위한 CORS 설정

# 전역 변수
db = Database('crypto_dashboard.db')
collector = BinanceCollector()

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
