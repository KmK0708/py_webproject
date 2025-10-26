"""
Binance API를 통해 코인 시세 데이터를 수집하는 모듈
"""
import requests
import time
from datetime import datetime


class BinanceCollector:
    """Binance API에서 코인 데이터를 수집하는 클래스"""

    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"

    def get_current_price(self, symbol="BTCUSDT"):
        """
        특정 코인의 현재 가격을 가져옵니다.

        Args:
            symbol (str): 코인 심볼 (예: BTCUSDT, ETHUSDT)

        Returns:
            dict: 가격 정보 딕셔너리
        """
        try:
            url = f"{self.base_url}/ticker/price"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["price"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None

    def get_24h_ticker(self, symbol="BTCUSDT"):
        """
        24시간 시세 변동 정보를 가져옵니다.

        Args:
            symbol (str): 코인 심볼

        Returns:
            dict: 24시간 시세 정보
        """
        try:
            url = f"{self.base_url}/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            return {
                "symbol": data["symbol"],
                "current_price": float(data["lastPrice"]),
                "high_price": float(data["highPrice"]),
                "low_price": float(data["lowPrice"]),
                "volume": float(data["volume"]),
                "price_change": float(data["priceChange"]),
                "price_change_percent": float(data["priceChangePercent"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None

    def get_multiple_tickers(self, symbols=["BTCUSDT", "ETHUSDT", "BNBUSDT"]):
        """
        여러 코인의 24시간 시세 정보를 가져옵니다.

        Args:
            symbols (list): 코인 심볼 리스트

        Returns:
            list: 각 코인의 시세 정보 리스트
        """
        result = []
        for symbol in symbols:
            data = self.get_24h_ticker(symbol)
            if data:
                result.append(data)
            time.sleep(0.1)  # API 요청 제한 방지
        return result


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("Binance API 테스트 시작")
    print("=" * 50)

    collector = BinanceCollector()

    # 1. BTC 현재 가격 조회
    print("\n[1] BTC 현재 가격:")
    btc_price = collector.get_current_price("BTCUSDT")
    if btc_price:
        print(f"  Symbol: {btc_price['symbol']}")
        print(f"  Price: ${btc_price['price']:,.2f}")
        print(f"  Time: {btc_price['timestamp']}")

    # 2. BTC 24시간 데이터 조회
    print("\n[2] BTC 24시간 데이터:")
    btc_24h = collector.get_24h_ticker("BTCUSDT")
    if btc_24h:
        print(f"  Symbol: {btc_24h['symbol']}")
        print(f"  Current Price: ${btc_24h['current_price']:,.2f}")
        print(f"  24h High: ${btc_24h['high_price']:,.2f}")
        print(f"  24h Low: ${btc_24h['low_price']:,.2f}")
        print(f"  24h Volume: {btc_24h['volume']:,.2f}")
        print(f"  24h Change: {btc_24h['price_change_percent']:.2f}%")

    # 3. 여러 코인 데이터 조회
    print("\n[3] 주요 코인 데이터:")
    coins = collector.get_multiple_tickers(["BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT"])
    for coin in coins:
        print(f"\n  {coin['symbol']}:")
        print(f"    Price: ${coin['current_price']:,.2f}")
        print(f"    24h Change: {coin['price_change_percent']:.2f}%")
        print(f"    Volume: {coin['volume']:,.2f}")

    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)
