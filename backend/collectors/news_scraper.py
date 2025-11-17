"""
뉴스 크롤러
CoinDesk, CryptoNews 등에서 암호화폐 관련 뉴스를 수집합니다.
RSS 피드와 API를 활용하여 안정적으로 뉴스를 수집합니다.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import time
import re
import feedparser
import pytz

KST = pytz.timezone("Asia/Seoul")

class NewsScraper:
    """암호화폐 뉴스 크롤러"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        
    
    
    def to_kst(self, dt):
        if dt is None:
            return datetime.now(KST)
        if dt.tzinfo is None:
            # naive → UTC 가정 → 한국 시간으로 변환
            return pytz.utc.localize(dt).astimezone(KST)
        else:
            return dt.astimezone(KST)

    def scrape_coindesk(self, limit=10):
        """
        CoinDesk RSS 피드에서 최신 뉴스를 가져옵니다.

        Args:
            limit (int): 가져올 뉴스 개수

        Returns:
            list: 뉴스 딕셔너리 리스트
        """
        news_list = []
        try:
            # CoinDesk RSS 피드 URL
            rss_url = "https://www.coindesk.com/arc/outboundfeeds/rss/"

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')

                    # 발행 시간 파싱
                    published_at = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                        
                    published_at = self.to_kst(published_at)

                    if title and url:
                        news_list.append({
                            'title': title,
                            'url': url,
                            'source': 'CoinDesk',
                            'published_at': published_at
                        })

                except Exception as e:
                    print(f"CoinDesk RSS 항목 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"CoinDesk RSS 크롤링 오류: {e}")

        return news_list

    def scrape_cryptonews(self, limit=10):
        """
        CryptoNews RSS 피드에서 최신 뉴스를 가져옵니다.

        Args:
            limit (int): 가져올 뉴스 개수

        Returns:
            list: 뉴스 딕셔너리 리스트
        """
        news_list = []
        try:
            # CryptoNews RSS 피드
            rss_url = "https://cryptonews.com/news/feed/"

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')

                    # 발행 시간 파싱
                    published_at = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                        
                    published_at = self.to_kst(published_at)

                    if title and url:
                        news_list.append({
                            'title': title,
                            'url': url,
                            'source': 'CryptoNews',
                            'published_at': published_at
                        })

                except Exception as e:
                    print(f"CryptoNews RSS 항목 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"CryptoNews RSS 크롤링 오류: {e}")

        return news_list

    def scrape_cointelegraph(self, limit=10):
        """
        CoinTelegraph RSS 피드에서 최신 뉴스를 가져옵니다.

        Args:
            limit (int): 가져올 뉴스 개수

        Returns:
            list: 뉴스 딕셔너리 리스트
        """
        news_list = []
        try:
            # CoinTelegraph RSS 피드
            rss_url = "https://cointelegraph.com/rss"

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')

                    # 발행 시간 파싱
                    published_at = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                        
                    published_at = self.to_kst(published_at)

                    if title and url and len(title) > 10:
                        news_list.append({
                            'title': title,
                            'url': url,
                            'source': 'CoinTelegraph',
                            'published_at': published_at
                        })

                except Exception as e:
                    print(f"CoinTelegraph RSS 항목 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"CoinTelegraph RSS 크롤링 오류: {e}")

        return news_list
    
    def scrape_coinness(self, limit=10):
        """
        코인니스 RSS 피드에서 최신 뉴스를 가져옵니다.

        Args:
            limit (int): 가져올 뉴스 개수

        Returns:
            list: 뉴스 딕셔너리 리스트
        """
        news_list = []
        try:
            # coinness RSS 피드 URL
            rss_url = "https://www.coinness.com/rss"

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')

                    # 발행 시간 파싱
                    published_at = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                    else:
                        published_at = datetime.utcnow()
                        
                    published_at = self.to_kst(published_at)

                    if title and url:
                        news_list.append({
                            'title': title,
                            'url': url,
                            'source': 'Coinness',
                            'published_at': published_at
                        })

                except Exception as e:
                    print(f"CoinDesk RSS 항목 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"Coinness RSS 크롤링 오류: {e}")

        return news_list
    
    
    def scrape_tokenpost(self, limit=10):
        """
        토큰포스트 RSS 피드에서 최신 뉴스를 가져옵니다.

        Args:
            limit (int): 가져올 뉴스 개수

        Returns:
            list: 뉴스 딕셔너리 리스트
        """
        news_list = []
        try:
            # tokenpost RSS 피드 URL
            rss_url = "https://www.tokenpost.kr/rss"

            feed = feedparser.parse(rss_url)

            for entry in feed.entries[:limit]:
                try:
                    title = entry.get('title', '').strip()
                    url = entry.get('link', '')

                    # 발행 시간 파싱
                    published_at = datetime.now()
                    if hasattr(entry, 'published_parsed') and entry.published_parsed:
                        published_at = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                        published_at = datetime(*entry.updated_parsed[:6])
                    else:
                        published_at = datetime.utcnow()
                        
                    published_at = self.to_kst(published_at)

                    if title and url:
                        news_list.append({
                            'title': title,
                            'url': url,
                            'source': 'TokenPost',
                            'published_at': published_at
                        })

                except Exception as e:
                    print(f"TokenPost RSS 항목 파싱 오류: {e}")
                    continue

        except Exception as e:
            print(f"CoinDesk RSS 크롤링 오류: {e}")

        return news_list
    

    def scrape_all_sources(self, limit_per_source=10):
        """
        모든 소스에서 뉴스를 크롤링합니다.

        Args:
            limit_per_source (int): 각 소스별 가져올 뉴스 개수

        Returns:
            list: 모든 뉴스 딕셔너리 리스트
        """
        all_news = []

        print("📰 Coinness(한국) 크롤링 시작...")
        Coinness_news = self.scrape_coinness(limit=limit_per_source)
        all_news.extend(Coinness_news)
        print(f"   ✓ Coinness: {len(Coinness_news)}개 수집")
        
        print("📰 TokenPost(한국) 크롤링 시작...")
        TokenPost_news = self.scrape_tokenpost(limit=limit_per_source)
        all_news.extend(TokenPost_news)
        print(f"   ✓ TokenPost: {len(TokenPost_news)}개 수집")

        print("📰 CoinDesk 크롤링 시작...")
        coindesk_news = self.scrape_coindesk(limit=limit_per_source)
        all_news.extend(coindesk_news)
        print(f"   ✓ CoinDesk: {len(coindesk_news)}개 수집")
        time.sleep(1)  # 요청 간격 조절

        print("📰 CryptoNews 크롤링 시작...")
        cryptonews_news = self.scrape_cryptonews(limit=limit_per_source)
        all_news.extend(cryptonews_news)
        print(f"   ✓ CryptoNews: {len(cryptonews_news)}개 수집")
        time.sleep(1)

        print("📰 CoinTelegraph 크롤링 시작...")
        cointelegraph_news = self.scrape_cointelegraph(limit=limit_per_source)
        all_news.extend(cointelegraph_news)
        print(f"   ✓ CoinTelegraph: {len(cointelegraph_news)}개 수집")
        

        # 중복 제거 (URL 기준)
        seen_urls = set()
        unique_news = []
        for news in all_news:
            if news['url'] not in seen_urls:
                seen_urls.add(news['url'])
                unique_news.append(news)

        # 시간 순으로 정렬 (최신순)
        unique_news.sort(key=lambda x: x['published_at'], reverse=True)

        print(f"\n📊 총 {len(unique_news)}개의 고유 뉴스 수집 완료")
        return unique_news

    def extract_coin_mentions(self, title):
        """
        뉴스 제목에서 언급된 코인을 추출합니다.

        Args:
            title (str): 뉴스 제목

        Returns:
            list: 언급된 코인 심볼 리스트
        """
        # 주요 코인 심볼 목록
        major_coins = {
            'BTC': ['bitcoin', 'btc'],
            'ETH': ['ethereum', 'eth', 'ether'],
            'BNB': ['binance', 'bnb'],
            'XRP': ['ripple', 'xrp'],
            'ADA': ['cardano', 'ada'],
            'SOL': ['solana', 'sol'],
            'DOGE': ['dogecoin', 'doge'],
            'MATIC': ['polygon', 'matic'],
            'DOT': ['polkadot', 'dot'],
            'AVAX': ['avalanche', 'avax']
        }

        mentioned_coins = []
        title_lower = title.lower()

        for symbol, keywords in major_coins.items():
            for keyword in keywords:
                if keyword in title_lower:
                    mentioned_coins.append(symbol)
                    break

        return mentioned_coins


# 테스트 코드
if __name__ == "__main__":
    print("=" * 60)
    print("뉴스 크롤러 테스트 시작")
    print("=" * 60)

    scraper = NewsScraper()

    # 모든 소스에서 뉴스 수집
    news_list = scraper.scrape_all_sources(limit_per_source=5)

    print("\n" + "=" * 60)
    print("수집된 뉴스:")
    print("=" * 60)

    for i, news in enumerate(news_list[:10], 1):
        print(f"\n[{i}] {news['source']}")
        print(f"    제목: {news['title']}")
        print(f"    URL: {news['url'][:60]}...")
        print(f"    시간: {news['published_at']}")

        # 코인 언급 추출
        coins = scraper.extract_coin_mentions(news['title'])
        if coins:
            print(f"    언급된 코인: {', '.join(coins)}")

    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
