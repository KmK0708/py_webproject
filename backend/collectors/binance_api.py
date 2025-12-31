"""
Binance API를 통해 코인 시세 데이터를 수집하는 모듈
"""
import os
import requests
import time
from datetime import datetime


class BinanceCollector:
    """Binance API에서 코인 데이터를 수집하는 클래스"""

    def __init__(self):
        env_urls = os.getenv("BINANCE_BASE_URLS")
        default_urls = [
            "https://api.binance.com/api/v3",
            "https://data-api.binance.vision/api/v3",
            "https://api1.binance.com/api/v3"
        ]
        if env_urls:
            base_urls = [u.strip().rstrip("/") for u in env_urls.split(",") if u.strip()]
        else:
            base_urls = default_urls

        self.base_urls = base_urls
        self.base_url = self.base_urls[0]
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)

    def _request(self, path, params=None):
        """Binance API request with base URL fallback."""
        last_exc = None
        for base_url in self.base_urls:
            url = f"{base_url}{path}"
            try:
                res = self.session.get(url, params=params, timeout=10)
                if res.status_code == 451:
                    raise requests.exceptions.HTTPError(
                        "451 Client Error: Unavailable For Legal Reasons",
                        response=res
                    )
                res.raise_for_status()
                self.base_url = base_url
                return res
            except requests.exceptions.RequestException as e:
                last_exc = e
                continue

        if last_exc:
            raise last_exc

        raise requests.exceptions.RequestException("Binance API ?? ??")

    # ----------------------------
    # ✅ 모든 거래 가능 코인 목록 가져오기
    # ----------------------------
    def get_all_symbols(self, quote="USDT"):
        """
        바이낸스에서 모든 거래 가능한 심볼 목록을 가져옴.

        Args:
            quote (str): 기준 통화 (예: USDT, BTC, BUSD)

        Returns:
            list: ["BTCUSDT", "ETHUSDT", ...]
        """
        try:
            res = self._request("/exchangeInfo")
            data = res.json()

            symbols = [
                s["symbol"] for s in data["symbols"]
                if s["status"] == "TRADING" and s["quoteAsset"] == quote
            ]
            return symbols
        except Exception as e:
            print(f"⚠️ 심볼 목록 가져오기 오류: {e}")
            return []

    # ----------------------------
    # ✅ 단일 코인 가격
    # ----------------------------
    def get_current_price(self, symbol="BTCUSDT"):
        try:
            params = {"symbol": symbol}
            res = self._request("/ticker/price", params=params)
            data = res.json()
            return {
                "symbol": data["symbol"],
                "price": float(data["price"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return None

    # ----------------------------
    # ✅ 단일 코인 24시간 데이터
    # ----------------------------
    def get_24h_ticker(self, symbol="BTCUSDT"):
        try:
            params = {"symbol": symbol}
            res = self._request("/ticker/24hr", params=params)
            data = res.json()
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

    # ----------------------------
    # ✅ 캔들스틱 데이터 가져오기 (차트용)
    # ----------------------------
    def get_klines(self, symbol="BTCUSDT", interval="1h", limit=24):
        """
        캔들스틱 데이터를 가져옴 (차트 그리기용).

        Args:
            symbol (str): 코인 심볼 (예: "BTCUSDT")
            interval (str): 시간 간격 (1m, 5m, 15m, 1h, 4h, 1d 등)
            limit (int): 가져올 캔들 개수 (기본 24개 = 24시간)

        Returns:
            list: 캔들스틱 데이터 리스트
        """
        try:
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            }
            res = self._request("/klines", params=params)
            data = res.json()

            # 캔들스틱 데이터 포맷팅
            klines = []
            for k in data:
                klines.append({
                    "time": k[0],  # 타임스탬프
                    "open": float(k[1]), # 시가
                    "high": float(k[2]), # 고가
                    "low": float(k[3]), # 저가
                    "close": float(k[4]), # 종가
                    "volume": float(k[5]) # 거래량
                })

            return klines
        except requests.exceptions.RequestException as e:
            print(f"캔들스틱 API 요청 오류: {e}")
            return []

    # ----------------------------
    # ✅ 여러 코인 일괄 조회 (빠름)
    # ----------------------------
    def get_multiple_tickers(self, symbols=None):
        """
        여러 코인의 시세 정보를 가져옴.
        symbols가 없으면 모든 USDT 코인을 자동으로 가져옴.
        """
        try:
            res = self._request("/ticker/24hr")
            data = res.json()

            if symbols is None:
                # USDT 코인 전체 자동 필터링
                filtered = [d for d in data if d["symbol"].endswith("USDT")]
            else:
                filtered = [d for d in data if d["symbol"] in symbols]

            result = [{
                "symbol": d["symbol"],
                "current_price": float(d["lastPrice"]),
                "volume": float(d["volume"]),
                "price_change_percent": float(d["priceChangePercent"]),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            } for d in filtered]

            return result
        except requests.exceptions.RequestException as e:
            print(f"API 요청 오류: {e}")
            return []


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("Binance API 테스트 시작")
    print("=" * 50)

    collector = BinanceCollector()

    print("\n=== 전체 코인 24h 데이터 가져오기 ===")
    tickers = collector.get_multiple_tickers()
    print(f"총 {len(tickers)}개 시세 데이터 수집 완료")
    print(tickers[:3])

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
