"""
데이터베이스 모델 정의
SQLAlchemy를 사용하여 코인 시세 데이터를 저장합니다.
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class CoinPrice(Base):
    """코인 시세 데이터 모델"""
    __tablename__ = 'coin_prices'

    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(20), nullable=False, index=True)
    current_price = Column(Float, nullable=False)
    high_price = Column(Float)
    low_price = Column(Float)
    volume = Column(Float)
    price_change = Column(Float)
    price_change_percent = Column(Float)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    def __repr__(self):
        return f"<CoinPrice(symbol={self.symbol}, price={self.current_price}, time={self.timestamp})>"


class News(Base):
    """뉴스 데이터 모델"""
    __tablename__ = 'news'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    url = Column(String(1000), unique=True, index=True)  # 중복 방지를 위한 unique 인덱스
    source = Column(String(100), index=True)
    published_at = Column(DateTime, index=True)
    related_coins = Column(String(200))  # 관련 코인 심볼 (쉼표로 구분)
    timestamp = Column(DateTime, default=datetime.now, index=True)

    def __repr__(self):
        return f"<News(title={self.title[:30]}..., source={self.source})>"


class Database:
    """데이터베이스 연결 및 관리 클래스"""

    def __init__(self, db_path='crypto_dashboard.db'):
        """
        Args:
            db_path (str): SQLite 데이터베이스 파일 경로
        """
        self.db_path = db_path
        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def add_coin_price(self, coin_data):
        """
        코인 시세 데이터를 데이터베이스에 추가합니다.

        Args:
            coin_data (dict): 코인 시세 정보 딕셔너리
        """
        try:
            price_record = CoinPrice(
                symbol=coin_data['symbol'],
                current_price=coin_data['current_price'],
                high_price=coin_data.get('high_price'),
                low_price=coin_data.get('low_price'),
                volume=coin_data.get('volume'),
                price_change=coin_data.get('price_change'),
                price_change_percent=coin_data.get('price_change_percent')
            )
            self.session.add(price_record)
            self.session.commit()
            return True
        except Exception as e:
            print(f"데이터 저장 오류: {e}")
            self.session.rollback()
            return False

    def get_recent_prices(self, symbol, limit=100):
        """
        특정 코인의 최근 시세 데이터를 조회합니다.

        Args:
            symbol (str): 코인 심볼
            limit (int): 조회할 데이터 개수

        Returns:
            list: CoinPrice 객체 리스트
        """
        return self.session.query(CoinPrice)\
            .filter(CoinPrice.symbol == symbol)\
            .order_by(CoinPrice.timestamp.desc())\
            .limit(limit)\
            .all()

    def get_all_symbols(self):
        """
        데이터베이스에 저장된 모든 코인 심볼을 조회합니다.

        Returns:
            list: 코인 심볼 리스트
        """
        result = self.session.query(CoinPrice.symbol).distinct().all()
        return [r[0] for r in result]

    def add_news(self, news_data):
        """
        뉴스 데이터를 데이터베이스에 추가합니다.
        중복된 URL은 건너뜁니다.

        Args:
            news_data (dict): 뉴스 정보 딕셔너리

        Returns:
            bool: 성공 여부
        """
        try:
            # 중복 체크
            existing = self.session.query(News).filter(News.url == news_data.get('url')).first()
            if existing:
                return False  # 이미 존재하는 뉴스

            news_record = News(
                title=news_data['title'],
                url=news_data.get('url'),
                source=news_data.get('source'),
                published_at=news_data.get('published_at'),
                related_coins=news_data.get('related_coins')
            )
            self.session.add(news_record)
            self.session.commit()
            return True
        except Exception as e:
            print(f"뉴스 저장 오류: {e}")
            self.session.rollback()
            return False

    def get_recent_news(self, limit=20, source=None):
        """
        최근 뉴스를 조회합니다.

        Args:
            limit (int): 조회할 뉴스 개수
            source (str): 특정 소스만 조회 (선택)

        Returns:
            list: News 객체 리스트
        """
        query = self.session.query(News)

        if source:
            query = query.filter(News.source == source)

        return query.order_by(News.published_at.desc())\
            .limit(limit)\
            .all()

    def get_news_by_coin(self, coin_symbol, limit=20):
        """
        특정 코인과 관련된 뉴스를 조회합니다.

        Args:
            coin_symbol (str): 코인 심볼 (예: BTC, ETH)
            limit (int): 조회할 뉴스 개수

        Returns:
            list: News 객체 리스트
        """
        return self.session.query(News)\
            .filter(News.related_coins.like(f'%{coin_symbol}%'))\
            .order_by(News.published_at.desc())\
            .limit(limit)\
            .all()

    def close(self):
        """데이터베이스 연결을 종료합니다."""
        self.session.close()


# 테스트 코드
if __name__ == "__main__":
    print("=" * 50)
    print("데이터베이스 테스트 시작")
    print("=" * 50)

    # 데이터베이스 생성
    db = Database('test_crypto.db')

    # 테스트 데이터 추가
    test_coin_data = {
        'symbol': 'BTCUSDT',
        'current_price': 108524.68,
        'high_price': 111705.56,
        'low_price': 107473.72,
        'volume': 18435.42,
        'price_change': -2200.0,
        'price_change_percent': -2.02
    }

    print("\n[1] 코인 데이터 저장 테스트:")
    if db.add_coin_price(test_coin_data):
        print("  ✓ 데이터 저장 성공!")

    # 데이터 조회
    print("\n[2] 저장된 데이터 조회:")
    recent_prices = db.get_recent_prices('BTCUSDT', limit=5)
    for price in recent_prices:
        print(f"  {price.symbol}: ${price.current_price:,.2f} ({price.timestamp})")

    # 심볼 조회
    print("\n[3] 저장된 코인 심볼:")
    symbols = db.get_all_symbols()
    print(f"  {symbols}")

    # 뉴스 데이터 테스트
    test_news = {
        'title': 'Bitcoin reaches new all-time high',
        'url': 'https://example.com/news/1',
        'source': 'CoinDesk',
        'published_at': datetime.now()
    }

    print("\n[4] 뉴스 데이터 저장 테스트:")
    if db.add_news(test_news):
        print("  ✓ 뉴스 저장 성공!")

    # 뉴스 조회
    print("\n[5] 저장된 뉴스 조회:")
    recent_news = db.get_recent_news(limit=5)
    for news in recent_news:
        print(f"  [{news.source}] {news.title}")

    db.close()

    # 테스트 DB 파일 삭제
    if os.path.exists('test_crypto.db'):
        os.remove('test_crypto.db')
        print("\n✓ 테스트 DB 파일 삭제 완료")

    print("\n" + "=" * 50)
    print("테스트 완료!")
    print("=" * 50)
