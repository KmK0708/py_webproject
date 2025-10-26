"""
Flask 웹 서버 메인 파일
코인 시세 대시보드 웹 애플리케이션
"""
from flask import Flask, render_template, jsonify
from data_collector.binance_api import BinanceCollector
from database.models import Database
from datetime import datetime
import threading
import time

app = Flask(__name__)

# 전역 변수
db = Database('crypto_dashboard.db')
collector = BinanceCollector()

# 모니터링할 코인 리스트
COIN_SYMBOLS = ["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT"]


@app.route('/')
def index():
    """메인 대시보드 페이지"""
    return render_template('dashboard.html')


@app.route('/api/current-prices')
def get_current_prices():
    """
    현재 코인 시세를 반환하는 API
    Returns:
        JSON: 코인 시세 리스트
    """
    try:
        coins = collector.get_multiple_tickers(COIN_SYMBOLS)
        return jsonify({
            'success': True,
            'data': coins,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


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


def background_data_collector():
    """
    백그라운드에서 주기적으로 데이터를 수집하는 함수
    (나중에 APScheduler로 대체 가능)
    """
    while True:
        try:
            print(f"[{datetime.now()}] 데이터 수집 시작...")
            coins = collector.get_multiple_tickers(COIN_SYMBOLS)

            for coin in coins:
                db.add_coin_price(coin)
                print(f"  - {coin['symbol']}: ${coin['current_price']:,.2f}")

            print("데이터 수집 완료!\n")
        except Exception as e:
            print(f"데이터 수집 오류: {e}")

        # 5분마다 데이터 수집
        time.sleep(300)


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
    print(" 코인 시세 대시보드 서버 시작 ")
    print("=" * 60)
    print(f"모니터링 코인: {', '.join(COIN_SYMBOLS)}")
    print("서버 주소: http://127.0.0.1:5000")
    print("=" * 60)

    # 백그라운드 데이터 수집 시작 (선택사항)
    # collector_thread = threading.Thread(target=background_data_collector, daemon=True)
    # collector_thread.start()

    # Flask 서버 실행
    app.run(debug=True, host='0.0.0.0', port=5000)
