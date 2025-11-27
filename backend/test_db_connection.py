"""
데이터베이스 연결 테스트 스크립트

PostgreSQL 또는 SQLite 연결을 테스트하고 기본 정보를 출력합니다.
"""
import sys
import os

# 현재 디렉토리를 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.models import Database, CoinPrice, News
from config import Config


def test_connection():
    """데이터베이스 연결을 테스트합니다."""

    print("\n" + "=" * 70)
    print("데이터베이스 연결 테스트")
    print("=" * 70)

    # 현재 설정 출력
    Config.print_config()

    try:
        # 데이터베이스 연결
        print("\n[1] Database connection attempt...")
        db = Database()
        print("[OK] Connection successful!")

        # 코인 가격 데이터 확인
        print("\n[2] 코인 가격 데이터 확인...")
        price_count = db.session.query(CoinPrice).count()
        print(f"  총 레코드 수: {price_count:,}개")

        if price_count > 0:
            # 심볼 목록
            symbols = db.get_all_symbols()
            print(f"  코인 종류: {len(symbols)}개")
            print(f"  예시 심볼: {', '.join(symbols[:5])}")

            # 최근 데이터 조회
            recent_prices = db.session.query(CoinPrice)\
                .order_by(CoinPrice.timestamp.desc())\
                .limit(3)\
                .all()

            print("\n  최근 3개 데이터:")
            for price in recent_prices:
                print(f"    {price.symbol}: ${price.current_price:,.2f} ({price.timestamp})")
        else:
            print("  [WARNING] No data found.")

        # 뉴스 데이터 확인
        print("\n[3] 뉴스 데이터 확인...")
        news_count = db.session.query(News).count()
        print(f"  총 레코드 수: {news_count:,}개")

        if news_count > 0:
            # 최근 뉴스 조회
            recent_news = db.session.query(News)\
                .order_by(News.published_at.desc())\
                .limit(3)\
                .all()

            print("\n  최근 3개 뉴스:")
            for news in recent_news:
                print(f"    [{news.source}] {news.title[:50]}...")
        else:
            print("  [WARNING] No news data found.")

        # 테이블 구조 확인
        print("\n[4] Table structure check...")
        print("  [OK] coin_prices table exists")
        print("  [OK] news table exists")

        # 연결 종료
        db.close()

        # 최종 결과
        print("\n" + "=" * 70)
        print("[SUCCESS] All tests passed!")
        print("=" * 70)
        print("\nNext steps:")
        print("  1. Run 'python app.py' to start Flask server")
        print("  2. Check data on frontend")
        print("=" * 70 + "\n")

        return True

    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        print("\n해결 방법:")
        print("  1. PostgreSQL 서비스가 실행 중인지 확인")
        print("  2. .env 파일의 DATABASE_URL이 올바른지 확인")
        print("  3. 데이터베이스가 생성되어 있는지 확인")
        print("  4. 비밀번호가 정확한지 확인")
        print("\n자세한 내용은 POSTGRESQL_SETUP.md를 참고하세요.")
        print("=" * 70 + "\n")

        import traceback
        traceback.print_exc()

        return False


if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1)
